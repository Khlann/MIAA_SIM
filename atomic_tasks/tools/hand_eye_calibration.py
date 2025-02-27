import re
import cv2
import numpy as np
import pyrealsense2 as rs
import urx
import time
import dexterous_grasp.config.control_module_varant as control_varant


# 请根据实际情况修改UR机械臂的IP地址和连接方式
UR5_IP = control_varant.robot_arm_ip_address # 示例IP，请替换为您的UR5真实IP地址

config_path = "dexterous_grasp/config/planning_module_varant.py"

class l515:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.profile = self.pipeline.start(self.config)
        self.align = rs.align(rs.stream.color)

    def get_aligned_images(self):
        frames = self.pipeline.wait_for_frames()  
        aligned_frames = self.align.process(frames)  
        color_frame = aligned_frames.get_color_frame()  
        if not color_frame:
            raise RuntimeError("No color frame received from camera.")
        intrinsics = color_frame.profile.as_video_stream_profile().intrinsics
        rgb_image = np.asanyarray(color_frame.get_data())
        dist_coeffs = np.array([intrinsics.coeffs[0], intrinsics.coeffs[1], intrinsics.coeffs[2],
                                intrinsics.coeffs[3], intrinsics.coeffs[4]])
        camera_matrix = np.array([[intrinsics.fx, 0, intrinsics.ppx],
                                  [0, intrinsics.fy, intrinsics.ppy],
                                  [0, 0, 1]])
        undistorted_image = cv2.undistort(rgb_image, camera_matrix, dist_coeffs)
        return undistorted_image, camera_matrix, dist_coeffs

def get_transform_from_rotation_translation(rotation, translation):
    rotation = np.array(rotation)
    translation = np.array(translation)
    transformation_matrix = np.eye(4)
    transformation_matrix[:3, :3] = rotation
    transformation_matrix[:3, 3] = translation
    return transformation_matrix

def detect_aruco_markers(image):
    # 使用ArUco的原始字典
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_ARUCO_ORIGINAL)
    parameters = cv2.aruco.DetectorParameters()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    if ids is None:
        return None, None, None

    target_id = 998
    filtered_corners = []
    filtered_ids = []
    for i, marker_id in enumerate(ids):
        if marker_id == target_id:
            filtered_corners.append(corners[i])
            filtered_ids.append(marker_id)

    if len(filtered_corners) == 0:
        return None, None, None

    cv2.aruco.drawDetectedMarkers(image, filtered_corners, np.array(filtered_ids))
    return filtered_corners, filtered_ids, image

def get_aruco2camera_transform(l515_obj, marker_length_m):
    rgb_image, camera_matrix, dist_coeffs = l515_obj.get_aligned_images()
    corners, ids, _ = detect_aruco_markers(rgb_image)

    if corners is not None and ids is not None and len(corners) > 0:
        rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length_m, camera_matrix, dist_coeffs)
        # rvec, tvec形状一般为(1,1,3)
        rotation_matrix = cv2.Rodrigues(rvec[0][0])[0]
        translation_vector = tvec[0][0]
        return get_transform_from_rotation_translation(rotation_matrix, translation_vector)
    return None

def get_ur5_end_effector_pose():
    """
    通过URX库获取UR-5末端执行器在Base坐标系下的位姿。
    get_pose()通常返回一个Transformation对象，可通过get_matrix()获得4x4矩阵。
    矩阵形式:
        [ R   p ]
        [ 0   1 ]
    R为3x3旋转矩阵，p为3x1平移向量。

    示例使用URX:
    """
    rob = urx.Robot(UR5_IP)
    time.sleep(0.5)  # 等待一下连接稳定（根据情况可省略）
    pose = rob.get_pose()  # pose是一个urx的Transformation对象
    rob.close()
    # 获取4x4矩阵
    T_base_ee = pose.get_matrix()
    return T_base_ee

# ArUco相对于Base的已知变换（需根据实际标定值修改）
aruco2base_translation = [0.01104, -0.68825, -0.00296]
aruco2base_rotation = [[-1, 0, 0],
                       [0, -1, 0],
                       [0, 0, 1]]
aruco2base_transform = get_transform_from_rotation_translation(aruco2base_rotation, aruco2base_translation)

