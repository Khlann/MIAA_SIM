import cv2
import numpy as np
import cv2.aruco as aruco
import json
import panda_py
from scipy.optimize import least_squares
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0,project_root)

from rethink.camera import D435
from rethink.robot import PandaRobot


T_eye2ee = np.array([
    [0.01324788, 0.99925666, -0.03620257, 0.05672094],
    [-0.99713529, 0.01589888, 0.07394889, 0.02921566],
    [0.0744695, 0.0351192, 0.9966047, -0.14172613],
    [0., 0., 0., 1.]
])

cam = D435()
robot = PandaRobot()
robot.panda.move_to_start()

pose = robot.get_pose()
pose = np.array(pose)
pose = np.dot(T_eye2ee, pose)

image = cam.get_aligned_images()[0]
cv2.imshow("image", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

cam.capture_current_info()
x_3d, y_3d, z_3d = cam.xy2d2xy3d(1134,943)

pose[0][3] += x_3d
pose[1][3] += y_3d
pose[2][3] += z_3d

robot.move_to_pose(pose)
