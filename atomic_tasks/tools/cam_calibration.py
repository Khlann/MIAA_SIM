# 这个是用于测试眼在手上精准度的代码
import urx.robot
from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logger_module.logger import LoggerManager
import cv2
from scipy.spatial.transform import Rotation as R

import numpy as np
log = LoggerManager()
cam = D435i(log)
cam.capture_current_info()
image,_ = cam.get_color_info()
cv2.imshow('img',image)
cv2.waitKey(0)
cv2.destroyAllWindows()

from dexterous_grasp.logic_module.vision_module import Estimation2D
from dexterous_grasp.config import planning_module_varant
e2c = planning_module_varant.end2camera
import urx
ur5 = urx.Robot("192.168.1.215")
estimation = Estimation2D(log)
d1 = estimation.get_3d_postion(1693,580,cam)#right up
d2 = estimation.get_3d_postion(1191,411,cam)#left up
d3 = estimation.get_3d_postion(1172,564,cam)#left down
d4 = estimation.get_3d_postion(1330,580,cam)#right down
radian = [1,1]
# d1c = estimation.transform_to_base_coordinates(d1,radian,e2c)
# d2c = estimation.transform_to_base_coordinates(d2,radian,e2c)
# d3c = estimation.transform_to_base_coordinates(d3,radian,e2c)
end_pose = ur5.getl()

from scipy.spatial.transform import Rotation as R

def euler_xyz_to_matrix(rx, ry, rz):
    """
    将欧拉角（绕x, y, z轴旋转）转换为旋转矩阵
    """
    rotation = R.from_euler('xyz', [rx, ry, rz], degrees=False)
    return rotation.as_matrix()

def pose_to_transformation_matrix(x, y, z, rx, ry, rz):
    """
    将6D姿态（位置 + 欧拉角）转换为4x4的齐次变换矩阵
    """
    rotation_matrix = euler_xyz_to_matrix(rx, ry, rz)
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation_matrix
    transformation_matrix[:3, 3] = [x, y, z]
    return transformation_matrix

def camera_to_base(end_pose, end2camera, points_camera):
    """
    将相机坐标系下的3D点转换为基坐标系下的3D点

    Parameters:
        end_pose (list or np.ndarray): 末端执行器的6D姿态 [x, y, z, rx, ry, rz]
        end2camera (dict): 包含 'rotation' (3x3矩阵) 和 'translation' (3,) 的字典
        points_camera (list, tuple, or np.ndarray): 相机坐标系下的3D点，可以是单个点 (3,) 或多个点 (N, 3)

    Returns:
        np.ndarray: 基坐标系下的3D点，形状为 (3,) 或 (N, 3)
    """
    # 将输入转换为 numpy 数组
    points_camera = np.array(points_camera)

    # 检查输入点的维度
    if points_camera.ndim == 1:
        if points_camera.shape[0] != 3:
            raise ValueError("单个点的形状不正确，应该是 (3,)")
        points_camera = points_camera.reshape(1, 3)  # 转换为 (1, 3)
        single_point = True
    elif points_camera.ndim == 2:
        if points_camera.shape[1] != 3:
            raise ValueError("points_camera 应该是形状为 (N, 3) 的数组")
        single_point = False
    else:
        raise ValueError("points_camera 的维度不正确，应该是 (3,) 或 (N, 3)")

    # 解构末端姿态
    x, y, z, rx, ry, rz = end_pose

    # 构建末端到基坐标系的变换矩阵
    T_base_end = pose_to_transformation_matrix(x, y, z, rx, ry, rz)

    # 构建末端到相机坐标系的变换矩阵
    R_end_camera = end2camera['rotation']
    t_end_camera = end2camera['translation']
    T_end_camera = np.eye(4)
    T_end_camera[:3, :3] = R_end_camera
    T_end_camera[:3, 3] = t_end_camera

    # 计算从相机坐标系到基坐标系的整体变换矩阵
    T_base_camera = T_base_end @ T_end_camera  # 使用 @ 进行矩阵乘法

    # 将每个点转化为齐次坐标 [x, y, z, 1] 形式
    ones = np.ones((points_camera.shape[0], 1))
    points_camera_hom = np.hstack((points_camera, ones))  # 形状 (N, 4)

    # 应用变换矩阵
    points_base_hom = (T_base_camera @ points_camera_hom.T).T  # 形状 (N, 4)

    # 转换回非齐次坐标
    points_base = points_base_hom[:, :3]

    if single_point:
        return points_base[0]
    return points_base



# 旋转矩阵和位移向量
rotation_matrix = {
        'rotation': np.array([
            [-0.99928889,  0.03515113, -0.01364238],
            [ 0.01268125, -0.02742233, -0.9995435 ],
            [-0.03550919, -0.99900571,  0.02695707]
        ]),
        'translation': np.array([0.04150159, -0.04781294, 0.03821502])
    }

# translation_vector = np.array([0.04150159, -0.04781294, 0.03821502])
d1c=camera_to_base(end_pose,rotation_matrix,d1)
d2c=camera_to_base(end_pose,rotation_matrix,d2)
d3c=camera_to_base(end_pose,rotation_matrix,d3)
d4c=camera_to_base(end_pose,rotation_matrix,d4)
print("d1:",d1c,"\n")
print("d2:",d2c,"\n")
print("d3:",d3c,"\n")
print("d4c",d4c,"\n")

x1 = np.sqrt((d1c[0]-d2c[0])**2+(d1c[1]-d2c[1])**2+ (d1c[2]-d2c[2])**2)
x2 = np.sqrt((d3c[0]-d4c[0])**2+(d3c[1]-d4c[1])**2+ (d3c[2]-d4c[2])**2)


print("x1:",x1,"\n")
print("x2:",x2,"\n")
print("endpose",end_pose,"\n")
#1075,928
#1078,775
#1083,623