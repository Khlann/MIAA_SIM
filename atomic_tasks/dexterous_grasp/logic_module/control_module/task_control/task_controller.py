import multiprocessing
import panda_py
from dexterous_grasp.logic_module.control_module import FrankaController, RealManArmController
from dexterous_grasp.logger_module.logger import LoggerValidator


class TaskController(LoggerValidator):
    def __init__(self, robot_type, robot_config, logger_manager=None):
        super().__init__(logger_manager)
        # self.tcp_save_place_joint_position = arm_motion_params.tcp_save_place_joint_position
        # self.tcp_up_on_basket_joint_position = arm_motion_params.tcp_up_on_basket_joint_position
        # self.tcp_start_place_joint_position = robot_config[robot_type].tcp_start_place_joint_position
        # self.tcp_up_on_basket_joint_position = robot_config[robot_type].tcp_up_on_basket_joint_position
        # self.dexterous_hand_controller = DexterousHandController(hand_motion_params, hand_device_params, logger_manager=logger_manager)
        if robot_type == "franka":
            self.robotic_arm_controller = FrankaController(robot_config, logger_manager=logger_manager)
            self.robotic_arm_controller.robot_arm.move_to_start()
            self.start_pose = self.robotic_arm_controller.robot_arm.get_pose()
            self.initial_angle_gap = panda_py.ik(self.start_pose)[6]
        elif robot_type == "realman":
            self.robotic_arm_controller = RealManArmController(robot_config, logger_manager=logger_manager)
            #todo: add realman move to start
        # self.robotic_arm_controller = RoboticArmController(robot_type, robot_config, logger_manager=logger_manager)
        # self.move_to_safeplace()

        
    def dict_to_list(self, dictionary: dict) -> list:
        return list(dictionary.values())
          
    def move_to_safeplace(self):
        self.robotic_arm_controller.execute_movement_joints(self.tcp_save_place_joint_position)


    # 原子动作
    # 抓取子任务    
    def pick(self, grasp_tpose_sequences: dict):
        # Implementation for picking up the object
        movement_command = self.dict_to_list(grasp_tpose_sequences)
        self.robotic_arm_controller.execute_smooth_movement_tposes(movement_command) # 执行机械臂运动到物体
        # self.logger_manager.logger.info(f"grasp posture:{self.robotic_arm_controller.robot_arm.getl()}")
        # self.dexterous_hand_controller.execute_grasp() # 执行灵巧手抓取
    
    # 放置子任务    
    def place(self, grasp_tpose_sequences: dict):
        # Implementation for placing the object
        grasp_tpose_sequences = self.dict_to_list(grasp_tpose_sequences)
        tcp_up_on_object_pose = grasp_tpose_sequences[0] # 抓取物体后抬起的位姿

        p = multiprocessing.Process(target=self.dexterous_hand_controller.execute_regrasp)
        p.start()

        self.robotic_arm_controller.execute_smooth_movement_tposes([tcp_up_on_object_pose]) # 执行机械臂抓取物体后抬起的动作print(f"arm lift posture:{self.robot_arm.getl()}")
        self.robotic_arm_controller.execute_movement_joints(self.tcp_up_on_basket_joint_position) # 执行机械臂移动到放置位置上方
        # self.logger_manager.logger.info(f"hand on basket posture:{self.robotic_arm_controller.robot_arm.getl()}")
        # self.dexterous_hand_controller.abort_grasp() # 放开物体
    
    # main 任务序列执行
    def execute_task(self, grasp_tpose_sequences: dict):
        # self.logger_manager.logger.info("Executing task sequence")
        # self.logger_manager.logger.info(f"grasp_tpose_sequences: {grasp_tpose_sequences}")
        # Implementation for executing the movement based on the planned path
        self.move_to_safeplace() # 移动到安全位置
        # self.logger_manager.logger.info(f"safe place:{self.robotic_arm_controller.robot_arm.getl()}")
        self.pick(grasp_tpose_sequences)
        self.place(grasp_tpose_sequences)

        self.move_to_safeplace()
        # self.logger_manager.logger.info(f"safe place:{self.robotic_arm_controller.robot_arm.getl()}")