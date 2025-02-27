import numpy as np
import pyrealsense2 as rs
from functools import wraps
import time
import cv2

class IntelRealSense():
    def __init__(self, depth_res=(1280, 720), color_res=(1920, 1080), depth_format=rs.format.z16,
                 color_format=rs.format.bgr8, fps=30, logger_manager=None):
        self.logger_manager = logger_manager
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        # Enable streams with passed configurations
        self.config.enable_stream(rs.stream.depth, depth_res[0], depth_res[1], depth_format, fps)
        self.config.enable_stream(rs.stream.color, color_res[0], color_res[1], color_format, fps)

        self.profile = self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

        self.color_frame = None
        self.depth_frame = None

        # 设置彩色相机的自动曝光
        color_sensor = self.profile.get_device().first_color_sensor()
        color_sensor.set_option(rs.option.enable_auto_exposure, True)

    def capture_current_info(self, warmup_time=2):
        # 让相机适应光线
        print(f"Waiting for {warmup_time} seconds to let the camera adjust to the light...")
        start_time = time.time()
        while time.time() - start_time < warmup_time:
            self.pipeline.wait_for_frames()

        frames = self.pipeline.wait_for_frames()
        aligned_frames = self.align.process(frames)
        self.color_frame = aligned_frames.get_color_frame()
        self.depth_frame = aligned_frames.get_depth_frame()

        self.color_image = np.asanyarray(self.color_frame.get_data())
        self.depth_image = np.asanyarray(self.depth_frame.get_data())

    # 装饰器函数，用于检查帧是否已经捕获
    def check_frames(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.color_frame is None or self.depth_frame is None:
                raise RuntimeError("Frames are not captured yet. Please run 'capture_current_info()' first.")
            return func(self, *args, **kwargs)

        return wrapper

    @check_frames
    def get_color_info(self):
        color_intrinsics = self.color_frame.profile.as_video_stream_profile().intrinsics
        fx, fy, ppx, ppy = color_intrinsics.fx, color_intrinsics.fy, color_intrinsics.ppx, color_intrinsics.ppy
        camera_matrix = np.array([[fx, 0, ppx], 
                          [0, fy, ppy], 
                          [0, 0, 1]], dtype=np.float32)
        return self.color_image, color_intrinsics, camera_matrix

    @check_frames
    def get_depth_info(self):
        depth_intrinsics = self.depth_frame.profile.as_video_stream_profile().intrinsics
        return self.depth_image, depth_intrinsics

    @check_frames
    def xy2d2xy3d(self, x_2d, y_2d):
        depth = self.depth_frame.get_distance(int(x_2d), int(y_2d))
        _, depth_intrinsics = self.get_depth_info()
        x_3d, y_3d, z_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x_2d, y_2d], depth)
        return x_3d, y_3d, z_3d

    def get_aligned_images(self):
        frames = self.pipeline.wait_for_frames()  
        aligned_frames = self.align.process(frames)  
        color_frame = aligned_frames.get_color_frame()  
        intrinsics = color_frame.profile.as_video_stream_profile().intrinsics 
        rgb_image = np.asanyarray(color_frame.get_data())
        dist_coeffs = np.array([intrinsics.coeffs[0], intrinsics.coeffs[1], intrinsics.coeffs[2], intrinsics.coeffs[3], intrinsics.coeffs[4]])
        camera_matrix = np.array([[intrinsics.fx, 0, intrinsics.ppx],
                                [0, intrinsics.fy, intrinsics.ppy],
                                [0, 0, 1]])
        undistorted_image = cv2.undistort(rgb_image, camera_matrix, dist_coeffs)
        return undistorted_image, camera_matrix, dist_coeffs