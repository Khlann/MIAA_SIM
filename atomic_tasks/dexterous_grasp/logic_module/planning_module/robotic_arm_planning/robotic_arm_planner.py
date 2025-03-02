import numpy as np
import copy
from scipy.spatial.transform import Rotation as R_cal
from dexterous_grasp.logic_module.planning_module import DexterousHandPlanner
from dexterous_grasp.logger_module import LoggerValidator
from dexterous_grasp.config import arm_motion_params
from .ik_solver import IKSolver
from typing import List
import cv2
import os
from dexterous_grasp.config import planning_module_varant

class RoboticArmPlanner(LoggerValidator):
    """
    Function:
    用于计算空间中的坐标关系
    6d pose, 4*4, 四元数
    """
    def __init__(self, camera2base, dexterous_hand_grasp_pose, grasp_safe_distance, standard_relative_pose_pairs, camera_intrinsic_matrix, logger_manager=None):
        super().__init__(logger_manager)
        self.camera2base_rotation = camera2base.rotation
        self.camera2base_translation = camera2base.translation
        self.end2base_forward_rotation = dexterous_hand_grasp_pose.forward_pose.end_rotation_matrix
        self.end2base_down_rotation = dexterous_hand_grasp_pose.down_pose.end_rotation_matrix
        self.tcp2end_forward_translation = dexterous_hand_grasp_pose.forward_pose.grasp_point_translation
        self.tcp2end_down_translation = dexterous_hand_grasp_pose.down_pose.grasp_point_translation
        self.forward_hand_rotvec = dexterous_hand_grasp_pose.forward_pose.end_rotvec #x,y,z
        self.down_hand_rotvec = dexterous_hand_grasp_pose.down_pose.end_rotvec
        self.grasp_safe_distance = grasp_safe_distance
        self.standard_relative_pose_pairs = standard_relative_pose_pairs.standard_relative_pose_pairs_dict #???
        self.dhp = DexterousHandPlanner(camera2base, dexterous_hand_grasp_pose, logger_manager=logger_manager)
        self.K = planning_module_varant.camera_intrinsic_matrix


    
    def get_target_base_coordinate(self, object_position_cam):
        object_position_base = self.camera2base_rotation @ object_position_cam + self.camera2base_translation
        try:
            x_base, y_base, z_base = object_position_base[planning_module_varant][0], object_position_base[0][1], object_position_base[0][2]
        except IndexError as e:
            x_base, y_base, z_base = object_position_base[0], object_position_base[1], object_position_base[2]
        return np.array([x_base, y_base, z_base])
    
    def get_center_end_position_and_translation(self, object_position_base, center_radian, forward_or_down):
        center_rotation = R.from_euler('z', center_radian).as_matrix()

        if forward_or_down == "down":
            tcp2end_translation_base = self.end2base_down_rotation @ self.tcp2end_down_translation
            center_tcp2end_translation_base = center_rotation @ tcp2end_translation_base
        else:
            tcp2end_translation_base = self.end2base_forward_rotation @ self.tcp2end_forward_translation
            center_tcp2end_translation_base = center_rotation @ tcp2end_translation_base
        
        center_end_position_base = object_position_base - center_tcp2end_translation_base
        return center_end_position_base, center_tcp2end_translation_base
    
    def get_center_end_rotvec(self, end_rotvec, center_radian):
        center_rotation = R.from_euler('z', center_radian).as_matrix()
        end_rotation = R.from_rotvec(end_rotvec).as_matrix()

        center_end_rotation = center_rotation @ end_rotation
        center_end_rotvec = R.from_matrix(center_end_rotation).as_rotvec()
        return center_end_rotvec
    
    def keep_save_distance_down(self, garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose):
        # 计算 garsp_tpose 和 最低高度 0.179 的差值，并且把这个差值加到 garsp_tpose、save_garsp_tpose、save_forward_garsp_tpose
        # 保证机械臂在抓取物体的时候不会碰到物体
        garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose = copy.deepcopy(garsp_tpose), copy.deepcopy(save_garsp_tpose), copy.deepcopy(save_forward_garsp_tpose)

        high_diff = 0.178 - garsp_tpose[2]
        if high_diff > 0:
            garsp_tpose[2] += high_diff
            save_garsp_tpose[2] += high_diff
            save_forward_garsp_tpose[2] += high_diff
        return garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose


    
    def change_tpose_high(self, tpose, offset):
        tpose = copy.deepcopy(tpose)
        tpose[2] += offset
        return tpose
    # 以下是新加的函数    
    def pose_trans(self, pose):
        """6D pose 和 4x4 transformation matrix 之间的转换"""
        if isinstance(pose, np.ndarray) and pose.shape == (6,):
            x, y, z, rx, ry, rz = pose
            R_x = np.array([[1, 0, 0],
                            [0, np.cos(rx), -np.sin(rx)],
                            [0, np.sin(rx), np.cos(rx)]])
            
            R_y = np.array([[np.cos(ry), 0, np.sin(ry)],
                            [0, 1, 0],
                            [-np.sin(ry), 0, np.cos(ry)]])
            
            R_z = np.array([[np.cos(rz), -np.sin(rz), 0],
                            [np.sin(rz), np.cos(rz), 0],
                            [0, 0, 1]])
            
            R = R_z @ R_y @ R_x
            T = np.eye(4)
            T[:3, :3] = R
            T[:3, 3] = [x, y, z]
            return T
        elif isinstance(pose, np.ndarray) and pose.shape == (4, 4):
            T = pose
            x, y, z = T[:3, 3]
            R = T[:3, :3]
            rx = np.arctan2(R[2, 1], R[2, 2])
            ry = np.arctan2(-R[2, 0], np.sqrt(R[2, 1]**2 + R[2, 2]**2))
            rz = np.arctan2(R[1, 0], R[0, 0])
            return np.array([x, y, z, rx, ry, rz])
        else:
            raise ValueError("Input must be a 6D pose or a 4x4 transformation matrix")

    def pose_distance(self, matrix1, matrix2):
        position_weight=1.0
        angle_weight=10.0
        
        # 计算位置的欧氏距离
        position_distance = np.linalg.norm(matrix1[:3, 3] - matrix2[:3, 3])
        
        # 计算旋转矩阵的角度差
        rotation1 = R.from_matrix(matrix1[:3, :3])
        rotation2 = R.from_matrix(matrix2[:3, :3])
        relative_rotation = rotation1.inv() * rotation2
        angle_distance = relative_rotation.magnitude()
        
        # 综合距离
        combined_distance = position_weight * position_distance + angle_weight * angle_distance
        return combined_distance

    def get_latest_folder(self):
        """
        获取指定目录下最新创建的子文件夹路径。

        参数:
            parent_dir (str): 父目录路径。

        返回:
            str: 最新创建的子文件夹的路径。如果不存在子文件夹，则返回 None。
        """
        # 获取目录下所有子文件夹
        subfolders = [f.path for f in os.scandir("/home/airs/Airs/project/module_based_dexterous_grasp_paper/logs") if f.is_dir()]
        
        if not subfolders:
            print("指定目录下没有任何子文件夹。")
            return None

        # 按子文件夹的创建时间进行排序，并获取最新的文件夹
        latest_folder = max(subfolders, key=os.path.getctime)
        return latest_folder
    
    def draw_obj_frame(self, T_obj, cameraMatrix, img):
        T_camera2base = np.eye(4)
        T_camera2base[:3, :3] = self.camera2base_rotation
        T_camera2base[:3, 3] = self.camera2base_translation
        T_obj2camera = np.dot(np.linalg.inv(T_camera2base), T_obj)
        distCoeffs = np.zeros((5, 1)) # 假设没有畸变 # 假设相机的外参（旋转向量rvec和平移向量tvec）
        rotation_matrix = T_obj2camera[:3, :3]  # 提取旋转矩阵
        rvec, _ = cv2.Rodrigues(rotation_matrix)  # 转换为旋转向量
        # rvec = np.array([0.0,0.0,0.0])
        tvec = T_obj2camera[:3, 3]
        # tvec = np.array([0.0,0.0,0.4])
        # 绘制坐标轴，长度为10
        cv2.drawFrameAxes(img, cameraMatrix, distCoeffs, rvec, tvec, 10)
        # 显示图像
        cv2.imshow('Image with Axes', img)
        cv2.imread(self.get_latest_folder() + "/object_frame.jpg")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    
    def project_point_to_image(self, image_path, point, R, t, K, output_path):
        """
        将基坐标系下的3D点投影到相机图片上，并保存结果图像。
        
        参数:
            image_path (str): 输入图片路径。
            point (array): 基坐标系下的3D点 [X, Y, Z]。
            R (array): 相机外参的旋转矩阵 (3x3)。
            t (array): 相机外参的平移向量 (3x1)。
            K (array): 相机内参矩阵 (3x3)，包含焦距和光心。
            output_path (str): 保存结果图像的路径。
        返回:
            None
        """
        # 读取输入图像
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("输入的图片路径无效，无法读取图片。")
        
        # 将3D点从基坐标系转换到相机坐标系
        point_base = np.array(point).reshape(3, 1)  # 3D点，形状为 (3, 1)
        t = np.array(t).reshape(3, 1)
        point_camera = R @ point_base + t          # 3D点在相机坐标系下的坐标
        
        # 使用内参矩阵将3D点投影到2D图像平面
        X, Y, Z = point_camera.flatten()  # 展开坐标
        if Z <= 0:
            raise ValueError("3D点在相机后方，无法投影到图像平面上。")
        
        # 投影公式： u = fx * X / Z + cx, v = fy * Y / Z + cy
        u = (K[0, 0] * X) / Z + K[0, 2]
        v = (K[1, 1] * Y) / Z + K[1, 2]
        
        # 将结果四舍五入为整数像素坐标
        u, v = int(round(u)), int(round(v))
        
        # 在图像上标记点
        image_height, image_width = image.shape[:2]
        if 0 <= u < image_width and 0 <= v < image_height:
            # 使用红色圆圈标记点
            cv2.circle(image, (u, v), radius=5, color=(0, 0, 255), thickness=-1)
            # 保存结果图像
            cv2.imwrite(output_path, image)
            print(f"点投影到图像上的坐标为: ({u}, {v})")
            print(f"结果图像已保存到: {output_path}")
        else:
            print("投影点超出图像边界，未标记。")

    def generate_candidates(self, st_grasp_pose: np.ndarray, T_object: np.ndarray) -> List[np.ndarray]:  
        """
        输入相对pose和物体在该坐标系下的transformation matrix, 输出采样后的pose组成的list（基坐标系下）
        采样方法：在相对pose和镜像相对pose的基础上，对rz进行均匀采样，得到候选pose
        """
        if not isinstance(st_grasp_pose, np.ndarray) or st_grasp_pose.shape != (6,):
            raise ValueError("Input pose must be a numpy array of shape (6,)")
        
        # 将st_grasp_pose绕物体坐标系的z轴旋转180度
        rotated_pose = st_grasp_pose.copy()
        rotated_pose[5] += np.pi 
        rotated_pose[5] = (rotated_pose[5] + np.pi) % (2 * np.pi) - np.pi
        
        candidates = []
        offsets = np.linspace(-0.1745, 0.1745, 10) #+-10*pi/180 采样范围
        for rz_offsets in offsets:
            candidate_pose = st_grasp_pose.copy()
            candidate_pose[5] += rz_offsets
            candidate_T2obj = self.pose_trans(candidate_pose)
            candidate_T2base = T_object @ candidate_T2obj
            candidates.append(candidate_T2base)
        for rz_offsets in offsets:
            candidate_pose = rotated_pose.copy()
            candidate_pose[5] += rz_offsets
            candidate_T2obj = self.pose_trans(candidate_pose)
            candidate_T2base = T_object @ candidate_T2obj
            candidates.append(candidate_T2base)
        print(f"Generated {len(candidates)} candidates")
        return candidates # transformation matrix in base frame

    def candidates_filter(self, candidates, st_grasp_pose, T_object): # origin_radian这里要保证主函数传的还是z_axis_radian
        """
        输入：采样后的pose组成的list
        输出：最佳pose
        1. 判断每个candidate是否都存在逆运动学解，没有的就被筛掉
        2. 判断每个candidate是否满足自避碰约束(经验值），没有的就被筛掉
        3. 从筛除后的candidate当中，选最接近st_grasp_pose的那个
        """
        #  1. 判断每个candidate是否都存在逆运动学解，没有的被筛掉
        candidates_after_ik = []
        num_candidates_after_ik = 0
        for T in candidates:
            try :
                IKSolver().inv_kin(T, arm_motion_params.tcp_save_place_joint_position) 
                candidates_after_ik.append(T)
                num_candidates_after_ik += 1
            except:
                continue
        print(f"Filtered by IK: {num_candidates_after_ik} candidates left and {len(candidates) - num_candidates_after_ik} candidates filtered")
        if num_candidates_after_ik == 0:
            raise ValueError("No candidates left after IK filtering") # 提供接口，回到初始位置
        
        # 2. 判断每个candidate是否满足自避碰约束(经验值），没有的就被筛掉
        # base_rotation_radian = np.arctan2(T_object[0, 3], T_object[1, 3])# 基座转动角度
        # base_rotation_matrix_base = R.from_euler('z', base_rotation_radian).as_matrix()
        # distance_from_object_to_base = np.linalg.norm(T_object[:2, 3])
        # candidates_after_constraint = []
        # for T in candidates_after_ik:
        #     align_end_rotation = T[:3, :3]  # 提取旋转部分 (3x3)
        #     align_rotation = align_end_rotation @ base_rotation_matrix_base @ np.linalg.inv(align_end_rotation)
        #     align_radian = np.arctan2(align_rotation[1, 0], align_rotation[0, 0])
        #     max_angle = (0.8 - distance_from_object_to_base) * 30 + 40 # 将 align_radian 最大值限制在 distance 为 0.8 时设置为 40度和 distance 为 0.5 是设置为 50度的线性空间中
        #     if align_radian < max_angle / 180 * np.pi:
        #         candidates_after_constraint.append(T)
        #     else:
        #         continue
        # print(f"Filtered by constraint: {len(candidates_after_constraint)} candidates left and {len(candidates_after_ik) - len(candidates_after_constraint)} candidates filtered")
        # if len(candidates_after_constraint) == 0:
        #     raise ValueError("No candidates left after constraint filtering") # 提供接口，回到初始位置
            
        # 3. 从筛除后的candidate当中，选最接近st_greshaperasp_pose的那个
        dist_matrix_pair = {}
        for T in candidates_after_ik:
            candidates2obj = np.dot(T, np.linalg.inv(T_object))
            st_grasp_T = self.pose_trans(st_grasp_pose)
            dist = self.pose_distance(candidates2obj, st_grasp_T)
            dist_matrix_pair[dist] = T
        min_dist = min(dist_matrix_pair.keys())
        best_candidate = dist_matrix_pair[min_dist] # transformation matrix in base frame
        best_candidate = self.pose_trans(best_candidate) # 6D pose in base frame

        tcp_translation = np.array([0.00973, -0.03662, 0.18595])
        translation_base_to_end = best_candidate[:3]
        rotation_base_to_end = R.from_euler('xyz', best_candidate[3:])  # Create rotation object
        best_candidate_tcp = (
            rotation_base_to_end.apply(tcp_translation) + translation_base_to_end
        ) # TCP position in base frame
        self.project_point_to_image(self.get_latest_folder() + "/captured_image.jpg", 
                                    best_candidate_tcp, 
                                    self.camera2base_rotation, 
                                    self.camera2base_translation, 
                                    self.K, 
                                    self.get_latest_folder() + "/projected_image.jpg")
                                    
        print(f"Best candidate distance: {min_dist}\n Best candidate: {best_candidate}\n Best TCP candidate : {best_candidate_tcp}")
        
        return best_candidate # transformation matrix in base frame


    def plan_path(self, obj_cam_position: list, origin_radian: float, T_obj:np.array):
        # Implementation for planning the robotic arm's path
        # 输入：基于camera的3D position，基于camera的2D的物体的偏转角
        # 输出：3个tpose(x,y,z,rx,ry,rz)

        object_position_base = self.get_target_base_coordinate(obj_cam_position)# 物体在base坐标系下的位置
        center_radian = np.arctan(object_position_base[0] / object_position_base[1]) # 机器人基座的旋转角度
        # self.logger_manager.logger.info(f"x-y distance from object to base: {np.linalg.norm(object_position_base[:2])})")
        forward_or_down, align_radian = self.dhp.get_hand_grasp_strategy(origin_radian, obj_cam_position) # 机器人手的方向，string
        
        center_end_position_base, center_tcp2end_translation_base = self.get_center_end_position_and_translation(
            object_position_base, -center_radian, forward_or_down) # 计算物体在tcp坐标系下的位置和tcp坐标系下的translation，tcp2end_translation_base
        end_rotvec = self.down_hand_rotvec if forward_or_down == "down" else self.forward_hand_rotvec
        center_end_rotvec = self.get_center_end_rotvec(end_rotvec, -center_radian)

        standard_relative_pose_pairs_6d = self.pose_trans(self.standard_relative_pose_pairs["screwdriver"]) #根据实际序列决定
        candidates = self.generate_candidates(standard_relative_pose_pairs_6d, T_obj)
        align_end_pose = self.candidates_filter(candidates, standard_relative_pose_pairs_6d, T_obj)

        center_end_pose = np.concatenate([center_end_position_base, center_end_rotvec])
        higher_center_end_pose = self.change_tpose_high(center_end_pose, self.grasp_safe_distance) # 物体上方，转动前的 tcp pose
        higher_align_end_pose = self.change_tpose_high(align_end_pose, self.grasp_safe_distance/2) # 物体上方，转动后的 tcp pose
 
        keep_save_distance = self.keep_save_distance_down
        align_end_pose, higher_align_end_pose, higher_center_end_pose = keep_save_distance(align_end_pose, higher_align_end_pose, higher_center_end_pose)
        
        return {"higher_center_end_pose": higher_center_end_pose, "higher_align_end_pose": higher_align_end_pose, "align_end_pose": align_end_pose}
    
    # to be deleted
    def _make_radian_in_range(self, radian):
        while radian <= -np.pi/2 or radian > np.pi/2:
            if radian > np.pi/2:
                radian -= np.pi
            elif radian <= -np.pi/2:
                radian += np.pi
        return radian

    def _keep_save_distance_forward(self, garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose):
        # 计算 garsp_tpose 和 最低高度 0.179 的差值，并且把这个差值加到 garsp_tpose、save_garsp_tpose、save_forward_garsp_tpose
        # 保证机械臂在抓取物体的时候不会碰到物体
        garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose = copy.deepcopy(garsp_tpose), copy.deepcopy(save_garsp_tpose), copy.deepcopy(save_forward_garsp_tpose)

        high_diff = 0.102 - garsp_tpose[2]
        if high_diff > 0:
            garsp_tpose[2] += high_diff
            save_garsp_tpose[2] += high_diff
            save_forward_garsp_tpose[2] += high_diff
        return garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose


