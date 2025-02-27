import cv2
import panda_py
from panda_py import libfranka

import sys
import os
import json
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[3])

sys.path.insert(0, project_root)

from rethink.camera import D435

# 机器人参数
hostname = "172.16.0.2"
username = "franka"
password = "franka123"

# 初始化机器人
desk = panda_py.Desk(hostname, username, password)
desk.unlock()
desk.activate_fci()
panda = panda_py.Panda(hostname)

# 初始化相机
cam = D435()
pose_list = []
count = 0

while True:
    cam.capture_current_info()
    rgb_image, camera_matrix, dist_coeffs = cam.get_aligned_images()
    cv2.imshow("rgb_image", rgb_image)
    key = cv2.waitKey(1)
    if key == ord('r'):
        pose = panda.get_pose()
        pose_list.append(pose.tolist())  # 将numpy数组转换为列表，以便保存为JSON
        count += 1
        print(pose)
        if count == 10:
            # 保存到JSON文件，使用 indent 参数进行格式化
            with open('pose_data.json', 'w') as f:
                json.dump(pose_list, f, indent=4)
            print("10组姿态数据已保存到 pose_data.json")
            break

cv2.destroyAllWindows()