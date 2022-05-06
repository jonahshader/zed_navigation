from typing import Callable, List

from bezier import Bezier
from cost_field import CostField


def make_loss(field: CostField, samples=100) -> Callable[[Bezier], float]:
    def loss(bezier: Bezier) -> float:
        dist = bezier.get_distance()
        avgcost = 0.0
        for n in range(samples):
            avgcost += field.get_cost(bezier.get(dist/n))
        return avgcost / samples
    return loss

def optimize_bezier_inner_points(bezier: Bezier, loss: Callable[[Bezier], float], popsize=10, gensize=10, init_mutation=3.0, mutation_scalar=0.5) -> Bezier:
    pop: List[Bezier] = [bezier.copy() for _ in range(popsize)]

    best = pop[0]
    for g in range(gensize):
        mutate_amount = init_mutation * mutation_scalar**g
        for b in pop:
            b.mutate_point(mutate_amount, 1)
            b.mutate_point(mutate_amount, 2)
        best = _get_best_from_population(pop, loss)
        for b in pop:
            if b != best:
                b.copyfrom(best)
    return best

def optimize_bezier_inner_points_on_field(bezier: Bezier, field: CostField, samples=100, **kwargs) -> Bezier:
    loss = make_loss(field, samples)
    return optimize_bezier_inner_points(bezier, loss, **kwargs)


def _get_best_from_population(pop: List[Bezier], loss: Callable[[Bezier], float]) -> Bezier:
    losses: List[float] = [loss(b) for b in pop]
    return pop[losses.index(min(losses))]