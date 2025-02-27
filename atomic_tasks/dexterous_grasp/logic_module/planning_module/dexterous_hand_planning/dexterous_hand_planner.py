import numpy as np

from dexterous_grasp.logger_module import LoggerValidator
from dexterous_grasp.utils.common import object_position_cam2base, make_radian_in_range


def calculate_hand_radian(object_radian, offset):
    """Calculate and return the hand radian with a specific offset, ensuring it's in the valid range."""
    hand_radian = object_radian + offset
    return make_radian_in_range(hand_radian)


class DexterousHandPlanner(LoggerValidator):
    def __init__(self, camera2base, dexterous_hand_grasp_pose, logger_manager=None):
        super().__init__(logger_manager)
        self.camera2base = camera2base
        self.dexterous_hand_grasp_pose = dexterous_hand_grasp_pose

    def get_hand_grasp_strategy(self, origin_radian, object_position_cam):
        # Calculate the object's position in the base coordinate system
        object_position_base = object_position_cam2base(
            object_position_cam[0], object_position_cam[1], object_position_cam[2],
            self.camera2base.rotation, self.camera2base.translation
        )
        distance_from_object_to_base = np.linalg.norm(object_position_base[:2])

        # Calculate the base rotation and adjust the object's radian
        base_rotation_radian = np.arctan2(object_position_base[0], object_position_base[1])
        center_radian = make_radian_in_range(origin_radian + base_rotation_radian)

        # Calculate hand radians for forward and downward strategies
        forward_hand_radian = calculate_hand_radian(center_radian,
                                                    self.dexterous_hand_grasp_pose.forward_pose.rotation_offset)
        down_hand_radian = calculate_hand_radian(center_radian,
                                                 self.dexterous_hand_grasp_pose.down_pose.rotation_offset)
        self.logger_manager.logger.info(
            f"Center radian: {center_radian:.4f}, Forward hand radian: {forward_hand_radian:.4f}, Down hand radian: {down_hand_radian:.4f}")

        # Determine whether to grasp forward or downward based on which radian is smaller
        if abs(forward_hand_radian) < abs(down_hand_radian):
            grasp_strategy = "forward"
            align_radian = forward_hand_radian
            # 将 align_radian 限制在 -70° 到 50° 之间
            align_radian = min(max(align_radian, -70 / 180 * np.pi), 50 / 180 * np.pi)
        else:
            grasp_strategy = "down"
            align_radian = down_hand_radian
            # 将 align_radian 最大值限制在 distance 为 0.8 时设置为 40度和 distance 为 0.5 是设置为 50度的线性空间中
            max_angle = (0.8 - distance_from_object_to_base) * 30 + 40
            align_radian = min(align_radian, max_angle / 180 * np.pi)


        # Log the grasp strategy and rotation in a readable format
        self.logger_manager.logger.info(
            f"Grasp strategy: {grasp_strategy}, align rotation (radian): {align_radian:.4f} "
            f"(degree): {np.degrees(align_radian):.2f}")

        return grasp_strategy, align_radian
