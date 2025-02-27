import torch
# import clip
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

class Dinox:
    def __init__(self):
        API_TOKEN = "82c4f05eadf72bfae374da97c456344c"
        IMG_PATH = "/home/arlen/arlen/miaa_sim/cola_image.png"

        token = API_TOKEN
        config = Config(token)
        self.client = Client(config)
    
    def get_mask(self, image_path: str, text_prompt: str):
        image_url = self.client.upload_file(image_path)
        task = DinoxTask(
            image_url=image_url,
            prompts=[TextPrompt(text=text_prompt)],
            bbox_threshold=0.25,
            targets=[DetectionTarget.BBox, DetectionTarget.Mask]
        )
        self.client.run_task(task)
        predictions = task.result.objects

        masks = []
        for idx, obj in enumerate(predictions):
            masks.append(DetectionTask.rle2mask(DetectionTask.string2rle(obj.mask.counts), obj.mask.size))  # convert mask to np.array using DDS API
        
        mask = masks[0]
        for i in range(mask.shape[0]):
            for j in range(mask.shape[1]):
                if mask[i, j]:
                    mask[i, j] = 255
                else:
                    mask[i, j] = 0
        mask = mask.astype(np.uint8)
        return mask