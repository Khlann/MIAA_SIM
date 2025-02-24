import numpy as np
from collections import namedtuple
from scipy.spatial.transform import Rotation as R


def compute_end2T(T2base, end2base_pose):
    """
    计算机械臂末端相对于物体坐标系的4x4变换矩阵。
    
    参数：
    screwdriver_T2base (np.ndarray): 物体坐标系相对于基坐标系的4x4变换矩阵。
    screwdriver_end2base (np.ndarray): 机械臂末端相对于基坐标系的6D姿势数组 (x, y, z, rx, ry, rz)。

    返回：
    np.ndarray: 机械臂末端相对于物体坐标系的4x4变换矩阵。
    """
    # 从6D姿势生成机械臂末端相对于基坐标系的4x4变换矩阵
    def pose_to_transformation_matrix(pose):
        x, y, z, rx, ry, rz = pose
        rotation = R.from_euler('xyz', [rx, ry, rz])
        R_matrix = rotation.as_matrix()
        T = np.eye(4)
        T[:3, :3] = R_matrix
        T[:3, 3] = [x, y, z]
        return T

    end2base = pose_to_transformation_matrix(end2base_pose)
    T2base_inv = np.linalg.inv(T2base)
    end2T = np.dot(T2base_inv, end2base)
    
    return end2T

# Define namedtuples for camera and pose configurations
RotationTranslation = namedtuple('RotationTranslation', ['rotation', 'translation'])
PoseConfiguration = namedtuple('PoseConfiguration', ['end_rotvec', 'end_rotation_matrix', 'grasp_point_translation', 'rotation_offset', 'min_height'])
DexterousHandGraspConfiguration = namedtuple('DexterousHandGraspConfiguration', ['forward_pose', 'down_pose'])
StandardRelativePosePairs = namedtuple('StandardRelativePosePairs', ['standard_relative_pose_pairs_dict'])

 #Camera to base transformation
end2camera = RotationTranslation(
    rotation=np.array([
        [-0.99928889,  0.03515113, -0.01364238],
        [ 0.01268125, -0.02742233, -0.9995435 ],
        [-0.03550919, -0.99900571,  0.02695707],
        
    ]),
    translation=np.array([0.04150159, -0.04781294, 0.03821502])
)

# Camera to base transformation

camera2base = RotationTranslation(
    rotation=np.array([[-0.99920647, 0.03101367, -0.02499168],
               [0.03170615, 0.99911038, -0.02780593],
               [0.02410709, -0.02857626, -0.99930088]]),
    translation=np.array([-0.09486684, -0.5677745, 0.34250334])
)

shot_pose=[0.01117,-0.45764,0.38532,1.596,-0.113,-0.145]

# Forward pose configuration
forward_rotvec = [1.761, -0.407, 0.373]
forward_pose = PoseConfiguration(
    end_rotvec=forward_rotvec,
    end_rotation_matrix=R.from_rotvec(forward_rotvec).as_matrix(),  # Now we correctly use forward_rotvec
    grasp_point_translation=np.array([0.022, -0.04, 0.1718]),
    rotation_offset=-np.pi / 3 + (15 / 180 * np.pi),
    min_height=0.102
)

# Down pose configuration
down_rotvec = [2.189, 0.358, 0.136]
down_pose = PoseConfiguration(
    end_rotvec=down_rotvec,
    end_rotation_matrix=R.from_rotvec(down_rotvec).as_matrix(),  # Now we correctly use down_rotvec
    grasp_point_translation=np.array([0.00973, -0.03662, 0.18595]),
    rotation_offset=np.pi / 2,
    min_height=0.178
)

# Dexterous hand grasp configuration combining both forward and down poses
dexterous_hand_grasp_pose = DexterousHandGraspConfiguration(
    forward_pose=forward_pose,
    down_pose=down_pose
)

# Grasp safe distance
grasp_safe_distance = 0.08

# Relative poses of different objects
# standard_relative_pose_pairs = StandardRelativePosePairs(
#     pairs_dict = {"bottle":np.array([0.1,0,0,1.0,0,0])}
#     )

# origin log of T and pose
screwdriver_T2base = np.array([[ 0.8121345  ,0.58341058,  0.00834531, -0.03038252],
 [ 0.58340777, -0.81175511, -0.02624881, -0.36465443],
 [-0.00853948 , 0.02618628 ,-0.99962061, -0.08969113],
 [ 0. ,         0. ,         0. ,         1.        ]])
screwdriver_end2base_pose = np.array([0.06133, -0.42268, 0.13600, 2.281, -0.150, -0.168])
screwdriver_end2T = compute_end2T(screwdriver_T2base, screwdriver_end2base_pose)

# Relative poses of different objects
standard_relative_pose_pairs = StandardRelativePosePairs(standard_relative_pose_pairs_dict = {
                                                          "screwdriver": screwdriver_end2T
                                                        })

# Camera intrinsic matrix
camera_intrinsic_matrix = np.array([
    [1367.24, 0.0, 984.708],
    [0.0, 1366.53, 550.043],
    [0.0, 0.0, 1.0]
])