class FrankaArmPlanner:

    def __init__(self):
        # self.T_G_E = []
        # self.T_C_E = []   
        # # self.T_E_B = []
        self.T_O_C = []
        pass

    def plan(self, P_O_C,R, T_C_E, T_E_B):
        """
        Input:
        Position : P_O_C[x, y, z], Z-axis rotation: R_O_C
        Output:
        Sequence of tposes to reach the target position
            Data_Structure:
            Include tpose and gripper state
        """
        # 首先，将P_O_C转换为齐次坐标

        P_O_C_homogeneous = np.array([P_O_C[0], P_O_C[1], P_O_C[2], 1]).reshape(4, 1)

        # 计算物体相对于基座的位置P_O_B
        P_O_B = np.dot(T_E_B, np.dot(T_C_E, P_O_C_homogeneous))[:3, 0]

        # R = 1.7
        # P_O_B = np.array([0.4, 0.1, -0.02])

        # 创建绕y轴旋转180度（pi弧度）的旋转矩阵
        rotation_matrix_y = np.array([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, -1]
        ])

        # 创建绕z轴旋转R弧度的旋转矩阵
        rotation_matrix_z = np.array([
            [np.cos(R), -np.sin(R), 0],
            [np.sin(R), np.cos(R), 0],
            [0, 0, 1]
        ])

        # 将两个旋转矩阵相乘
        rotation_matrix = np.dot(rotation_matrix_y, rotation_matrix_z)

        # z = 0.05
        # x = 0.04
        # y = 0.03
        P_O_B[0] += x
        P_O_B[1] += y
        P_O_B[2] -= z
        # 构建4x4的变换矩阵
        pose_matrix = np.eye(4)
        pose_matrix[:3, :3] = rotation_matrix
        pose_matrix[:3, 3] = P_O_B
        return pose_matrix
        # pass

    def rotation_matrix_to_quaternion(self, rotation_matrix):
        """
        将旋转矩阵转换为四元数。
        """
        rotation = R_cal.from_matrix(rotation_matrix)
        quaternion = rotation.as_quat()
        return quaternion
    
    def get_translation_and_rotation(self, P_O_C, R, T_C_E, T_E_B):
        # 首先，将P_O_C转换为齐次坐标

        P_O_C_homogeneous = np.array([P_O_C[0], P_O_C[1], P_O_C[2], 1]).reshape(4, 1)

        # 计算物体相对于基座的位置P_O_B
        P_O_B = np.dot(T_E_B, np.dot(T_C_E, P_O_C_homogeneous))[:3, 0]

        # 创建绕y轴旋转180度（pi弧度）的旋转矩阵
        rotation_matrix_y = np.array([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, -1]
        ])

        # 创建绕z轴旋转R弧度的旋转矩阵
        rotation_matrix_z = np.array([
            [np.cos(R), -np.sin(R), 0],
            [np.sin(R), np.cos(R), 0],
            [0, 0, 1]
        ])

        # 将两个旋转矩阵相乘
        rotation_matrix = np.dot(rotation_matrix_y, rotation_matrix_z)

        # rotation = R_cal.from_matrix(rotation_matrix)
        rotation = self.rotation_matrix_to_quaternion(rotation_matrix_y)
        translation = P_O_B
        return translation, rotation

    def adjust_grasp_angle(self, q_solution, R):
        # 调整 grasp 角度
        q_solution[6] = R
        return q_solution
    def plan_curobo(self, P_O_C, R, T_C_E, T_E_B):
        # Third Party
        import torch

        # cuRobo
        from curobo.types.base import TensorDeviceType
        from curobo.types.math import Pose
        from curobo.types.robot import RobotConfig
        from curobo.util_file import get_robot_configs_path, join_path, load_yaml
        from curobo.wrap.reacher.ik_solver import IKSolver, IKSolverConfig


        tensor_args = TensorDeviceType()

        config_file = load_yaml(join_path(get_robot_configs_path(), "franka.yml"))
        urdf_file = config_file["robot_cfg"]["kinematics"][
            "urdf_path"
        ]  # Send global path starting with "/"
        base_link = config_file["robot_cfg"]["kinematics"]["base_link"]
        ee_link = config_file["robot_cfg"]["kinematics"]["ee_link"]
        robot_cfg = RobotConfig.from_basic(urdf_file, base_link, ee_link, tensor_args)

        ik_config = IKSolverConfig.load_from_robot_config(
            robot_cfg,
            None,
            rotation_threshold=0.05,
            position_threshold=0.005,
            num_seeds=20,
            self_collision_check=False,
            self_collision_opt=False,
            tensor_args=tensor_args,
            use_cuda_graph=True,
        )
        ik_solver = IKSolver(ik_config)

        # q_sample = ik_solver.sample_configs(5000)#七个关节角度
        # q_sample_single = q_sample[0]

        # kin_state = ik_solver.fk(q_sample)
        # kin_state_single = ik_solver.fk(q_sample_single)

        # goal = Pose(kin_state.ee_position, kin_state.ee_quaternion)
        translation, rotation = self.get_translation_and_rotation(P_O_C, R, T_C_E, T_E_B)
        translation_tensor = torch.tensor(translation, device=tensor_args.device, dtype=tensor_args.dtype)
        rotation_tensor = torch.tensor(rotation, device=tensor_args.device, dtype=tensor_args.dtype)
        goal = Pose(translation_tensor, rotation_tensor)

        # result = ik_solver.solve_batch(goal)
        result_single = ik_solver.solve_batch(goal)

        # q_solution = result.solution[result.success]
        q_solution = result_single.solution[result_single.success]
        
        # 将tensor转为list
        q_solution = q_solution.tolist()[0]

        q_solution = self.adjust_grasp_angle(q_solution,R)
        return q_solution


        # R = 1.7
        # P_O_B = np.array([0.4, 0.1, -0.02])



        # z = 0.09
        # x = 0.04
        # y = 0.03
        # P_O_B[0] += x
        # P_O_B[1] += y
        # P_O_B[2] -= z
        # # 构建4x4的变换矩阵
        # pose_matrix = np.eye(4)
        # pose_matrix[:3, :3] = rotation_matrix
        # pose_matrix[:3, 3] = P_O_B
        # return pose_matrix