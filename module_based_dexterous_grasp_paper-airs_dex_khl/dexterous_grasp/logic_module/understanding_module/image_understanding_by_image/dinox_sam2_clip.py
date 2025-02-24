import torch
import clip
from PIL import Image
import numpy as np
from pathlib import Path
from typing import Union, List, Tuple
import cv2
import os
import time
from dds_cloudapi_sdk import Config
from dds_cloudapi_sdk import Client
from dds_cloudapi_sdk.tasks.dinox import DinoxTask
from dds_cloudapi_sdk.tasks.types import DetectionTarget
from dds_cloudapi_sdk.tasks.detection import DetectionTask
from dds_cloudapi_sdk import TextPrompt

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

class CLIPImageSimilarity:
    def __init__(self, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        """
        初始化CLIP模型
        """
        self.device = device
        print(f"Using device: {self.device}")
        
        # 加载CLIP模型和预处理器
        self.model, self.preprocess = clip.load("ViT-L/14@336px", device=self.device)
        
    def load_image(self, image_path: Union[str, Path]) -> torch.Tensor:
        """
        加载和预处理图像
        """
        image = Image.open(image_path).convert('RGB')
        return self.preprocess(image).unsqueeze(0).to(self.device)
    
    def get_image_features(self, image: torch.Tensor) -> torch.Tensor:
        """
        获取图像特征
        """
        with torch.no_grad():
            image_features = self.model.encode_image(image)
            # 归一化特征
            image_features /= image_features.norm(dim=-1, keepdim=True)
        return image_features
    
    # def compute_similarity(self, 
    #                      image_path1: Union[str, Path], 
    #                      image_path2: Union[str, Path]) -> float:
    def compute_similarity(self, image1, image2):
        """
        计算两张图片的相似度
        """
        # 加载图片
        # image1 = self.load_image(image_path1)
        # image2 = self.load_image(image_path2)
        image1 = self.preprocess(image1).unsqueeze(0).to(self.device)
        image2 = self.preprocess(image2).unsqueeze(0).to(self.device)
        
        # 获取特征
        features1 = self.get_image_features(image1)
        features2 = self.get_image_features(image2)
        
        # 计算余弦相似度
        similarity = torch.nn.functional.cosine_similarity(features1, features2)
        
        return similarity.item()
    
    def find_most_similar(self, 
                         query_image: Union[str, Path], 
                         image_list: List[Union[str, Path]]) -> List[Tuple[str, float]]:
        """
        在图片列表中找到与查询图片最相似的图片
        """
        # 加载查询图片
        query_tensor = self.load_image(query_image)
        query_features = self.get_image_features(query_tensor)
        
        similarities = []
        
        # 计算与每张图片的相似度
        for img_path in image_list:
            img_tensor = self.load_image(img_path)
            img_features = self.get_image_features(img_tensor)
            
            similarity = torch.nn.functional.cosine_similarity(query_features, img_features)
            similarities.append((str(img_path), similarity.item()))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

class Img2Mask:
    def __init__(self, dinox_sam2_clip_config):
        token =  dinox_sam2_clip_config.api_token
        config = Config(token)
        self.client = Client(config)
        # initialize SAM2 model
        torch.autocast(device_type='cuda', dtype=torch.bfloat16).__enter__()
        if torch.cuda.get_device_properties(0).major >= 8:
            # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
            torch.backends.cuda.matmul.allow_tf32 = True
            torch.backends.cudnn.allow_tf32 = True
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sam2_model = build_sam2(dinox_sam2_clip_config.sam2_model_config,
                                dinox_sam2_clip_config.sam2_checkpoint,
                                device=self.device)
        self.sam2_predictor = SAM2ImagePredictor(self.sam2_model)

        # 模板匹配的config
        airs_hand_image_path = dinox_sam2_clip_config.image_template_path
        files = os.listdir(airs_hand_image_path)
        file_name = [os.path.splitext(file)[0] for file in files]
        for i in range(len(files)):
            files[i] = os.path.join(airs_hand_image_path, files[i])
        self.image_dict = {}
        for i in range(len(files)):
            self.image_dict[file_name[i]] = Image.open(files[i]).convert('RGB')
        
        # crop 
        self.crop_point = dinox_sam2_clip_config.crop_point
    
    def boxes_filter(self, image_path,boxes):
        color_image = cv2.imread(image_path)
        mask = np.zeros((color_image.shape[0], color_image.shape[1]), dtype=np.uint8)
        pts = np.array(self.crop_point, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(mask, [pts], isClosed=True, color=(255, 255, 255), thickness=2)
        cv2.fillPoly(mask, [pts], color=(255, 255, 255))

        save_boxes = []
        for box in boxes:
            center_x = (box[0] + box[2]) / 2
            center_y = (box[1] + box[3]) / 2
            if mask[int(center_y), int(center_x)] == 255:
                save_boxes.append(box)
        return save_boxes


    def detect_objects(self, image_path: str,mode):
        # config = Config(self.token)
        # client = Client(config)
        start_time = time.time()
        image_url = self.client.upload_file(image_path)
        task = DinoxTask(
            image_url=image_url,
            prompts=[TextPrompt(text="<prompt_free>")],
            bbox_threshold=0.1,
            targets=[DetectionTarget.BBox, DetectionTarget.Mask]
        )
        self.client.run_task(task)
        predictions = task.result.objects

        classes = [pred.category for pred in predictions]
        classes = list(set(classes))
        class_name_to_id = {name: id for id, name in enumerate(classes)}
        class_id_to_name = {id: name for name, id in class_name_to_id.items()}

        boxes = []
        masks = []
        confidences = []
        class_names = []
        class_ids = []

        for idx, obj in enumerate(predictions):
            boxes.append(obj.bbox)
            masks.append(DetectionTask.rle2mask(DetectionTask.string2rle(obj.mask.counts), obj.mask.size))  # convert mask to np.array using DDS API
            confidences.append(obj.score)
            cls_name = obj.category.lower().strip()
            class_names.append(cls_name)
            class_ids.append(class_name_to_id[cls_name])

        boxes = np.array(boxes)
        boxes = self.boxes_filter(image_path,boxes)
        masks = np.array(masks)
        class_ids = np.array(class_ids)

        end_time = time.time()
        print("Sam_time cost: ", end_time - start_time)
        #后面是sam的环节
        image = Image.open(image_path)
        self.sam2_predictor.set_image(np.array(image.convert("RGB")))
        masks, scores, logits = self.sam2_predictor.predict(
            point_coords=None,
            point_labels=None,
            box=boxes,
            multimask_output=False,
        )

        if masks.ndim == 4:
            masks = masks.squeeze(1)

        img = cv2.imread(image_path)
        # 根据mask保存每一个mask
        clip_masks = []
        for i, mask in enumerate(masks):
            save_img = np.zeros_like(img)
            # mask_path = os.path.join(OUTPUT_DIR, f"mask_{i}.png")
            
            # 应用 mask
            for j in range(mask.shape[0]):
                for k in range(mask.shape[1]):
                    if mask[j, k]:
                        save_img[j, k] = img[j, k]
            
            # 找到非零区域的边界
            non_zero = np.any(save_img != 0, axis=2)  # 检查所有通道是否都为 0
            if non_zero.any():  # 确保有非零像素
                rows = np.any(non_zero, axis=1)
                cols = np.any(non_zero, axis=0)
                rmin, rmax = np.where(rows)[0][[0, -1]]
                cmin, cmax = np.where(cols)[0][[0, -1]]
                
                # 裁剪到非零区域
                save_img = save_img[rmin:rmax+1, cmin:cmax+1]

                #转为PIL
                if mode !="debug":
                    save_img = Image.fromarray(save_img)
                
            # cv2.imwrite(mask_path, save_img)
            clip_masks.append(save_img)
        
        return clip_masks,masks
    
    def get_object_type(self,object_name):
        A_list = ["ball", "battery", "screwdriver", "screw"] 
        if object_name in A_list:
            return "A"
        else:
            return "B"

def find_most_similar(clip_masks,object_name,img2mask,clip_similarity):
    max_similarity = 0
    max_clip_mask_index = 0
    for index, clip_mask in enumerate(clip_masks):
        c_similarity = clip_similarity.compute_similarity(clip_mask, img2mask.image_dict[object_name])

        def calculate_area(mask):
            # 将 PIL 图像转换为 NumPy 数组
            mask_array = np.array(mask)
            # 确保图像是二值化的
            if len(mask_array.shape) == 3:
                mask_array = cv2.cvtColor(mask_array, cv2.COLOR_RGB2GRAY)
            _, binary_mask = cv2.threshold(mask_array, 1, 255, cv2.THRESH_BINARY)
            # 计算非零像素的数量
            return cv2.countNonZero(binary_mask)
        
        def calculate_area_ratio(mask1, mask2):
            area1 = calculate_area(mask1)
            area2 = calculate_area(mask2)
            if area1 == 0 or area2 == 0:
                return 0  # 避免除以零
            ratio = area1 / area2
            return min(ratio, 1/ratio)
        

        area_ratio = calculate_area_ratio(clip_mask, img2mask.image_dict[object_name])

        similarity = 0.6 * c_similarity + 0.4 * area_ratio
        # 得到clip_mask有效

        if similarity > max_similarity:
            max_similarity = similarity
            max_clip_mask_index = index

    return max_clip_mask_index
