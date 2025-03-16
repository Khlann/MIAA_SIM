import sys
import cv2
import panda_py
# 下面三个路径自行替换为自己的路径
project_root_path = "/home/arlen/arlen/miaa_sim_khl/edgs"
gsam_path = "/home/arlen/arlen/miaa_sim_khl/edgs/external/gsam2"
sys.path.insert(0,project_root_path)
sys.path.insert(0,gsam_path)


from dexterous_grasp.logic_module import Dinox,TaskController, FrankaArmPlanner, Estimation, DoubaoClient
from dexterous_grasp.logger_module import LoggerManager
from dexterous_grasp.device_module import D435i, Speaker, Microphone
from dexterous_grasp.config import (franka_config, feedback_params, 
                                    audio_record_params, awake_params,doubao_config,
                                    api_token,franka_pose)

from utils import project_keypoints_to_img
from constraint_generation import ConstraintGenerator

# User_config
instruction = "Help me put the duck into the pot"

class rekep():
    def __init__(self):
        self.logger_manager = LoggerManager(project_root_path)
        self.cam = D435i(self.logger_manager)
        self.dinox = Dinox(api_token)
        self.estimation2D = Estimation()
        self.constraint_generator = ConstraintGenerator(doubao_config)

    def process(self):
        # Step 1: Get RGBD
        self.cam.capture_current_info()
        color_image, _ = self.cam.get_color_info()
        cv2.imwrite("color_image.png", color_image)
        color_image_path = "color_image.png"

        # Step 2: Get mask
        text_prompt = "<prompt_free>"
        masks = self.dinox.get_mask(color_image_path, text_prompt)

        # Step 3: Get keypoints
        keypoints_3d = self.estimation2D.get_keypoints_3d(masks,self.cam)# 像素坐标相对于相机坐标系的三维坐标（x,y,z)
        keypoints_2d = self.estimation2D.get_keypoints_2d(masks) # 像素坐标（x,y)
        project_keypoints_to_img(keypoints_2d,color_image)

        # Step 4: Generate constraints
        result = self.constraint_generator.generate(instruction, 'keypoints.png')
        with open('result.txt', 'w') as f:
            f.write(result)


if __name__ == '__main__':
    task = rekep()
    task.process()