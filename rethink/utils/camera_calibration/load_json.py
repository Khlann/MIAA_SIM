import json
import panda_py

# 定义 JSON 文件的路径
file_path = '/home/arlen/arlen/miaa_sim/robot/camera_calibration/pose_data.json'


with open(file_path, 'r') as file:
    # 加载 JSON 数据到一个列表中
    pose_list = json.load(file)
    print("数据已成功加载到列表中。")

q_list = []
for pose in pose_list:
    # pose = panda_py.pose_from_list(pose)
    q = panda_py.ik(pose)   
    q_list.append(q.tolist())