# Unit tests for dexterous hand planning
import unittest
import numpy as np
import copy
from scipy.spatial.transform import Rotation as R

from dexterous_grasp.logic_module.control_module import RoboticArmController
from dexterous_grasp.logic_module.planning_module import RoboticArmPlanner
from dexterous_grasp.config import (
    robot_arm_ip_address,
    arm_motion_params,
    camera2base, 
    dexterous_hand_grasp_pose, 
    grasp_safe_distance
)

def make_radian_in_range(radian):
        while radian <= -np.pi/2 or radian > np.pi/2:
            if radian > np.pi/2:
                radian -= np.pi
            elif radian <= -np.pi/2:
                radian += np.pi
        return radian
    
def get_target_base_coordinate(target_x_3d, target_y_3d, target_z_3d):
    target_position_in_camera = np.array([target_x_3d, target_y_3d, target_z_3d])
    target_position_in_base = camera2base.rotation @ target_position_in_camera + camera2base.translation
    try:
        x_base, y_base, z_base = target_position_in_base[0][0], target_position_in_base[0][1], target_position_in_base[0][2]
    except IndexError as e:
        x_base, y_base, z_base = target_position_in_base[0], target_position_in_base[1], target_position_in_base[2]
    return x_base, y_base, z_base

def get_target_position_in_tcp_with_translation(target_x_base, target_y_base, target_z_base, base_rotation_radian, forward_or_down):
    z_rotation = R.from_euler('z', base_rotation_radian).as_matrix()

    if forward_or_down == "down":
        tcp2base_translation = dexterous_hand_grasp_pose.down_pose.end_rotation_matrix @ dexterous_hand_grasp_pose.down_pose.grasp_point_translation
        after_rotate_tcp2base_translation = z_rotation @ tcp2base_translation
    else:
        tcp2base_translation = dexterous_hand_grasp_pose.forward_pose.end_rotation_matrix @ dexterous_hand_grasp_pose.forward_pose.grasp_point_translation
        after_rotate_tcp2base_translation = z_rotation @ tcp2base_translation

    target_position_in_base = np.array([target_x_base, target_y_base, target_z_base])
    
    after_rotate_target_position_in_tcp = target_position_in_base - after_rotate_tcp2base_translation
    return after_rotate_target_position_in_tcp, after_rotate_tcp2base_translation

def get_tcp_rotvec_by_radian(default_rotvec, radian):
    z_rotation = R.from_euler('z', radian).as_matrix()
    hand_rotation = R.from_rotvec(default_rotvec).as_matrix()

    after_rotate_tcp_rotation = z_rotation @ hand_rotation
    after_rotate_tcp_rotvec = R.from_matrix(after_rotate_tcp_rotation).as_rotvec()
    return after_rotate_tcp_rotvec

def keep_save_distance_down(garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose):
    # 计算 garsp_tpose 和 最低高度 0.179 的差值，并且把这个差值加到 garsp_tpose、save_garsp_tpose、save_forward_garsp_tpose
    # 保证机械臂在抓取物体的时候不会碰到物体
    garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose = copy.deepcopy(garsp_tpose), copy.deepcopy(save_garsp_tpose), copy.deepcopy(save_forward_garsp_tpose)

    high_diff = 0.178 - garsp_tpose[2]
    if high_diff > 0:
        garsp_tpose[2] += high_diff
        save_garsp_tpose[2] += high_diff
        save_forward_garsp_tpose[2] += high_diff
    return garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose

def keep_save_distance_forward(garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose):
    # 计算 garsp_tpose 和 最低高度 0.179 的差值，并且把这个差值加到 garsp_tpose、save_garsp_tpose、save_forward_garsp_tpose
    # 保证机械臂在抓取物体的时候不会碰到物体
    garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose = copy.deepcopy(garsp_tpose), copy.deepcopy(save_garsp_tpose), copy.deepcopy(save_forward_garsp_tpose)

    high_diff = 0.102 - garsp_tpose[2]
    if high_diff > 0:
        garsp_tpose[2] += high_diff
        save_garsp_tpose[2] += high_diff
        save_forward_garsp_tpose[2] += high_diff
    return garsp_tpose, save_garsp_tpose, save_forward_garsp_tpose

def change_tpose_high(tpose, offset):
    tpose = copy.deepcopy(tpose)
    tpose[2] += offset
    return tpose

