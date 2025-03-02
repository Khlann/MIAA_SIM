import sys
import cv2
import numpy as np
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
gsam_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2"
sys.path.insert(0,project_root)
sys.path.insert(0,gsam_path)

from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.logic_module.planning_module import FrankaArmPlanner
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logic_module.understanding_module import Dinox
from dexterous_grasp.logic_module.vision_module import Estimation
from dexterous_grasp.logic_module.vision_module import GroundedSAM
from dexterous_grasp.config import franka_config
from dexterous_grasp.config import ground_sam2_config, file_paths

# Todo:重新生成一份手眼标定矩阵
T_C_E = np.array([
    [0.01324788, 0.99925666, -0.03620257, 0.08072094],
    [-0.99713529, 0.01589888, 0.07394889, -0.02021566],
    [0.0744695, 0.0351192, 0.9966047, -0.14172613],
    [0., 0., 0., 1.]
])#相机标定： 相机到末端法兰盘的变换矩阵

logger_manager = LoggerManager(project_root)
robot_type = "franka"
task_controller = TaskController(robot_type,franka_config, logger_manager)
robot_planner = FrankaArmPlanner()
dinox = Dinox()
# grounded_sam2 = GroundedSAM(ground_sam2_config)
estimation2D = Estimation()
# task_controller.robotic_arm_controller.close_gripper()

# 从相机获取图像
cam = D435i(logger_manager)
cam.capture_current_info()
cola_image , color_intrinsics = cam.get_color_info()
depth_image, depth_intrinsics = cam.get_depth_info()
cv2.imwrite("cola_image.png", cola_image)
# user_input = "yellow nailong"
user_input = "yellow banana"
dinox_mask = dinox.get_mask("cola_image.png", user_input)
cv2.imwrite("dinox_mask.png", dinox_mask)
# dinox_mask = cv2.imread("/home/arlen/arlen/miaa_sim/dinox_mask.png")

# text_prompt = "red apple"
# mask, input_boxe, label, confidence = grounded_sam2.segment(text_prompt, cola_image)
# cv2.imwrite("mask.png", mask)

# mask = cv2.imread("/home/arlen/arlen/miaa_sim/dino_mask.png")

# 假设 dinox_mask 是三通道图像
# 将其转换为灰度图
# gray = cv2.cvtColor(dinox_mask, cv2.COLOR_BGR2GRAY)

# 进行二值化处理
_, binary = cv2.threshold(dinox_mask, 127, 255, cv2.THRESH_BINARY)

# 查找轮廓
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 找到最大轮廓
max_contour = max(contours, key=cv2.contourArea)

# 计算最大外接多边形
epsilon = 0.01 * cv2.arcLength(max_contour, True)
approx = cv2.approxPolyDP(max_contour, epsilon, True)

# 找到最长斜边
max_length = 0
longest_edge = None
for i in range(len(approx)):
    p1 = approx[i][0]
    p2 = approx[(i + 1) % len(approx)][0]
    length = np.linalg.norm(p1 - p2)
    if length > max_length:
        max_length = length
        longest_edge = (p1, p2)

# 显示最长斜边
cv2.line(dinox_mask, tuple(longest_edge[0]), tuple(longest_edge[1]), (0, 0, 255), 2)

# 计算斜边与 x 轴的夹角
dx = longest_edge[1][0] - longest_edge[0][0]
dy = longest_edge[1][1] - longest_edge[0][1]
angle = np.arctan2(dy, dx) * 180 / np.pi

print(f"最长斜边与 x 轴的夹角: {angle} 度")

# 绘制表示夹角的箭头
start_point = tuple(longest_edge[0])
end_point = tuple(longest_edge[1])
# 沿着 x 轴正方向画一条辅助线
x_axis_end = (start_point[0] + 100, start_point[1])
cv2.line(dinox_mask, start_point, x_axis_end, (255, 0, 0), 2)  # 蓝色辅助线
# 画表示夹角的箭头
cv2.arrowedLine(dinox_mask, start_point, end_point, (0, 255, 0), 2)

# 显示结果
cv2.imshow('Max Enclosing Polygon with Longest Edge', dinox_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
# cv2.imshow("mask", mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# dinox_mask = dinox.get_mask("cola_image.png", user_input)
# cv2.imwrite("dinox_mask.png", dinox_mask)
# dinox_mask = cv2.imread("/home/arlen/arlen/miaa_sim/dinox_mask.png")
# dinox_mask = dinox_mask[:, :, 0]
# cv2.imshow("dinox_mask", dinox_mask)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

# position, z_axis_radian,t = estimation2D.process_mask_and_transform( dinox_mask, cam,T_C_E)
P_O_C = estimation2D.process_mask_and_transform(mask, cam)


# 创建旋转矩阵，使末端法兰盘E垂直朝向桌面
# 绕z轴旋转R弧度
R = np.pi/90

T_E_B = task_controller.robotic_arm_controller.robot_arm.get_pose()

q = robot_planner.plan_curobo(P_O_C, R, T_C_E, T_E_B)
task_controller.robotic_arm_controller.execute_movement_joints(q)
# task_controller.robotic_arm_controller.execute_movement_pose(tpose)
task_controller.robotic_arm_controller.close_gripper()
task_controller.robotic_arm_controller.execute_movement_pose(task_controller.start_pose)


