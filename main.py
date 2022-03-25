import math

import cv2
import arcade
import pyzed.sl as sl
import numpy as np

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 1024
SCREEN_TITLE = "ZED pos tester"

MAX_STORED_POINTS = 2000

PIXELS_PER_METER = 100  # 500


class ZedPosRenderer(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.WHITE)
        self.time = 0
        self.stored_transformed_points = []


        # create a camera object
        self.zed = sl.Camera()

        # create an InitParameters object and set configuration parameters
        self.init_params = sl.InitParameters()
        self.init_params.camera_resolution = sl.RESOLUTION.HD1080
        self.init_params.depth_mode = sl.DEPTH_MODE.QUALITY
        self.init_params.camera_fps = 30
        # use a right-handed Y-up coordinate system
        self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP
        self.init_params.coordinate_units = sl.UNIT.METER

        # open the camera
        err = self.zed.open(self.init_params)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        # enable positional tracking with default parameters
        self.py_transform = sl.Transform()
        self.tracking_parameters = sl.PositionalTrackingParameters(_init_pos=self.py_transform)
        err = self.zed.enable_positional_tracking(self.tracking_parameters)
        if err != sl.ERROR_CODE.SUCCESS:
            exit(1)

        self.zed_pose = sl.Pose()
        self.zed_sensors = sl.SensorsData()
        self.runtime_parameters = sl.RuntimeParameters()

        self.image_size = self.zed.get_camera_information().camera_resolution
        # self.image_size.width = self.image_size.width / 2
        # self.image_size.height = self.image_size.height / 2
        self.image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.depth_image_zed = sl.Mat(self.image_size.width, self.image_size.height, sl.MAT_TYPE.U8_C4)
        self.point_cloud = sl.Mat()

    def setup(self):
        self.time = 0.0
        pass

    def on_draw(self):
        tx = 0
        ty = 0
        tz = 0
        pitch = 0
        yaw = 0
        roll = 0
        points = []
        if self.zed.grab(self.runtime_parameters) == sl.ERROR_CODE.SUCCESS:
            self.zed.retrieve_image(self.image_zed, sl.VIEW.LEFT, sl.MEM.CPU, self.image_size)
            self.zed.retrieve_image(self.depth_image_zed, sl.VIEW.DEPTH, sl.MEM.CPU, self.image_size)
            self.zed.retrieve_measure(self.point_cloud, sl.MEASURE.XYZRGBA, sl.MEM.CPU, self.image_size)

            image_ocv = self.image_zed.get_data()
            depth_image_ocv = self.depth_image_zed.get_data()

            gray = cv2.cvtColor(image_ocv, cv2.COLOR_BGR2GRAY)

            for i in range(200):
                x_pos = (i / 199) * self.image_size.width
                point = self.point_cloud.get_value(x_pos, self.image_size.height / 2)
                points.append(point)

            # point = self.point_cloud.get_value(self.image_size.width/2, self.image_size.height/2)
            # distance = math.sqrt(point[1][0]*point[1][0] + point[1][1]*point[1][1] + point[1][2]*point[1][2])

            self.zed.get_position(self.zed_pose, sl.REFERENCE_FRAME.WORLD)
            self.zed.get_sensors_data(self.zed_sensors, sl.TIME_REFERENCE.IMAGE)
            zed_imu = self.zed_sensors.get_imu_data()

            py_translation = sl.Translation()
            tx = self.zed_pose.get_translation(py_translation).get()[0]
            ty = self.zed_pose.get_translation(py_translation).get()[1]
            tz = self.zed_pose.get_translation(py_translation).get()[2]
            pitch = self.zed_pose.get_rotation_vector()[0]
            yaw = self.zed_pose.get_rotation_vector()[1]
            roll = self.zed_pose.get_rotation_vector()[2]
            print("Translation: Tx: {0}, Ty: {1}, Tz {2}\n".format(tx, ty, tz))
            print(f'Rotation: Pitch: {pitch}, Roll: {roll}, Yaw: {yaw}')

        arcade.start_render()
        # arcade.draw_point(SCREEN_WIDTH / 2 + tx * PIXELS_PER_METER, SCREEN_HEIGHT / 2 - tz * PIXELS_PER_METER,
        #                   arcade.color.BLACK, pow(2, ty) * 20)
        arcade.draw_point(SCREEN_WIDTH / 2 + tx * PIXELS_PER_METER, SCREEN_HEIGHT / 2 + tz * PIXELS_PER_METER,
                          arcade.color.BLACK, pow(2, ty) * 20)

        # yaw_line_x = math.cos(-yaw + math.pi / 2) * 15 + tx
        # yaw_line_z = math.sin(-yaw + math.pi / 2) * 15 + tz
        yaw_line_x = math.cos(-yaw - math.pi/2) * 15 + tx
        yaw_line_z = math.sin(-yaw - math.pi/2) * 15 + tz
        # arcade.draw_line(SCREEN_WIDTH / 2 + tx * PIXELS_PER_METER, SCREEN_HEIGHT / 2 - tz * PIXELS_PER_METER,
        #                  SCREEN_WIDTH / 2 + yaw_line_x * PIXELS_PER_METER,
        #                  SCREEN_HEIGHT / 2 - yaw_line_z * PIXELS_PER_METER, arcade.color.GREEN)
        arcade.draw_line(SCREEN_WIDTH / 2 + tx * PIXELS_PER_METER, SCREEN_HEIGHT / 2 + tz * PIXELS_PER_METER,
                         SCREEN_WIDTH / 2 + yaw_line_x * PIXELS_PER_METER,
                         SCREEN_HEIGHT / 2 - yaw_line_z * PIXELS_PER_METER, arcade.color.GREEN)

        for p in points:
            # arcade.draw_line(SCREEN_WIDTH/2, SCREEN_HEIGHT,  SCREEN_WIDTH/2 + p[1][0], SCREEN_HEIGHT/2 + p[1][2],
            #                  arcade.color.BLACK)
            cloud_color = arcade.color.BLACK
            if abs(p[1][1]) > 0.1:
                cloud_color = arcade.color.RED

            point_angle = math.atan2(p[1][2], p[1][0])
            point_distance = math.sqrt(p[1][2] * p[1][2] + p[1][0] * p[1][0])

            point_angle_rotated = point_angle + -yaw
            point_rotated = (
            math.cos(point_angle_rotated) * point_distance, math.sin(point_angle_rotated) * point_distance)
            point_transformed = (point_rotated[0] + tx, point_rotated[1] + tz)
            self.stored_transformed_points.append(point_transformed)
            while len(self.stored_transformed_points) > MAX_STORED_POINTS:
                self.stored_transformed_points.pop(0)

            # arcade.draw_circle_filled(p[1][0] * PIXELS_PER_METER / 4 + SCREEN_WIDTH/2,
            #                           p[1][2] * PIXELS_PER_METER / 4 + SCREEN_HEIGHT/2, 2, cloud_color)

        for p in self.stored_transformed_points:
            arcade.draw_circle_filled(p[0] * PIXELS_PER_METER + SCREEN_WIDTH/2, -p[1] * PIXELS_PER_METER + SCREEN_HEIGHT/2,
                                      2, arcade.color.BLACK)
        # arcade.draw_line(self.time * 10, 0, SCREEN_WIDTH, SCREEN_HEIGHT, arcade.color.BLACK, 2)
        self.time += 1 / 60.0


def main():
    window = ZedPosRenderer()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
