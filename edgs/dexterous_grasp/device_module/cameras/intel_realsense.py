import numpy as np
import pyrealsense2 as rs
from functools import wraps
from dexterous_grasp.logger_module import LoggerValidator
import time

class IntelRealSense(LoggerValidator):
    def __init__(self, depth_res=(1024, 768), color_res=(1920, 1080), depth_format=rs.format.z16,
                 color_format=rs.format.bgr8, fps=30, logger_manager=None):
        super().__init__(logger_manager)
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
        return self.color_image, color_intrinsics

    @check_frames
    def get_depth_info(self):
        depth_intrinsics = self.depth_frame.profile.as_video_stream_profile().intrinsics
        return self.depth_image, depth_intrinsics

    @check_frames
    def xy2d2xy3d(self, x_2d, y_2d):
        # depth = self.depth_frame.get_distance(int(x_2d), int(y_2d))
        depth_frame, depth_intrinsics = self.get_depth_info()
        depth = depth_frame[int(y_2d)][int(x_2d)]
        x_3d, y_3d, z_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x_2d, y_2d], depth)
        x_3d = x_3d / 1000
        y_3d = y_3d / 1000
        z_3d = z_3d / 1000
        return x_3d, y_3d, z_3d
    
    def save_npz(self, filename):
        np.savez(filename, color_image=self.color_image, depth_image=self.depth_image) 
