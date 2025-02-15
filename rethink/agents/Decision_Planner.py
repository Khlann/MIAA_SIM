class ActionPrimitives:
    def camera_pan_tilt(self, angle_x, angle_y):
        """云台控制API"""
        
    def push_object(self, start_pose, end_pose):
        """非抓取式物体移动"""
        
    def grasp_sequence(self, target_pose):
        """抓取动作链生成"""
        
    #这里需要结合sapien定义一些元动作
    
    """
    引入 PDDL 规划器生成动作序列
    集成碰撞检测算法（GJK+EPA）
    """