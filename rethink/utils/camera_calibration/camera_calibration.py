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


def get_transform_from_rotation_translation(rotation, translation):
    rotation = np.array(rotation)
    translation = np.array(translation)

    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation
    transformation_matrix[:3, 3] = translation
    return transformation_matrix

def get_aruco2camera_transform(cam, marker_length_m):
    rgb_image, camera_matrix, dist_coeffs = cam.get_aligned_images()
    # cv2.imshow("rgb_image",rgb_image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    corners, _, image = detect_aruco_markers(rgb_image)
    
    if corners is not None:
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length_m, camera_matrix, dist_coeffs)
        # cv2.drawFrameAxes(image, camera_matrix, dist_coeffs, rvec, tvec, marker_length_m)
        # cv2.imshow("ArUco Marker", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        rotation_matrix = cv2.Rodrigues(rvec)[0]
        translation_vector = tvec.flatten()
        return get_transform_from_rotation_translation(rotation_matrix, translation_vector)
    return None

def detect_aruco_markers(image):
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is None:
        return None, None, None
    
    target_id = 20
    corners = [corners[i] for i in range(len(ids)) if ids[i] == target_id]
    ids = [ids[i] for i in range(len(ids)) if ids[i] == target_id]
    cv2.aruco.drawDetectedMarkers(image, corners)
    return corners, ids, image

def get_robot_pose_list():
    file_path = '/home/arlen/arlen/miaa_sim/rethink/utils/camera_calibration/pose_data.json'
    q_list = []
    with open(file_path, 'r') as file:
        pose_list = json.load(file)
    for pose in pose_list:
        q = panda_py.ik(pose)   
        q_list.append(q.tolist())
    return q_list

def get_aruco_pose(cam):
    for attempt in range(10):
        aruco2camera_transform = get_aruco2camera_transform(cam, 0.1)
        if aruco2camera_transform is None:
            print(f"Attempt {attempt + 1}: ArUco marker not detected. Please try again.")
        else:
            break
    else:
        raise Exception("ArUco marker not detected after multiple attempts. Calibration failed.")
    return aruco2camera_transform

