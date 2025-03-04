import numpy as np
import torch
from scipy.spatial.transform import Rotation as R_cal
# Third Party
"""
因为panda_py库求解能力不行，所以使用curobo库进行求解
"""
# cuRobo
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import RobotConfig
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.ik_solver import IKSolver, IKSolverConfig

class FrankaArmPlanner:

    def __init__(self):
        pass

    def rotation_matrix_to_quaternion(self, rotation_matrix):
        """
        将旋转矩阵转换为四元数。
        """
        rotation = R_cal.from_matrix(rotation_matrix)
        quaternion = rotation.as_quat()
        return quaternion
    
    def get_translation_and_rotation(self, P_O_C, R, T_C_E, T_E_B):
        """
        根据给定的参数计算物体相对于基座的位置P_O_B和旋转。
        """
        P_O_C_homogeneous = np.array([P_O_C[0], P_O_C[1], P_O_C[2], 1]).reshape(4, 1)# 首先，将P_O_C转换为齐次坐标
        P_O_B = np.dot(T_E_B, np.dot(T_C_E, P_O_C_homogeneous))[:3, 0]# 计算物体相对于基座的位置P_O_B

        rotation_matrix = np.array([
            [-1, 0, 0],
            [0, 1, 0],
            [0, 0, -1]
        ])        # 创建绕y轴旋转180度（pi弧度）的旋转矩阵

        rotation = self.rotation_matrix_to_quaternion(rotation_matrix)
        translation = P_O_B
        return translation, rotation

    def curobo_process(self, P_O_C,T_C_E, T_E_B):
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

        translation, rotation = self.get_translation_and_rotation(P_O_C, R, T_C_E, T_E_B)
        translation_tensor = torch.tensor(translation, device=tensor_args.device, dtype=tensor_args.dtype)
        rotation_tensor = torch.tensor(rotation, device=tensor_args.device, dtype=tensor_args.dtype)
        goal = Pose(translation_tensor, rotation_tensor)

        result_single = ik_solver.solve_batch(goal)
        q_solution = result_single.solution[result_single.success]
        
        # 将tensor转为list
        q_solution = q_solution.tolist()[0]
        return q_solution
    
    def plan_curobo(self, P_O_C, R, T_C_E, T_E_B,initial_angle_gap):
        """
        根据给定的参数计算机械臂的7个关节角度。curobo负责前6个关节，第7个关节由estimation给到的R调整
        """
        q_solution = self.curobo_process(P_O_C, T_C_E, T_E_B)

        target_ee_angle = R + initial_angle_gap
        q_solution[6] = target_ee_angle # 调整末端法兰盘的角度

        return q_solution
