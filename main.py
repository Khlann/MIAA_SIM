from robot.controller import Controller
# from robot.camera import Camera
from config.robot_varant import robot_config
from config.object_varant import table_config,banana_config,cup_config
from config.camera_varant import camera_config
import cv2
import numpy as np
if __name__ == "__main__":
    controller = Controller()
    # robot = controller.add_object(robot_config,position=[0.37,0,1],orientation=[0,0,0,1]) 
    # pose0 = [-0.09494194, 0.23374271, 0.12117605, -1.0869864, -0.041404177, 1.6850036, 0.8100117, -1,-1]
    pose1 = [-0.09494194, 0.23374271, 0.12117605, -1.0869864, -0.041404177, 1.6850036, 0.8100117, 0.02400002, 0.02400003]
    pose2 = [0.21446425, -0.62299305, -0.16168733, -2.3664722, -0.09338276, 1.7050921, 1.059, 0.022, 0.021999994]
    pose2_3 = [0.2807816, 0.06503955, -0.19345255, -2.822746, 0.04314058, 2.842783, 0.8810461, 0.039999958, 0.039999958]
    # pose3 =[0.16712324, 0.3304621, -0.05479945, -2.7666037, 0.21289669, 3.051275, 0.73704845, 0.039999958, 0.039999954]
    # pose4 =[0.16712324, 0.3304621, -0.05479945, -2.7666037, 0.21289669, 3.051275, 0.73704845, 0.01769958, 0.01769954]
    # pose5 =[0.25614867, -0.3213782, -0.21498922, -2.8050687, -0.10736658, 2.4444273, 0.971751, 0.01769958, 0.01769954]
    pose3 = [0.225228, 0.30376562, -0.06447889, -2.7651474, 0.20479356, 3.0225291, 0.7951184, 0.03981996, 0.03981996]
    # pose4 = [0.225228, 0.30376562, -0.06447889, -2.7651474, 0.20479356, 3.0225291, 0.7951184, 0.02081996, 0.02081996]
    # pose5 = [0.3059081, 0.10595425, -0.17528498, -2.8085804, 0.08144568, 2.868615, 0.8880116, 0.020537796, 0.020537793]
    pose4 = [0.225228, 0.30376562, -0.06447889, -2.7651474, 0.20479356, 3.0225291, 0.7951184, -1, -1]
    pose5 = [0.3059081, 0.10595425, -0.17528498, -2.8085804, 0.08144568, 2.868615, 0.8880116, -1, -1]
    # current_qpos = robot.get_qpos()
    # controller.create_table(pose=[0,0,1],size=1.0,height=1.0)
    # banana = controller.add_obj(banana_config,position=[0,0,1],orientation=[1,0,0,0])
    # box = controller.create_box(                                                                                                               
    #     [0, -0.04, 1],
    #     half_size=[0.025, 0.025, 0.025],
    #     color=[1.0, 0.0, 0.0],
    #     name="box",
    # )
    
    # controller.set_robot_pose(robot,pose0)
    # controller.visualize_trajectory(robot, pose1, pose2)
    # controller.visualize_trajectory(robot, pose2, pose2_3)
    # controller.visualize_trajectory(robot, pose2_3, pose3)
    # controller.visualize_trajectory(robot, pose3, pose4)
    # controller.visualize_trajectory(robot, pose4, pose5)
    
    obj = controller.add_multiple_objects()
    controller.visualize(obj)