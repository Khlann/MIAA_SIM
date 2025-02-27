from .intel_realsense import IntelRealSense

class D435(IntelRealSense):
    def __init__(self):
        # Initialize with L515 specific settings or pass to parent constructor
        super().__init__(depth_res=(1280, 720), color_res=(1920, 1080))