# 多次尝试检测ArUco标记
for attempt in range(10):
    aruco2camera_transform = get_aruco2camera_transform(l515(), 0.1)
    if aruco2camera_transform is None:
        print(f"Attempt {attempt + 1}: ArUco marker not detected. Please try again.")
    else:
        break
else:
    raise Exception("ArUco marker not detected after multiple attempts. Calibration failed.")

# camera2aruco_transform = (T_aruco_camera)^(-1)
camera2aruco_transform = np.linalg.inv(aruco2camera_transform)
# T_base_camera = T_base_aruco * T_aruco_camera^(-1) = aruco2base_transform @ camera2aruco_transform
camera2base_transform = aruco2base_transform @ camera2aruco_transform

# 从UR5获取末端执行器的T_base_ee
T_base_ee = get_ur5_end_effector_pose()

# T_base_camera已知
T_base_camera = camera2base_transform

# 计算T_ee_camera = (T_base_ee)^(-1) * T_base_camera
T_ee_base = np.linalg.inv(T_base_ee)
T_ee_camera = T_ee_base @ T_base_camera

ee_camera_rotation_matrix = T_ee_camera[:3, :3]
ee_camera_translation = T_ee_camera[:3, 3]

print("Camera to End-Effector Rotation:\n", ee_camera_rotation_matrix)
print("Camera to End-Effector Translation:\n", ee_camera_translation)
# Read the content of the specified file
with open(config_path, "r") as file:
    config_content = file.read()

# Convert lists to the required string format
new_translation_str = f"np.array({ee_camera_translation})"
new_rotation_str = "np.array([" + ",\n               ".join([str(row) for row in ee_camera_rotation_matrix]) + "])"

# Regular expressions to match translation and rotation
translation_regex = r"\stranslation=np\.array\(\[.*?\]\)"
rotation_regex = r"\srotation=np\.array\(\[\[.*?\]\]\)"

# Replace old translation and rotation with new ones
updated_content = re.sub(translation_regex, f" translation={new_translation_str}", config_content, flags=re.DOTALL)
updated_content = re.sub(rotation_regex, f" rotation={new_rotation_str}", updated_content, flags=re.DOTALL)

with open(config_path, "w") as file:
    file.write(updated_content)
# # 更新 config 文件中的end2camera矩阵
# with open(config_path, "r") as file:
#     config_content = file.read()

# # 将ee_camera_rotation_matrix和ee_camera_translation转换为字符串格式
# new_end2camera_rotation_str = "np.array([" + ",\n        ".join([str(row.tolist()) for row in ee_camera_rotation_matrix]) + "])"
# new_end2camera_translation_str = f"np.array({ee_camera_translation.tolist()})"

# # 使用正则表达式替换end2camera的值
# # 假设原文件中 end2camera 定义格式为:
# # end2camera = RotationTranslation(
# #     rotation=np.array([
# #         [0.7071, -0.7071, 0],
# #         [4.33e-17, 4.33e-17, -1],
# #         [0.7071, 0.7071, 6.12e-17]
# #     ]),
# #     translation=np.array([34.02 / 1000, 34.02 / 1000, 48.73 / 1000])
# # )
# # 我们需要替换rotation和translation的定义行

# pattern = r"(end2camera\s*=\s*RotationTranslation\s*\(\s*rotation=\s*np\.array\(\[\[.*?\]\]\s*,\s*translation=\s*np\.array\(\[.*?\]\)\s*\))"
# # 使用re.DOTALL来匹配多行
# match = re.search(pattern, config_content, flags=re.DOTALL)
# if match:
#     # 构造新的end2camera定义
#     new_end2camera = f"end2camera = RotationTranslation(\n" \
#                      f"    rotation={new_end2camera_rotation_str},\n" \
#                      f"    translation={new_end2camera_translation_str}\n" \
#                      f")"
#     updated_content = re.sub(pattern, new_end2camera, config_content, flags=re.DOTALL)
# else:
#     raise ValueError("Could not find the original end2camera definition in the config file.")

# with open(config_path, "w") as file:
#     file.write(updated_content)

# print("end2camera matrix updated successfully in config file.")

