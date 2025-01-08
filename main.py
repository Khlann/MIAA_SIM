from robot.controller import Controller
from robot.camera import Camera
from config.robot_varant import robot_config
from config.camera_varant import camera_config
from config.object_varant import table_config
import cv2

controller = Controller(robot_config)
controller.set_robot_pose(controller.robot_id,position=[0,0,0],orientation=[0,0,0,1])
controller.get_joint_info()
# 目标位置（弧度）
target_positions = [0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.5]  # 每个关节的目标位置
controller.control(target_positions)

#加载桌子
table_id = controller.add_object(table_config,position=[0,0,0],orientation=[0,0,0,1])
camera = Camera(camera_config)
img = camera.get_camera_image()
img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
cv2.imshow('camera',img)
cv2.waitKey(0)
cv2.destroyAllWindows()

controller.visualize()