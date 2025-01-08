from .controller import p

class Camera:
    def __init__(self,camera_config):
        # 设置相机参数
        self.camera_distance = camera_config['camera_distance']  # 相机距离目标点的距离
        self.camera_yaw = camera_config['camera_yaw']       # 相机水平旋转角度(度)
        self.camera_pitch = camera_config['camera_pitch']    # 相机俯仰角度(度)
        self.camera_target = camera_config['camera_target']  # 相机目标点坐标 [x, y, z]
        # 设置相机视角
        p.resetDebugVisualizerCamera(
            cameraDistance=self.camera_distance,
            cameraYaw=self.camera_yaw,
            cameraPitch=self.camera_pitch,
            cameraTargetPosition=self.camera_target
        )
        
    # 如果需要获取相机图像，可以这样设置：
    def get_camera_image(self,width=640, height=480):
        # 设置相机参数
        view_matrix = p.computeViewMatrixFromYawPitchRoll(
            cameraTargetPosition=self.camera_target,
            distance=self.camera_distance,
            yaw=self.camera_yaw,
            pitch=self.camera_pitch,
            roll=0,
            upAxisIndex=2
        )
        
        # 设置投影矩阵
        proj_matrix = p.computeProjectionMatrixFOV(
            fov=60.0,               # 视场角
            aspect=width/height,    # 宽高比
            nearVal=0.1,           # 最近距离
            farVal=100.0           # 最远距离
        )
        
        # 获取图像
        (_, _, px, _, _) = p.getCameraImage(
            width=width,
            height=height,
            viewMatrix=view_matrix,
            projectionMatrix=proj_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL
        )
        
        return px