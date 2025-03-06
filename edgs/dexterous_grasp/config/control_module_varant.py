import numpy as np
from collections import namedtuple

# Define namedtuples for arm and hand parameters
MotionParams = namedtuple('MotionParams', ['default_acc', 'default_radius', 'tcp_save_place_joint_position', 'tcp_up_on_basket_joint_position'])
HandMotionParams = namedtuple('HandMotionParams', ['speedSet', 'angleSet_execute1', 'angleSet_execute2', 'forceSet', 'tinyforceSet', 'angleSet_abort'])
HandDeviceParams = namedtuple('HandDeviceParams', ['port', 'baudrate', 'regdict'])
FrankaParams = namedtuple('FrankaParams', ['hostname', 'username', 'password','T_C_E'])
RealManParams = namedtuple('RealManParams', ['hostname', 'username', 'password'])
FrankaPose = namedtuple('FrankaPose', ['pick_up_pose','place_pose','pick_up_joint','place_joint'])

# Robot arm IP address
# robot_arm_ip_address = "192.168.1.215"

# Arm motion parameters
arm_motion_params = MotionParams(
    default_acc=0.12,
    default_radius=0.03,
    # tcp_save_place_joint_position=[i * np.pi / 180 for i in [71.49, -93.21, 94.21, -4.7, 70.17, 0.79]],
    tcp_save_place_joint_position=[i * np.pi / 180 for i in [82.41, -83.59, 76.07, 10.63, 79.63, 2.73]],
    tcp_up_on_basket_joint_position=[i * np.pi / 180 for i in [89.54, -38.44, 30.95, 15.91, 96.24, 29.71]]
)




# Hand motion parameters
hand_motion_params = HandMotionParams(
    speedSet=[500, 500, 380, 380, 400, 500],
    angleSet_execute1=[800, 850, -1, -1, -1, 400],
    angleSet_execute2=[20, 20, 20, 20, 60, 0],
    forceSet=[450] * 6,
    tinyforceSet=[50] * 6,
    angleSet_abort=[950, 950, 950, 950, 950, 400]
)

# Hand device parameters
hand_device_params = HandDeviceParams(
    port="/dev/ttyUSB0",
    baudrate=115200,
    regdict={
        'ID': 1000,
        'baudrate': 1001,
        'clearErr': 1004,
        'forceClb': 1009,
        'angleSet': 1486,
        'forceSet': 1498,
        'speedSet': 1522,
        'angleAct': 1546,
        'forceAct': 1582,
        'errCode': 1606,
        'statusCode': 1612,
        'temp': 1618,
        'actionSeq': 2320,
        'actionRun': 2322
    }
)




franka_config = FrankaParams(
    hostname="172.16.0.2",
    username="franka",
    password="franka123",
    T_C_E = np.array([
        [0.01324788, 0.99925666, -0.03620257, 0.08072094],
        [-0.99713529, 0.01589888, 0.07394889, -0.02021566],
        [0.0744695, 0.0351192, 0.9966047, -0.14172613],
        [0., 0., 0., 1.]
    ])#相机标定： 相机到末端法兰盘的变换矩阵


)

realman_config = RealManParams(
    hostname="",
    username="",
    password=""
)

franka_pose = FrankaPose(
    pick_up_pose = [
        [9.99127271e-01, 2.53216505e-04, -4.15380770e-02, 3.72154993e-01],
        [8.24733595e-04, -9.99895602e-01, 1.37424452e-02, 9.02327462e-03],
        [-4.15302607e-02, -1.37647096e-02, -9.99042408e-01, 2.27123375e-01],
        [0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
    ],
    place_pose = [
        [0.51680651, -0.85371277, -0.06376806, 0.29916253],
        [-0.8555555, -0.51768258, -0.00320589, -0.34101281],
        [-0.03027471, 0.05621394, -0.9979596, 0.09485565],
        [0., 0., 0., 1.]
    ],
    pick_up_joint = [-0.011383417062461376, -0.25433722138404846, 0.022677350789308548, -2.6251397132873535, 0.005148423369973898, 2.295717477798462, 0.8916455507278442],
    place_joint = []
)