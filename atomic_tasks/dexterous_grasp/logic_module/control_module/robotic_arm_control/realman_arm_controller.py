
class RealManArmController():
    def __init__(self, robot_type, robot_config, logger_manager=None):
        self.logger_manager = logger_manager
        self.robot_type = robot_type
        self.robot_config = robot_config