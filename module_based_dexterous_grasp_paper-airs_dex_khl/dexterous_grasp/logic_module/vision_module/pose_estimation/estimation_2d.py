import os
import cv2
import numpy as np

from dexterous_grasp.config import planning_module_varant,control_module_varant
from scipy.spatial.transform import Rotation as R


import pyrealsense2 as rs
from sklearn.decomposition import PCA  # PCA包，用于计算主轴
from dexterous_grasp.logger_module import LoggerValidator
import matplotlib.pyplot as plt
import urx  # 用于与UR机器人通信

class Estimation2D(LoggerValidator):
    def __init__(self, logger_manager=None, robot_ip=control_module_varant.robot_arm_ip_address):
        super().__init__(logger_manager)
        self.robot = urx.Robot(robot_ip)
        self.end2camera=planning_module_varant.end2camera


    def get_boundary_polygon(self, mask, epsilon_factor=0.02):
        mask = mask.astype(np.uint8)
        self.logger_manager.logger.info("Finding contours in the mask.")
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            self.logger_manager.logger.warning("No contours found in the mask.")
            return None
        contours = sorted(contours, key=lambda x: cv2.contourArea(x), reverse=True)
        max_area_contour = contours[0]
        self.logger_manager.logger.info(f"Found {len(contours)} contours. Selected the largest one.")
        epsilon = epsilon_factor * cv2.arcLength(max_area_contour, True)
        polygon = cv2.approxPolyDP(max_area_contour, epsilon, True)
        return polygon

    def calculate_mask_centroid(self, mask):
        self.logger_manager.logger.info("Calculating the centroid of the mask.")
        y_2d, x_2d = np.mean(np.where(mask), axis=1)
        self.logger_manager.logger.info(f"Calculated centroid at (x: {x_2d}, y: {y_2d}).")
        return (x_2d, y_2d)

    def get_3d_postion(self, x_2d, y_2d, camera):
        self.logger_manager.logger.info(f"Converting 2D point ({x_2d}, {y_2d}) to 3D coordinates using the camera.")
        x_3d, y_3d, z_3d = camera.xy2d2xy3d(x_2d, y_2d)
        self.logger_manager.logger.info(f"3D coordinates are (x: {x_3d}, y: {y_3d}, z: {z_3d}).")
        return x_3d, y_3d, z_3d

    def get_z_axis_deflection_radian(self, polygon):
        self.logger_manager.logger.info("Calculating z-axis deflection angle based on the boundary polygon.")
        rect = cv2.minAreaRect(polygon)
        rect_point = cv2.boxPoints(rect)
        rect_point = np.int32(rect_point)
        self.logger_manager.logger.info(f"Bounding rectangle points: {rect_point.tolist()}")

        line_0_1_length = np.linalg.norm(rect_point[0] - rect_point[1])
        line_1_2_length = np.linalg.norm(rect_point[1] - rect_point[2])

        if line_0_1_length > line_1_2_length:
            center_1_2 = (rect_point[1] + rect_point[2]) / 2
            center_0_3 = (rect_point[0] + rect_point[3]) / 2
            higher_point = center_1_2
            lower_point = center_0_3
        else:
            center_0_1 = (rect_point[0] + rect_point[1]) / 2
            center_2_3 = (rect_point[2] + rect_point[3]) / 2
            higher_point = center_2_3
            lower_point = center_0_1

        symmetry_axis = higher_point - lower_point
        tan = symmetry_axis[0] / symmetry_axis[1]
        radian = np.arctan(tan)
        self.logger_manager.logger.info(f"Calculated deflection angle in radians: {radian}")
        return radian, rect_point, higher_point, lower_point

    def get_3d_position_and_z_axis_radian(self, mask, camera):
        boundary_polygon = self.get_boundary_polygon(mask)
        if boundary_polygon is None:
            self.logger_manager.logger.error("Failed to get boundary polygon. Cannot proceed with 3D position and z-axis radian calculation.")
            return None, None
        centroid = self.calculate_mask_centroid(mask)

        position = self.get_3d_postion(centroid[0], centroid[1], camera)
        z_axis_radian, _, _, _ = self.get_z_axis_deflection_radian(boundary_polygon)
        self.logger_manager.logger.info(
            f"3D Position: {position}, z-axis deflection angle: {z_axis_radian * 180 / np.pi} degrees")

        # Visualize position and angle
        color_image, _ = camera.get_color_info()
        center = (int(centroid[0]), int(centroid[1]))
        cv2.circle(color_image, center, radius=5, color=(0, 255, 0), thickness=-1)

        length = 50  # Arrow length
        radian = z_axis_radian
        endpoint = (
            int(center[0] - length * np.sin(radian)),
            int(center[1] - length * np.cos(radian))  # Adjust y-axis direction
        )
        cv2.arrowedLine(color_image, center, endpoint, color=(0, 0, 255), thickness=2, tipLength=0.3)

        self.logger_manager.save_image(color_image, "3d_position_and_angle_visualization.jpg", self)

        return position, z_axis_radian
    

    def xy2d2xy3d(self, x_2d, y_2d):
        depth = self.depth_frame.get_distance(int(x_2d), int(y_2d))
        _, depth_intrinsics = self.get_depth_info()
        x_3d, y_3d, z_3d = rs.rs2_deproject_pixel_to_point(depth_intrinsics, [x_2d, y_2d], depth)
        return x_3d, y_3d, z_3d
    
    def get_boundary_pca_axis_with_direction_and_centroid(self, mask,camera):
        """
        从G-SAM2分割好的RGB二维mask中提取主轴方向（带正方向）和质心，并将质心与一个z参数连接起来。

        Parameters:
            mask: numpy.ndarray
                二维的分割mask图像，像素值为0或1。
            z_value: float
                用于附加到质心的z参数。
            depth_map: numpy.ndarray
                深度图像，用于获取像素对应的深度。

        Returns:
            direction: numpy.ndarray
                PCA主轴方向的单位向量，带正方向（2D）。
            centroid: numpy.ndarray
                质心的坐标 (x, y)，Z由用户自行输入。
        """
        mask = mask.astype(np.uint8)
        self.logger_manager.logger.info("Processing the mask to extract centroid and PCA direction.")
        centroid = self.calculate_mask_centroid(mask)
        # z_value = depth_varent.get_next_depth_value()
        # 计算二维质心
        x_2d, y_2d = centroid
        self.logger_manager.logger.info(f"Calculated centroid at {centroid}.")
        position=self.get_3d_postion(x_2d, y_2d, camera)
        # 使用深度图像和相机内参localize质心的3D坐标
        
        

        # 返回质心的前两个维度（X, Y），而不是返回完整的三维质心

        # 提取边界点
        self.logger_manager.logger.info("Extracting contours from the mask.")
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            self.logger_manager.logger.warning("No contours found in the mask.")
            return None, centroid # 添加z参数

        # 选择最大轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        boundary_points = largest_contour.reshape(-1, 2)  # 将轮廓点展平成二维坐标数组

        # 使用PCA计算主轴
        self.logger_manager.logger.info("Applying PCA on the boundary points.")
        pca = PCA(n_components=2)
        pca.fit(boundary_points)
        V1 = pca.components_[0]  # PCA主轴的方向向量

        # 寻找PCA轴与边界的交点
        self.logger_manager.logger.info("Calculating intersections of PCA axis with mask boundary.")
        intersections = []
        for point in boundary_points:
            vector = point - centroid  # 只使用x, y部分进行计算
            projection_length = np.dot(vector, V1)
            projection_point = centroid + projection_length * V1
            distance_to_axis = np.linalg.norm(point - projection_point)
            if distance_to_axis < 5:  # 距离阈值，判断是否为交点
                intersections.append(point)

        # 如果交点少于2个，使用单个交点作为正方向
        if len(intersections) < 2:
            self.logger_manager.logger.warning(f"Found only {len(intersections)} intersection(s). Using single intersection for direction.")
            if intersections:
                farthest_point = intersections[0]
            else:
                self.logger_manager.logger.warning("No valid intersection found. Using default PCA direction.")
                # 计算V1到pixel坐标系远端的PCA方向
                direction = np.linalg.norm(V1)
                direction.append(0)
                return direction, position
        else:
            # 找到两个交点中距离质心更远的点
            distances = [np.linalg.norm(intersection - centroid) for intersection in intersections]
            farthest_point = intersections[np.argmax(distances)]

        farthest_point = np.array(self.get_3d_postion(farthest_point[0], farthest_point[1], camera))
        centroid = np.array(self.get_3d_postion(centroid[0], centroid[1], camera))

