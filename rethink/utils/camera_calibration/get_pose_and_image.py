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

cam = D435()
panda = PandaRobot()
panda.panda.move_to_start()
pose = panda.panda.get_state().q
tpose = panda.panda.get_pose()
print(tpose)
print(pose)
tpose[2][3] -=0.4
panda.panda.move_to_pose(tpose)
# cam.capture_current_info()
# image = cam.get_color_info()[0]
# cv2.imwrite("image4.png",image)

capture_pose = [[-2.62117052589383, 0.27274232822552064, 2.8916160119458247, -0.7573939886344107, -0.3653997534360118, 0.8943572264512378, -2.3128942678827378],
                [-2.8612601318363575, 0.9819311937951204, 2.8633279143885564, -2.4652915328845637, -0.36673162149720717, 1.9530202775796253, -2.224280670141068],
                [-2.804427080783104, 1.307971106124795, 2.6710108352106174, -2.7435440940187688, -0.9202820362748122, 1.9133149375120797, -1.8597193001169297],
                [-1.7517838039343525, 1.482401121624729, 2.794125486106537, -2.909970284010235, -1.072715748179847, 1.769423575957616, -1.2140521680264744]]
