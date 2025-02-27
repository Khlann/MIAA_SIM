import torch

from PIL import Image
from torchvision.ops import box_convert

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from grounding_dino.groundingdino.util.inference import load_model, load_image, predict
import grounding_dino.groundingdino.datasets.transforms as T
from dexterous_grasp.logger_module import LoggerValidator


def image_preprocess(color_image):
    color_image_rgb = color_image[:, :, ::-1].copy()
    transform = T.Compose(
        [
            T.RandomResize([800], max_size=1333),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image_source = color_image_rgb
    image = Image.fromarray(color_image_rgb)
    image_transform, _ = transform(image, None)
    return image_source, image_transform


def convert_boxes_for_sam2(boxes, image_source):
    """Convert bounding boxes to SAM2 input format."""
    h, w, _ = image_source.shape
    boxes = boxes * torch.Tensor([w, h, w, h])
    return box_convert(boxes=boxes, in_fmt="cxcywh", out_fmt="xyxy").numpy()


class GroundedSAM(LoggerValidator):
    def __init__(self, ground_sam2_config, logger_manager=None):
        super().__init__(logger_manager)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ground_sam2_config = ground_sam2_config

        # Load models
        self._load_sam2_model()
        self._load_grounding_dino_model()

    def _load_sam2_model(self):
        self.logger_manager.logger.info("Loading SAM2 model...")
        try:
            sam2_model = build_sam2(self.ground_sam2_config.sam2_model_config,
                                    self.ground_sam2_config.sam2_checkpoint,
                                    device=self.device)
            self.sam2_predictor = SAM2ImagePredictor(sam2_model)
        except Exception as e:
            self.logger_manager.logger.error(f"Error loading SAM2 model: {e}")
            raise

    def _load_grounding_dino_model(self):
        self.logger_manager.logger.info("Loading Grounding DINO model...")
        try:
            self.grounding_model = load_model(self.ground_sam2_config.grounding_dino_config,
                                              self.ground_sam2_config.grounding_dino_checkpoint,
                                              device=self.device)
        except Exception as e:
            self.logger_manager.logger.error(f"Error loading Grounding DINO model: {e}")
            raise

    def segment(self, test_prompt, color_image):
        self.logger_manager.logger.info(f"Performing segmentation on image with prompt: {test_prompt}")

        # Enable autocast for better GPU performance
        with torch.autocast(device_type="cuda", dtype=torch.float16):
            if self._is_ampere_gpu:
                self._enable_tf32()

            # Preprocess image
            image_source, image_transform = image_preprocess(color_image)
            self.sam2_predictor.set_image(image_source)

            # Perform object detection using Grounding DINO
            boxes, confidences, labels = self._predict_with_grounding_dino(test_prompt, image_transform)

            # Convert boxes and predict with SAM2
            input_boxes = convert_boxes_for_sam2(boxes, image_source)
            mask, score, logit = self._predict_with_sam2(input_boxes)

            if mask is None:
                self.logger_manager.logger.error(f"No mask generated for prompt: {test_prompt}")
                return None, None, None, None

            mask = mask.squeeze(1) if mask.ndim == 4 else mask

            confidences = confidences.numpy().tolist()

            if len(labels) > 1:
                input_box, label, confidence = input_boxes[:1], labels[:1], confidences[:1]
            else:
                input_box, label, confidence = input_boxes, labels, confidences

            label = [f"{label[0]} {confidence[0]:.2f}"]
            mask = mask[:1] if len(mask) > 1 else mask
            self.logger_manager.logger.info(f"Segmentation mask: {mask.shape}, label: {label}")

            self.logger_manager.visualize_sam2(color_image, input_box, mask, label, self)

            masks = mask.squeeze() if mask.ndim == 3 else mask

            return masks, input_boxes, labels, confidences

    @staticmethod
    def _is_ampere_gpu(self):
        """Check if the current GPU is Ampere (for TF32 support)."""
        return torch.cuda.get_device_properties(0).major >= 8

    def _enable_tf32(self):
        """Enable TensorFloat-32 (TF32) for Ampere GPUs."""
        # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    def _predict_with_grounding_dino(self, test_prompt, image_transform):
        """Run Grounding DINO prediction."""
        return predict(
            model=self.grounding_model,
            image=image_transform,
            caption=test_prompt.lower(),
            box_threshold=self.ground_sam2_config.box_threshold,
            text_threshold=self.ground_sam2_config.text_threshold,
        )

    def _predict_with_sam2(self, input_boxes):
        """Run SAM2 prediction on the provided boxes."""
        try:
            return self.sam2_predictor.predict(
                point_coords=None,
                point_labels=None,
                box=input_boxes,
                multimask_output=False,
            )
        except AssertionError:
            self.logger_manager.logger.error("SAM2 prediction failed.")
            return None, None, None