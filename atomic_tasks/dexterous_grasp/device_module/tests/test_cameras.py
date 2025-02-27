import unittest
from dexterous_grasp.device_module import D405

class TestIntelRealSense(unittest.TestCase):
    def setUp(self):
        # Set up the RealSense camera with default resolution and settings
        self.realsense = D405()
        self.realsense.capture_current_info()

    def test_capture_image(self):
        # Capture an image and ensure it is not None
        color_image, color_intrinsics = self.realsense.get_color_info()
        self.assertIsNotNone(color_image, "Color frame is None!")
        self.assertEquals(color_image.shape, (720, 1280, 3))

    def test_capture_depth(self):
        # Capture a depth frame and ensure it is not None
        depth_image, depth_intrinsics = self.realsense.get_depth_info()
        self.assertIsNotNone(depth_image, "Depth frame is None!")
        self.assertEquals(depth_image.shape, (720, 1280))

    def test_intrinsics(self):
        # Capture aligned frames and check if the intrinsics are dynamic or static
        _, color_intrinsics = self.realsense.get_color_info()
        _, depth_intrinsics = self.realsense.get_depth_info()

        # Check if intrinsics for color and depth are not None
        self.assertIsNotNone(color_intrinsics, "Color intrinsics are None!")
        self.assertIsNotNone(depth_intrinsics, "Depth intrinsics are None!")

if __name__ == '__main__':
    unittest.main()
