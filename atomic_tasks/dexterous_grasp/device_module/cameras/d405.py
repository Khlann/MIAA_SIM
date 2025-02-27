from .intel_realsense import IntelRealSense

class D405(IntelRealSense):
    def __init__(self, logger_manager=None):
        # Initialize with L515 specific settings or pass to parent constructor
        super().__init__(depth_res=(1280, 720), color_res=(1280, 720),logger_manager=logger_manager)