from .intel_realsense import IntelRealSense

class L515(IntelRealSense):
    def __init__(self, logger_manager=None):
        super().__init__(depth_res=(1024, 768), color_res=(1920, 1080), logger_manager=logger_manager)