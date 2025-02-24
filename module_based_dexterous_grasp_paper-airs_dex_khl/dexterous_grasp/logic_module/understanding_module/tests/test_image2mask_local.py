import unittest

from dexterous_grasp.logic_module.understanding_module import Img2Mask_local
from dexterous_grasp.logic_module.understanding_module import CLIPImageSimilarity_local,find_most_similar_local
from dexterous_grasp.config import dinox_sam2_clip_config
import cv2
import os
from PIL import Image
import time
test_path_list = [
    "/home/arlen/arlen/module_based_dexterous_grasp_paper/assets/color_image_1.png",
    "/home/arlen/arlen/module_based_dexterous_grasp_paper/assets/color_image_2.png",
    "/home/arlen/arlen/module_based_dexterous_grasp_paper/assets/color_image_3.png",
    "/home/arlen/arlen/module_based_dexterous_grasp_paper/assets/color_image_4.png",
    "/home/arlen/arlen/module_based_dexterous_grasp_paper/assets/color_image_5.png",]
test_object_list = ["battery", "capsule", "ball", "screwdriver", "red_cloth", "egg", "screw"]
output_dir = "/home/arlen/arlen/module_based_dexterous_grasp_paper/dexterous_grasp/logic_module/understanding_module/tests/output"
def get_object_type(object_name):
    A_list = ["ball", "battery", "screwdriver", "screw"] 
    if object_name in A_list:
        return "A"
    else:
        return "B"
class TestImage2Mask(unittest.TestCase):
    def setUp(self):
        self.img2mask = Img2Mask_local(dinox_sam2_clip_config)
        self.clip_similarity = CLIPImageSimilarity_local()

    def test_img2mask(self):
        for idx, test_path in enumerate(test_path_list):
            
            clip_masks,masks = self.img2mask.detect_objects(test_path)

            # User_input
            for object_name in test_object_list:
                obj_type = get_object_type(object_name)
                # object_name = "capsule"#['battery', 'capsule', 'ball', 'screwdriver', 'red_cloth', 'egg', 'screw']
                start_time = time.time()
                max_clip_mask_index = find_most_similar_local(clip_masks, object_name, self.img2mask, self.clip_similarity)
                end_time = time.time()
                print("Clip_time cost: ", end_time - start_time)
                # 这里的mask是下游的mask
                mask = masks[max_clip_mask_index]
                raw_image = cv2.imread(test_path)
                # 在原图上画出mask
                for i in range(mask.shape[0]):
                    for j in range(mask.shape[1]):
                        if mask[i, j]:
                            if obj_type == "A":#设置为红色
                                raw_image[i, j] = [255, 0, 0]
                            else:#设置为绿色
                                raw_image[i, j] = [0, 0, 255]
                                
                            # raw_image[i, j] = [0, 0, 255]
                cv2.imwrite(os.path.join(output_dir, f"mask_{idx}_{object_name}.png"), raw_image)

if __name__ == '__main__':
    unittest.main()