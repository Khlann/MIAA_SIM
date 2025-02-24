import numpy as np
from collections import namedtuple

# Define namedtuples for arm and hand parameters
MotionParams = namedtuple('MotionParams', ['default_acc', 'default_radius', 'tcp_save_place_joint_position', 'tcp_up_on_basket_joint_position'])
HandMotionParams = namedtuple('HandMotionParams', ['speedSet', 'angleSet_execute1', 'angleSet_execute2', 'forceSet', 'tinyforceSet', 'angleSet_abort'])
HandDeviceParams = namedtuple('HandDeviceParams', ['port', 'baudrate', 'regdict'])

# Robot arm IP address
robot_arm_ip_address = "192.168.1.215"

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

# Now, you can access elements like:
# arm_motion_params.default_acc, hand_motion_params.angleSet_execute1, hand_device_params.port, etc.