# 确定正方向
        direction = farthest_point - centroid
        direction = direction / np.linalg.norm(direction)  # 单位化方向向量
        self.logger_manager.logger.info(f"Computed PCA direction with positive orientation: {direction}.")
        

        # 只返回前两个维度的方向和质心
        return direction,position # 只返回前两个维度的方向和质心心
    
    def get_transformation_matrix(self, direction, position,end2camera,mask,camera):
        """
        根据方向和质心构造物体坐标系相对于相机坐标系的4x4变换矩阵。
        direction为物体坐标系的x轴方向（在相机坐标系下的2D向量），
        centroid为物体坐标系原点在相机坐标系下的坐标(x, y, z)。
        
        假设：
        - 相机坐标系的z轴向下为正（即相机z朝向地面）。
        - 物体坐标系z轴竖直向上，与相机z轴反方向。
        - direction给出的方向在水平面中（即x-y平面内），
        direction对应物体坐标系的x轴。
        """

        # 确保direction是单位向量
        direction,position = self.get_boundary_pca_axis_with_direction_and_centroid(mask, camera)
        if direction is None or position is None:
            self.logger_manager.logger.error("Failed to compute direction or centroid.")
            return None
        direction = direction / np.linalg.norm(direction)
        dx, dy = direction[0], direction[1]
        
        # 构造物体坐标系的x轴（在相机坐标系下表示）
        object_x = np.array([dx, dy, 0.0])
        object_x = object_x / np.linalg.norm(object_x)  # 再次归一化
        
        # 物体坐标系z轴竖直向上，相机z轴向下，则object_z在相机系中为 [0,0,-1]
        object_z = np.array([0.0, 0.0, -1.0])
        object_z = object_z / np.linalg.norm(object_z)
        
        # 使用z × x得到y轴，确保右手坐标系
        object_y = np.cross(object_z, object_x)
        object_y = object_y / np.linalg.norm(object_y)
        
        # 再次保证正交(可选，一般三者已正交)
        # object_x = object_x / np.linalg.norm(object_x)
        # object_y = object_y / np.linalg.norm(object_y)
        # object_z = object_z / np.linalg.norm(object_z)

        # 构造旋转矩阵 R (from camera to object)
        # rows为object系的基向量在camera系的表示，
        # p_object = R * (p_camera - centroid)
        R = np.vstack((object_x, object_y, object_z))
        
        # 构造4x4的齐次变换矩阵
        # T = [ R    -R*centroid
        #       0 0 0       1     direction]
        position = np.array(position)
        translation = -R @ position.reshape(3,1)
        T_camera2object = np.eye(4)
        T_camera2object[:3,:3] = R
        T_camera2object[:3, 3] = translation.flatten()
        T_object2camera = np.linalg.inv(T_camera2object)
        self.logger_manager.logger.info(f"Transformation Matrix (Object to Camera): \n{T_object2camera}")

        self.logger_manager.logger.info(f"Transformation Matrix (Camera to Object): \n{T_camera2object}")


        return T_camera2object           




    def get_ur5_end_effector_pose(self):
        """
        获取UR-5末端的位姿。

        Returns:
            ur5_end_pose: numpy.ndarray
                4x4的变换矩阵，描述末端在基坐标系下的位置和方向。
        """
        self.logger_manager.logger.info("Retrieving UR-5 end effector pose.")

        tcp_pose = self.robot.getl()
        self.logger_manager.logger.info(f"Retrieved TCP pose: {tcp_pose}.")
        return np.array(tcp_pose)

    def pose_to_transformation_matrix(self,pose):
        """
        将6D姿势（x, y, z, rx, ry, rz）转换为4x4的变换矩阵。
        
        参数：
        pose (array-like): 长度为6的数组，包含x, y, z, rx, ry, rz。
                            x, y, z是平移，rx, ry, rz是绕X、Y、Z轴的欧拉角（弧度）。

        返回：
        np.ndarray: 4x4的变换矩阵。
        """
        # 提取位置和平移
        x, y, z, rx, ry, rz = pose
        
        # 使用scipy生成旋转矩阵，欧拉角顺序为 'xyz' (默认)
        rotation = R.from_euler('xyz', [rx, ry, rz])  # 使用'xyz'顺序表示欧拉角
        R_matrix = rotation.as_matrix()  # 获取3x3的旋转矩阵
        
        # 创建4x4的变换矩阵
        T = np.eye(4)
        T[:3, :3] = R_matrix  # 设置旋转矩阵
        T[:3, 3] = [x, y, z]  # 设置平移向量
        
        return T
    def transform_to_base_coordinates(self, position, direction, end2camera,mask,camera):
        """
        将像素质心点和方向从相机坐标系转换到基坐标系，并最终返回物体坐标系相对于基坐标系的4x4变换矩阵。

        Parameters:
            centroid: numpy.ndarray
                像素空间中质心的坐标 (x, y, z) 在相机坐标系下的点。
            direction: numpy.ndarray
                PCA主轴方向的单位向量（在相机坐标系下）。
            end2camera: RotationTranslation
                相机标定外参，包括旋转矩阵和平移向量，用于从相机坐标系到末端坐标系的变换。

        Returns:
            T_base2object: numpy.ndarray (4x4)
                物体坐标系相对于基坐标系的4x4齐次变换矩阵。
        """

        self.logger_manager.logger.info("Transforming centroid and direction to base coordinates.")
        end2camera = planning_module_varant.end2camera

        # UR5末端的姿态（根据上面的分析，此矩阵用于从end到base的转换）
        ur5_end_pose = self.get_ur5_end_effector_pose()
        # ur5_end_pose 为4x4矩阵：p_base = ur5_end_pose * p_end
        # 因此 ur5_end_pose = T_end2base

        # Step 1: Convert from camera coordinates to end-effector coordinates
        # p_end = R_end2camera * p_camera + t_end2camera
        # 所以end2camera参数实际上提供了从camera到end的变换：T_camera2end
        R_end2camera = end2camera.rotation
        t_end2camera = end2camera.translation
        T_end2camera = np.eye(4)
        T_end2camera[:3, :3] = R_end2camera
        T_end2camera[:3, 3] = t_end2camera

        # Step 2: Convert from end-effector coordinates to base coordinates
        # ur5_end_pose为T_end2base
        T_end2base = self.pose_to_transformation_matrix(ur5_end_pose)

        # 获得物体相对于相机的变换矩阵
        T_camera2object = self.get_transformation_matrix(direction,position,end2camera,mask,camera)
        self.logger_manager.logger.info(f"T_camera2object: \n{T_camera2object}")

        # 我们需要T_base2object:
        # T_base2object = T_camera2object * T_end2camera * T_end2base^-1
        # 由于我们有T_camera2end，需要先求T_end2camera = (T_camera2end)^-1
        # T_end2camera = np.linalg.inv(T_camera2end)

        # 同时我们有T_end2base，需要T_base2end = (T_end2base)^-1
        T_base2end = np.linalg.inv(T_end2base)
        T_camera2end=np.linalg.inv(T_end2camera)
        # 刚才推导的公式有两种等价形式：
        # p_object = T_camera2object * T_end2camera * (T_end2base^-1 * p_base)
        # 即
        # T_base2object = T_camera2object * T_end2camera * T_end2base^-1
        # 请注意这与上面的变量含义匹配。
        T_base2object = T_camera2object @ T_camera2end @ T_base2end
        # self.logger_manager.logger.info(f"T_object2base: \n{T_object2base}")

        T_object2base= np.linalg.inv(T_base2object)
        self.logger_manager.logger.info(f"T_base2object: \n{T_base2object}")
        self.logger_manager.logger.info(f"T_base2object: \n{T_object2base}")

        return T_object2base
    
    def visualize_results(self, base_centroid, base_direction):
        """
        可视化基坐标系下的质心和方向向量，并保存图像。

        Parameters:
            base_centroid: numpy.ndarray
                基坐标系下的质心坐标。
            base_direction: numpy.ndarray
                基坐标系下的方向向量。
            output_path: str
                保存可视化结果的路径。
        """
        self.logger_manager.logger.info("Visualizing results.")

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')

        # 质心
        ax.scatter(base_centroid[0], base_centroid[1], base_centroid[2], color='r', s=100, label='Base Centroid')

        # 方向向量
        direction_length = 0.1
        direction_end = base_centroid + base_direction * direction_length
        ax.quiver(
            base_centroid[0], base_centroid[1], base_centroid[2],
            base_direction[0], base_direction[1], base_direction[2],
            length=direction_length, color='b', label='Base Direction'
        )

        # 设置轴范围和标签
        ax.set_xlim([base_centroid[0] - 0.2, base_centroid[0] + 0.2])
        ax.set_ylim([base_centroid[1] - 0.2, base_centroid[1] + 0.2])
        ax.set_zlim([base_centroid[2] - 0.2, base_centroid[2] + 0.2])

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()

        plt.title("Visualization of Base Centroid and Direction")
        output_dir = os.path.expanduser('~/Contest_FInal/contest/assets/')
        os.makedirs(output_dir, exist_ok=True)
        existing_files = sorted([int(f.split('.')[0]) for f in os.listdir(output_dir) if f.split('.')[0].isdigit()])
        next_index = (existing_files[-1] + 1) if existing_files else 1
        output_path = os.path.join(output_dir, f"{next_index}.png")
        plt.savefig(output_path)
        self.logger_manager.logger.info(f"Visualization saved at {output_path}.")

    


    def process_mask_and_transform(self, mask, camera, end2camera):
        """
        综合封装函数，返回 3D 位置、z 轴偏转角度（弧度），以及物体相对于基坐标系的 4x4 变换矩阵。

        Parameters:
            mask: numpy.ndarray
                分割后的二值图像。
            camera: CameraInterface
                用于获取深度和颜色信息的相机实例。
            end2camera: RotationTranslation
                相机相对于机械臂末端的外参。

        Returns:
            position: tuple
                3D 空间中的 (x, y, z) 坐标。
            z_axis_radian: float
                z 轴偏转角度，单位为弧度。
            T_base2object: numpy.ndarray
                物体相对于基坐标系的 4x4 齐次变换矩阵。
        """
        try:
            self.logger_manager.logger.info("Starting mask processing and transformation.")

            # Step 1: 获取 3D 位置和 z 轴偏转角度
            position, z_axis_radian = self.get_3d_position_and_z_axis_radian(mask, camera)

            if position is None or z_axis_radian is None:
                self.logger_manager.logger.error("Failed to retrieve 3D position or z-axis radian.")
                return None, None, None

            self.logger_manager.logger.info(f"Position: {position}, Z-axis radian: {z_axis_radian}")

            # Step 2: 计算方向和质心
            direction, centroid = self.get_boundary_pca_axis_with_direction_and_centroid(mask,camera)

            if direction is None or centroid is None:
                self.logger_manager.logger.error("Failed to compute direction or centroid.")
                return position, z_axis_radian, None

            self.logger_manager.logger.info(f"Direction: {direction}, Centroid: {centroid}")

            # Step 3: 转换到基坐标系
            T_object2base = self.transform_to_base_coordinates(centroid, direction, end2camera,mask,camera)

            self.logger_manager.logger.info(f"Transformation Matrix (Base to Object): \n{T_object2base}")

            return position, z_axis_radian, T_object2base

        except Exception as e:
            self.logger_manager.logger.error(f"An error occurred during processing: {e}")
            return None, None, None



        # #用于在没有和ur-5连上的情况下单元测试的UR-5随机生成end-effector pose的代码
    # def get_ur5_end_effector_pose(self):
    #     """
    #     获取UR-5末端的位姿。返回一个随机的位姿。

    #     Returns:
    #         ur5_end_pose: numpy.ndarray
    #             4x4的变换矩阵，描述末端在基坐标系下的位置和方向。
    #     """
    #     self.logger_manager.logger.info("Retrieving UR-5 end effector pose.")

    #     # 随机生成一个 4x4 的变换矩阵
    #     # 位置部分：随机生成x, y, z坐标
    #     position = np.random.uniform(-1.0, 1.0, 3)  # 随机生成x, y, z坐标，范围为 -1 到 1

    #     # 旋转部分：随机生成一个3x3的旋转矩阵
    #     rotation = np.random.rand(3, 3)
    #     rotation = rotation @ rotation.T  # 使其成为一个对称矩阵，从而是一个有效的旋转矩阵
    #     rotation = rotation / np.linalg.norm(rotation)  # 归一化旋转矩阵

    #     # 构建 4x4 变换矩阵
    #     ur5_end_pose = np.eye(4)  # 生成一个单位矩阵
    #     ur5_end_pose[:3, :3] = rotation  # 设定旋转部分
    #     ur5_end_pose[:3, 3] = position  # 设定位置部分

    #     self.logger_manager.logger.info(f"Generated random UR-5 end effector pose: \n{ur5_end_pose}.")

    #     return ur5_end_pose
