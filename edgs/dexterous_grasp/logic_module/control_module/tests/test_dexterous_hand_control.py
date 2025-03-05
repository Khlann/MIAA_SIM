import unittest
from dexterous_grasp.logic_module.control_module import DexterousHandController
from dexterous_grasp.config import hand_motion_params, hand_device_params


class TestDexterousHandController(unittest.TestCase):
    
    def setUp(self):
        # 创建 hand_motion_params 和 hand_device_params 的模拟对象
        self.dexterous_hand_controller = DexterousHandController(hand_motion_params, hand_device_params)

    def test_execute_grasp(self):
        # 执行抓取动作
        self.dexterous_hand_controller.execute_grasp()

    
        # 执行松开动作
        self.dexterous_hand_controller.abort_grasp()

    
if __name__ == "__main__":
    unittest.main()
    
