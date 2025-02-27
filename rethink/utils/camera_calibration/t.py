import numpy as np
import cv2

def hand_eye_calibration(T_ee_base_list, T_qr_cam_list):
    """
    进行眼在手的手眼标定，计算相机相对于末端执行器的变换矩阵 T_cam_ee。

    参数:
    T_ee_base_list (list): 包含多个 4x4 变换矩阵的列表，表示机器人末端执行器相对于机器人基坐标系的变换矩阵。
    T_qr_cam_list (list): 包含多个 4x4 变换矩阵的列表，表示相机相对于机器人基坐标系下某个标定物的变换矩阵。

    返回:
    np.ndarray: 4x4 的变换矩阵 T_cam_ee，表示相机相对于末端执行器的变换矩阵。
    """
    # 从 4x4 变换矩阵中提取旋转矩阵和平移向量
    R_gripper2base = []
    t_gripper2base = []
    R_target2cam = []
    t_target2cam = []

    for T_ee_base in T_ee_base_list:
        R_gripper2base.append(T_ee_base[:3, :3])
        t_gripper2base.append(T_ee_base[:3, 3])

    for T_qr_cam in T_qr_cam_list:
        R_target2cam.append(T_qr_cam[:3, :3])
        t_target2cam.append(T_qr_cam[:3, 3])

    # 调用 OpenCV 的手眼标定函数
    R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam)

    # 构建 4x4 变换矩阵 T_cam_ee
    T_cam_ee = np.eye(4)
    T_cam_ee[:3, :3] = R_cam2gripper
    T_cam_ee[:3, 3] = t_cam2gripper.flatten()

    return T_cam_ee
# 示范 T_ee_base_list
T_ee_base_list = [
    np.array([
        [0.866, -0.5, 0, 0.2],
        [0.5, 0.866, 0, 0.3],
        [0, 0, 1, 0.5],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.707, -0.707, 0, 0.3],
        [0.707, 0.707, 0, 0.4],
        [0, 0, 1, 0.6],
        [0, 0, 0, 1]
    ]),
    np.array([
        [1, 0, 0, 0.4],
        [0, 1, 0, 0.5],
        [0, 0, 1, 0.7],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.923, -0.385, 0, 0.1],
        [0.385, 0.923, 0, 0.2],
        [0, 0, 1, 0.4],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.643, -0.766, 0, 0.25],
        [0.766, 0.643, 0, 0.35],
        [0, 0, 1, 0.55],
        [0, 0, 0, 1]
    ])
]

# 示范 T_qr_cam_list
T_qr_cam_list = [
    np.array([
        [0.985, -0.174, 0, 0.05],
        [0.174, 0.985, 0, 0.1],
        [0, 0, 1, 0.2],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.939, -0.342, 0, 0.15],
        [0.342, 0.939, 0, 0.2],
        [0, 0, 1, 0.3],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.966, -0.259, 0, 0.1],
        [0.259, 0.966, 0, 0.15],
        [0, 0, 1, 0.25],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.951, -0.309, 0, 0.08],
        [0.309, 0.951, 0, 0.12],
        [0, 0, 1, 0.22],
        [0, 0, 0, 1]
    ]),
    np.array([
        [0.978, -0.208, 0, 0.13],
        [0.208, 0.978, 0, 0.18],
        [0, 0, 1, 0.28],
        [0, 0, 0, 1]
    ])
]

# 求解手眼标定矩阵
T_cam_ee = hand_eye_calibration(T_ee_base_list, T_qr_cam_list)
print("相机坐标系到机械臂末端坐标系的变换矩阵 T_cam_ee:")
print(T_cam_ee)
