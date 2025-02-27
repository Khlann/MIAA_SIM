# from Robotic_Arm.rm_robot_interface import *

# robot = RoboticArm(rm_thread_mode_e.RM_TRIPLE_MODE_E)
# handle = robot.rm_create_robot_arm("192.168.1.18", 8080)
# print("机械臂ID：", handle.id)

# software_info = robot.rm_get_arm_software_info()
# if software_info[0] == 0:
#     print("\n================== Arm Software Information ==================")
#     print("Arm Model: ", software_info[1]['product_version'])
#     print("Algorithm Library Version: ", software_info[1]['algorithm_info']['version'])
#     print("Control Layer Software Version: ", software_info[1]['ctrl_info']['version'])
#     print("Dynamics Version: ", software_info[1]['dynamic_info']['model_version'])
#     print("Planning Layer Software Version: ", software_info[1]['plan_info']['version'])
#     print("==============================================================\n")
# else:
#     print("\nFailed to get arm software information, Error code: ", software_info[0], "\n")
from Robotic_Arm.rm_robot_interface import *
robot_controller = RobotArmController("192.168.1.18", 8080, 3)