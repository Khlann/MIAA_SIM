"""
实现了3d点云稠密化的功能。具体来说，该代码实现了以下功能：
1. 从相机获取深度图像和彩色图像，并将它们转换为Open3D格式的点云。
2. 对每个点云进行统计滤波，去除离群点。
3. 将所有点云拼接在一起，得到一个完整的点云。
"""
import pyrealsense2 as rs
import open3d as o3d
import numpy as np
import cv2
import sys
import panda_py
import time
project_root = "/home/arlen/arlen/miaa_sim/atomic_tasks"
gsam_path = "/home/arlen/arlen/miaa_sim/atomic_tasks/external/gsam2"
sys.path.insert(0,project_root)
sys.path.insert(0,gsam_path)
from dexterous_grasp.logic_module.control_module import TaskController
from dexterous_grasp.logger_module.logger import LoggerManager
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.config import franka_config

# config
robot_type = "franka"
logger_manager = LoggerManager(project_root)
task_controller = TaskController(robot_type,franka_config, logger_manager)
cam = D435i(logger_manager)
origin_matrix = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]]
captured_pcds = []
num_neighbors = 20  # 每个点考虑的邻域点数
std_ratio = 2.0  # 标准差倍数

def get_pcd(cam, origin_matrix, num_neighbors, std_ratio, tf = None):
    cam.capture_current_info(2)
    color_image, color_intrinsics = cam.get_color_info()
    depth_image, depth_intrinsics = cam.get_depth_info()

    color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)

    depth_o3d = o3d.geometry.Image(depth_image)
    color_o3d = o3d.geometry.Image(color_image)
    rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_o3d, depth_o3d, convert_rgb_to_intensity=False)
    
    pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
        rgbd_image,
        o3d.camera.PinholeCameraIntrinsic(
            depth_intrinsics.width,
            depth_intrinsics.height,
            depth_intrinsics.fx,
            depth_intrinsics.fy,
            depth_intrinsics.ppx,
            depth_intrinsics.ppy
        )
    )

    if tf is not None:
        target_matrix = np.dot(np.linalg.inv(origin_matrix), tf)
        pcd.transform(target_matrix)
    else:
        pcd.transform(origin_matrix)
    pcd, ind = pcd.remove_statistical_outlier(num_neighbors, std_ratio)
    return pcd, color_image

for i in range(2):
    pcd, color_image = get_pcd(cam, origin_matrix, num_neighbors, std_ratio)
    captured_pcds.append(pcd)

# 进行点云拼接 可用
start_time = time.time()
combined_pcd = captured_pcds[0]
for i in range(1, len(captured_pcds)):
    trans_init = np.eye(4)
    reg_p2p = o3d.pipelines.registration.registration_icp(
        combined_pcd, captured_pcds[i], 0.02, trans_init,
        o3d.pipelines.registration.TransformationEstimationPointToPoint())
    captured_pcds[i].transform(reg_p2p.transformation)
    combined_pcd += captured_pcds[i]
end_time = time.time()
print(f"Point cloud registration finished in {end_time - start_time:.2f}s")
# 可视化拼接后的点云
o3d.visualization.draw_geometries([combined_pcd])