def plan_path(object_position_cam, grasp_strategy, origin_radian):

    target_position_base = get_target_base_coordinate(object_position_cam[0], object_position_cam[1], object_position_cam[2])# 物体在base坐标系下的位置
    base_rotation_radian = np.arctan(target_position_base[0] / target_position_base[1]) # 机器人基座的旋转角度
    print(f"target_position_base: {target_position_base}")
    print(f"distance from base: {np.linalg.norm(target_position_base[:2])})")
    forward_or_down = grasp_strategy
    z_axis_rotaion_radian = origin_radian
    
    target_x_base, target_y_base, target_z_base = target_position_base
    after_rotate_target_position_in_tcp, tcp2base_translation = get_target_position_in_tcp_with_translation(
        target_x_base, target_y_base, target_z_base, -base_rotation_radian, forward_or_down) # 计算物体在tcp坐标系下的位置和tcp坐标系下的translation，tcp2base_translation
    default_rotvec = dexterous_hand_grasp_pose.down_pose.end_rotvec if forward_or_down == "down" else dexterous_hand_grasp_pose.forward_pose.end_rotvec
    after_rotate_tcp_rotvec = get_tcp_rotvec_by_radian(default_rotvec, -base_rotation_radian)
    endeffector_location_and_rotvec = np.concatenate([after_rotate_target_position_in_tcp, after_rotate_tcp_rotvec])# 计算endeffector_location_and_rotvec
    
    endeffector_3d_location = endeffector_location_and_rotvec[:3]
    hand_rotvec = endeffector_location_and_rotvec[3:]

    endeffector_3d_location = np.array(endeffector_3d_location)
    tcp2base_translation = np.array(tcp2base_translation)

    tcp_3d_location = endeffector_3d_location + tcp2base_translation
    base_z_rotation = R.from_euler('z', z_axis_rotaion_radian).as_matrix()
    hand_rotation = R.from_rotvec(hand_rotvec).as_matrix()
    new_rotation_matrix = base_z_rotation @ hand_rotation
    new_tcp2base_translation = base_z_rotation @ tcp2base_translation
    new_endeffector_3d = tcp_3d_location - new_tcp2base_translation
    new_rotation_vector = R.from_matrix(new_rotation_matrix).as_rotvec()

    grasp_tpose = np.concatenate([new_endeffector_3d, new_rotation_vector]) # 即将抓取物体的tcp pose

    hand_pose = np.concatenate([endeffector_3d_location, hand_rotvec])
    save_forward_grasp_tpose = change_tpose_high(hand_pose, grasp_safe_distance) # 物体上方，转动前的 tcp pose
    save_grasp_tpose = change_tpose_high(grasp_tpose, grasp_safe_distance/2) # 物体上方，转动后的 tcp pose


    if forward_or_down == "down":
        keep_save_distance = keep_save_distance_down
    else:
        keep_save_distance = keep_save_distance_forward

    grasp_tpose, save_grasp_tpose, save_forward_grasp_tpose = keep_save_distance(grasp_tpose, save_grasp_tpose, save_forward_grasp_tpose)
    
    return {"save_forward_grasp_tpose": save_forward_grasp_tpose, "save_grasp_tpose": save_grasp_tpose, "grasp_tpose": grasp_tpose}

class TestTaskControl(unittest.TestCase):
    def setUp(self):
        self.robotic_arm_planner = RoboticArmPlanner(camera2base, dexterous_hand_grasp_pose, grasp_safe_distance)
        self.robotic_arm_controller = RoboticArmController(robot_arm_ip_address, arm_motion_params)

    def test_arm_movel_case0(self):
        self.robotic_arm_controller.execute_movement_joints(arm_motion_params.tcp_save_place_joint_position)
        distance = 0.5
        position_cam = (0.0077632253016593, 0.6222531324155962 - distance, 0.7887500524520874)
        strategy = "down"
        radian = 0 * np.pi / 180
        
        tposes = plan_path(position_cam, strategy, radian)
        tposes = list(tposes.values())
        print(f"使用 arm_planner 计算得到的 tpose_sequence: {tposes}")
        # self.robotic_arm_controller.execute_movement_tposes([target_tpose])
        self.robotic_arm_controller.execute_smooth_movement_tposes(tposes)


if __name__ == '__main__':
    unittest.main()
