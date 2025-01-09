from robot.controller import Controller
# from robot.camera import Camera
from config.robot_varant import robot_config
from config.object_varant import table_config,banana_config
from config.camera_varant import camera_config
import cv2

if __name__ == "__main__":
    controller = Controller()
    robot = controller.add_object(robot_config,position=[0.45,0,1],orientation=[1,0,0,0]) 
    arm = [0.5,0.5,0.5,0.5,0.5,0.5,0.5]
    current_qpos = robot.get_qpos()
    controller.set_robot_pose(robot,arm)
    controller.create_table(pose=[0,0,1],size=1.0,height=1.0)
    controller.add_obj(banana_config,position=[0,0,1],orientation=[1,0,0,0])
    controller.visualize(robot)
