import pybullet as p
import pybullet_data
import time

class Controller:
    def __init__(self,robot_config):
        p.connect(p.GUI)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        self.plane_id = p.loadURDF("plane.urdf")
        self.robot_id = p.loadURDF(robot_config["robot_description"])
        p.setGravity(0, 0, -9.81)

    def get_joint_info(self):
        num_joints = p.getNumJoints(self.robot_id)
        joint_info_list = []
        for joint_index in range(num_joints):
            joint_info = p.getJointInfo(self.robot_id, joint_index)
            joint_name = joint_info[1].decode('utf-8')  # Joint name is in bytes, decode to string
            joint_state = p.getJointState(self.robot_id, joint_index)
            joint_position = joint_state[0]  # Get the joint position
            joint_info_list.append({"joint_name": joint_name, "joint_position": joint_position})
            print(f"Joint {joint_index}: {joint_name}, Initial Position: {joint_position}") 
        return joint_info_list
        
    def visualize(self):
        # Run the simulation until 'q' is pressed
        while True:
            p.stepSimulation()
            time.sleep(1./240.)  # Sleep to simulate real-time
            
            # Get keyboard events
            keys = p.getKeyboardEvents()
            # Check if 'q' is pressed (ASCII code 113)
            if 113 in keys and keys[113] & p.KEY_WAS_TRIGGERED:
                break
            
    def set_robot_pose(self,robot_id, position, orientation):
        """
        设置机器人的初始位置和姿态
        
        参数:
            robot_id: 机器人的ID
            position: [x, y, z] 位置坐标
            orientation: [x, y, z, w] 四元数表示的姿态
        """
        # 设置机器人基座的位置和姿态
        p.resetBasePositionAndOrientation(
            bodyUniqueId=robot_id,
            posObj=position,
            ornObj=orientation
        )
    
    def add_object(self,object_config,position,orientation):
        """
        添加物体
        """ 
        object_urdf = object_config['object_description']
        object_id = p.loadURDF(object_urdf)
        self.set_robot_pose(object_id,position,orientation)
        return object_id
        
    def control(self,target_positions):
        joint_indices = [0, 1, 2, 3, 4, 5, 6]  # 7轴机器人的关节索引
        # 使用 setJointMotorControlArray 控制所有关节
        p.setJointMotorControlArray(
            bodyUniqueId=self.robot_id,
            jointIndices=joint_indices,
            controlMode=p.POSITION_CONTROL,
            targetPositions=target_positions,
            forces=[500] * len(joint_indices),  # 控制力矩
            positionGains=[0.03] * len(joint_indices),  # P增益
            velocityGains=[1] * len(joint_indices)  # D增益
        )