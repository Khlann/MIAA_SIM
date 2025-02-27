import numpy as np

class FrankaArmPlanner:

    def __init__(self):
        # self.T_G_E = []
        # self.T_C_E = []   
        # # self.T_E_B = []
        self.T_O_C = []
        pass

    def plan(self, P_O_C, R, T_C_E, T_E_B):
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
        # 构建4x4的变换矩阵
        pose_matrix = np.eye(4)
        pose_matrix[:3, :3] = rotation_matrix
        pose_matrix[:3, 3] = P_O_B

        pass