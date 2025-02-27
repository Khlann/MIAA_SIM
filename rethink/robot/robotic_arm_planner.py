import numpy as np
import copy
from scipy.spatial.transform import Rotation as R



class RoboticArmPlanner():
    def __init__(self, camera2base, dexterous_hand_grasp_pose, grasp_safe_distance, logger_manager=None):
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


    def make_radian_in_range(self, radian):
        while radian <= -np.pi/2 or radian > np.pi/2:
            if radian > np.pi/2:
                radian -= np.pi
            elif radian <= -np.pi/2:
                radian += np.pi
        return radian
    
    def get_target_base_coordinate(self, object_position_cam):
        object_position_base = self.camera2base_rotation @ object_position_cam + self.camera2base_translation
        try:
            x_base, y_base, z_base = object_position_base[0][0], object_position_base[0][1], object_position_base[0][2]
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

    def keep_save_distance_forward(self, garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose):
        # 计算 garsp_tpose 和 最低高度 0.179 的差值，并且把这个差值加到 garsp_tpose、save_garsp_tpose、save_forward_garsp_tpose
        # 保证机械臂在抓取物体的时候不会碰到物体
        garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose = copy.deepcopy(garsp_tpose), copy.deepcopy(save_garsp_tpose), copy.deepcopy(save_forward_garsp_tpose)

        high_diff = 0.102 - garsp_tpose[2]
        if high_diff > 0:
            garsp_tpose[2] += high_diff
            save_garsp_tpose[2] += high_diff
            save_forward_garsp_tpose[2] += high_diff
        return garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose
    
    def change_tpose_high(self, tpose, offset):
        tpose = copy.deepcopy(tpose)
        tpose[2] += offset
        return tpose


    def plan_path(self, object_position_cam: list, origin_radian):
        # Implementation for planning the robotic arm's path
        # 输入：基于camera的3D position，基于camera的2D的物体的偏转角
        # 输出：3个tpose(x,y,z,rx,ry,rz)

        object_position_base = self.get_target_base_coordinate(object_position_cam)# 物体在base坐标系下的位置
        center_radian = np.arctan(object_position_base[0] / object_position_base[1]) # 机器人基座的旋转角度
        forward_or_down, align_radian = self.dhp.get_hand_grasp_strategy(origin_radian, object_position_cam) # 机器人手的方向，string
        
        center_end_position_base, center_tcp2end_translation_base = self.get_center_end_position_and_translation(
            object_position_base, -center_radian, forward_or_down) # 计算物体在tcp坐标系下的位置和tcp坐标系下的translation，tcp2end_translation_base
        end_rotvec = self.down_hand_rotvec if forward_or_down == "down" else self.forward_hand_rotvec
        center_end_rotvec = self.get_center_end_rotvec(end_rotvec, -center_radian)

        center_tcp_position_base = center_end_position_base + center_tcp2end_translation_base
        align_rotation = R.from_euler('z', align_radian).as_matrix()
        center_end_rotation = R.from_rotvec(center_end_rotvec).as_matrix()
        align_end_rotation = align_rotation @ center_end_rotation
        align_tcp2end_translation_base = align_rotation @ center_tcp2end_translation_base
        align_end_position_base = center_tcp_position_base - align_tcp2end_translation_base
        align_enc_rotvec = R.from_matrix(align_end_rotation).as_rotvec()

        align_end_pose = np.concatenate([align_end_position_base, align_enc_rotvec]) # 即将抓取物体的tcp pose

        center_end_pose = np.concatenate([center_end_position_base, center_end_rotvec])
        higher_center_end_pose = self.change_tpose_high(center_end_pose, self.grasp_safe_distance) # 物体上方，转动前的 tcp pose
        higher_align_end_pose = self.change_tpose_high(align_end_pose, self.grasp_safe_distance/2) # 物体上方，转动后的 tcp pose
 

        if forward_or_down == "down":
            keep_save_distance = self.keep_save_distance_down
        else:
            keep_save_distance = self.keep_save_distance_forward

        align_end_pose, higher_align_end_pose, higher_center_end_pose = keep_save_distance(align_end_pose, higher_align_end_pose, higher_center_end_pose)
        
        return {"higher_center_end_pose": higher_center_end_pose, "higher_align_end_pose": higher_align_end_pose, "align_end_pose": align_end_pose}

    def obj2cam(self, position, radian):
        object_position_base = self.get_target_base_coordinate(position)# 物体在base坐标系下的位置