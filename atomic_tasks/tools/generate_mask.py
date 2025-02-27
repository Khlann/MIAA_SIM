from dexterous_grasp.device_module.cameras import D435i
from dexterous_grasp.logic_module.understanding_module import Img2Mask
from dexterous_grasp.config import dinox_sam2_clip_config
from dexterous_grasp.logger_module.logger import LoggerManager
import os
import cv2
if __name__ == "__main__":
    logger = LoggerManager()
    realsense_camera = D435i(logger)
    img2mask = Img2Mask(dinox_sam2_clip_config=dinox_sam2_clip_config)
    output_dir = "/home/airs/Airs/project/module_based_dexterous_grasp_paper/cache"
    realsense_camera.capture_current_info()
    color_image, _ = realsense_camera.get_color_info()
    cv2.imwrite("color_image.png", color_image)
    clip_mask, masks = img2mask.detect_objects("color_image.png", "debug")
    for idx,mask in enumerate(clip_mask):
        cv2.imwrite(os.path.join(output_dir,f"maskk_{idx}.png"),mask)        
         