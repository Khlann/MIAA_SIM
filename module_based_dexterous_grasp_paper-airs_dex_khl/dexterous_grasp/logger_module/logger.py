import re
import os
import cv2
import time
import logging
import numpy as np
import supervision as sv

class EmptyLoggerManager:
    def __init__(self):
        self.logger = self

    def __getattr__(self, name):
        # 对所有未定义的方法返回一个函数，它接受任意参数并直接pass
        def method(*args, **kwargs):
            pass

        return method


class LoggerManager:
    def __init__(self, project_root_path=None):
        # 初始化项目根路径，如果没有传入就从环境变量获取
        self.project_root_path = project_root_path or os.getenv("PROJECT_ROOT")

        # 获取当前时间戳并创建 log 文件夹名
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.log_dir = os.path.join(self.project_root_path, "logs", f"logs_{current_time}")
        self.log_file = os.path.join(self.log_dir, f"pipeline_{current_time}.log")
        self.prompt_dir = None

        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # 初始化全局 logger
        self.logger = logging.getLogger('DexterousGraspLogger')
        self.logger.setLevel(logging.DEBUG)

        # 文件处理器 - 将日志写入文件
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)

        # 格式化日志输出
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # 添加处理器到 logger
        self.logger.addHandler(file_handler)

        # 输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        self.logger.info("Logger initialized.")

    def create_prompt_folder(self, prompt):
        """根据 prompt 创建一个唯一文件夹，用于存放与 prompt 相关的图片"""
        # 处理 prompt，替换空格和其他特殊字符为下划线
        sanitized_prompt = re.sub(r'[^\w\-_]', '_', prompt.strip().replace(' ', '_'))

        # 使用当前时间戳确保文件夹名称唯一
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        self.prompt_dir = os.path.join(self.log_dir, f"{sanitized_prompt}_{current_time}")

        # 创建 prompt 文件夹
        if not os.path.exists(self.prompt_dir):
            os.makedirs(self.prompt_dir)
            self.logger.info(f"Created folder for prompt: {self.prompt_dir}")
        else:
            self.logger.warning(f"Folder already exists: {self.prompt_dir}")

    def save_image(self, image, file_name, instance):
        class_name = type(instance).__name__
        save_dir = self.prompt_dir if self.prompt_dir else self.log_dir
        image_path = os.path.join(save_dir, file_name)

        success = cv2.imwrite(image_path, image)
        if success:
            self.logger.info(f"Image saved by {class_name} as {file_name} in {save_dir}")
        else:
            self.logger.error(f"Failed to save image by {class_name} as {file_name}")

    def visualize_sam2(self, color_image, input_boxes, masks, labels, instance):
        detections = sv.Detections(xyxy=input_boxes, mask=masks.astype(bool), class_id=np.arange(len(labels)))

        # Box annotator
        box_annotator = sv.BoxAnnotator()
        annotated_frame = box_annotator.annotate(scene=color_image.copy(), detections=detections)

        # Label annotator
        label_annotator = sv.LabelAnnotator()
        annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections, labels=labels)

        # Mask annotator
        mask_annotator = sv.MaskAnnotator()
        annotated_frame = mask_annotator.annotate(scene=annotated_frame, detections=detections)

        # Save final annotated image with masks
        self.save_image(annotated_frame, "grounded_sam2_annotated_image_with_mask.jpg", instance)


class LoggerValidator:
    def __init__(self, logger_manager=None):
        self.logger_manager = logger_manager if logger_manager else EmptyLoggerManager()


