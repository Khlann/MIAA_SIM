from .intel_realsense import IntelRealSense

class D435i(IntelRealSense):
    def __init__(self, logger_manager=None):
        super().__init__(depth_res=(1280, 720), color_res=(1920,1080),logger_manager=logger_manager)