if __name__ == "__main__":
    # 类初始化
    cam = D435()
    panda = PandaRobot()

    # cam.capture_current_info()
    # image,_,camera_matrix = cam.get_color_info()
    # dist_coeffs = np.zeros((4, 1), dtype=np.float32)

    # joint_list = get_robot_pose_list()
    joint_list = [
        [-0.18494118377618624, -0.26550634451079785, 0.18896153811206218, -2.5629795703553317, 0.0029396774633407862, 2.2968021585437097, 0.7635257787060581],
        [-0.1659034346258431, -0.1738034915714933, 0.29321426558653385, -2.5394478090185864, 0.002965463533597888, 2.3939471626990794, 0.8689914808207087],
        [-0.143577719384999, -0.3482314158949935, 0.31201607492764466, -2.6523726473356546, 0.004015307215003932, 2.391871020555496, 0.8689149516365594],
        [-0.2394086679499137, -0.24214371871592336, 0.30443194482619296, -2.567132901810763, 0.003972357762411806, 2.3858046925286147, 0.85954496643582],
        [-0.1949551108927605, -0.2555569321439977, 0.3909656345760613, -2.603484154249492, 0.004018255788203221, 2.3860811625471245, 0.865481970463362],
        [-0.3009871426160567, -0.256079068654897, 0.37105117472981963, -2.596315233498289, 0.0040181387104570735, 2.3867167224089303, 0.8813919473048529],
        [-0.26256345412751364, -0.2660886309857954, 0.4813758351368634, -2.596601889091094, 0.003966965399771898, 2.3867705318927763, 0.87846815463795],
        [-0.22442928713106972, -0.4692756001041881, 0.48160831124740666, -2.6502411915917046, 0.04840535939138845, 2.2691005458037057, 0.8801497874193721],
        [-0.3109965091757058, -0.2817254594961802, 0.47547728945497875, -2.5392336698164018, 0.04651019000602356, 2.2717086988290145, 0.9157418129800674],
        [-0.3349182004970417, -0.13634896674956706, 0.49937907605191156, -2.474643598355745, 0.04643070351414655, 2.3228894461790714, 1.1394732656841018],
        [-0.3177163781910612, -0.2582545812924703, 0.5587883548595254, -2.535310624109777, 0.044475726132777386, 2.3189228826363877, 0.7225956082631066],
        [-0.36054367944650484, -0.3135714053699683, 0.5642024499227465, -2.597542998665257, 0.0456510877014524, 2.320363795518875, 0.7592806253375286],
        [-0.4493224136116821, -0.11879935851546185, 0.6044934148370174, -2.5126142409809846, 0.04627546298172739, 2.358419310754345, 1.0811661883813646]
    ]       
    panda.panda.move_to_start()
    T_qr_cam_list = []
    T_ee_base_list = [panda.calculate_fk(joint) for joint in joint_list]    

    for joint in joint_list:
        panda.move_to_joint_position(joint)
        # aruco_pose = get_aruco_pose(cam)
        T_qr_cam = get_aruco2camera_transform(cam, 0.1)
        T_qr_cam_list.append(T_qr_cam)

    def hand_eye_calibration(T_ee_base_list, T_qr_cam_list):
        """
        进行眼在手的手眼标定，计算相机相对于末端执行器的变换矩阵 T_cam_ee。

        参数:
        T_ee_base_list (list): 包含多个 4x4 变换矩阵的列表，
                            每个矩阵表示机器人末端执行器相对于机器人基坐标系的变换。
        T_qr_cam_list (list): 包含多个 4x4 变换矩阵的列表，
                            每个矩阵表示相机相对于机器人基坐标系下某个标定物的变换。

        返回:
        np.ndarray: 4x4 的变换矩阵 T_cam_ee，表示相机相对于末端执行器的变换矩阵。
        """
        # 从 4x4 变换矩阵中提取旋转矩阵和平移向量
        R_ee_base = []
        t_ee_base = []
        R_cam_marker = []
        t_cam_marker = []

        for T_ee_base in T_ee_base_list:
            R_ee_base.append(T_ee_base[:3, :3])
            t_ee_base.append(T_ee_base[:3, 3])

        for T_qr_cam in T_qr_cam_list:
            R_cam_marker.append(T_qr_cam[:3, :3])
            t_cam_marker.append(T_qr_cam[:3, 3])

        # 调用 OpenCV 的手眼标定函数
        R_cam_ee, t_cam_ee = cv2.calibrateHandEye(R_ee_base, t_ee_base, R_cam_marker, t_cam_marker)

        # 构建 4x4 变换矩阵 T_cam_ee
        T_cam_ee = np.eye(4)
        T_cam_ee[:3, :3] = R_cam_ee
        T_cam_ee[:3, 3] = t_cam_ee.flatten()

        return T_cam_ee
        
    T_cam_ee = hand_eye_calibration(T_ee_base_list, T_qr_cam_list)
    print(T_cam_ee)

    # 验证与优化
    # 移动机械臂到新的位姿进行验证
    # new_pose = [-0.432316464946981, -0.5742772510595487, 0.3929305473199719, -2.4510107246198154, 0.20528068674272962, 1.9125126731647524, 0.7010845845482414]

    # panda.move_to_joint_position(new_pose)
    # T_ee_base_new = panda.get_pose()
    # image_new, _, _ = cam.get_aligned_images()

    # T_qr_cam_new = get_aruco2camera_transform(cam, 0.1)

    # # 通过T_cam_ee转换二维码位姿到机械臂末端坐标系下
    # T_qr_ee_predicted = np.dot(np.linalg.inv(T_ee_base_new), np.dot(T_cam_ee, T_qr_cam_new))

    # # 定义计算误差的函数
    # def calculate_error(predicted_pose, actual_pose):
    #     """
    #     计算预测位姿和实际位姿之间的误差
    #     :param predicted_pose: 预测的位姿矩阵
    #     :param actual_pose: 实际的位姿矩阵
    #     :return: 误差值
    #     """
    #     # 这里简单地计算两个矩阵对应元素差值的平方和的平方根
    #     error = np.linalg.norm(predicted_pose - actual_pose)
    #     return error

    # # 获取实际的机械臂末端位姿
    # actual_pose = panda.get_pose()

    # # 定义误差阈值
    # threshold = 0.1

    # # 与实际的机械臂末端位姿进行比较，计算误差
    # error = calculate_error(T_qr_ee_predicted, actual_pose)
    # if error > threshold:
    #     # 重新进行标定或优化
    #     print("Error is too large. Re-calibrate or optimize.")

    new_pose = [-0.432316464946981, -0.5742772510595487, 0.3929305473199719, -2.4510107246198154, 0.20528068674272962, 1.9125126731647524, 0.7010845845482414]
    T_ee_base = panda.calculate_fk(new_pose)
    panda.move_to_joint_position(new_pose)
    T_qr_cam_new = get_aruco2camera_transform(cam, 0.1)
    T_qr_base = T_ee_base @T_cam_ee@T_qr_cam_new

    print(T_qr_base)