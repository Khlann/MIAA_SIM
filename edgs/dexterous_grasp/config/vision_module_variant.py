import os
from collections import namedtuple

# project_root_path = os.getenv("PROJECT_ROOT")
project_root_path =  "/home/arlen/arlen/miaa_sim/atomic_tasks"
external_gsam2_relative_path = "external/gsam2"

GroundSam2Config = namedtuple('GroundSam2Config', [
    'sam2_checkpoint',
    'sam2_model_config',
    'grounding_dino_config',
    'grounding_dino_checkpoint',
    'box_threshold',
    'text_threshold'
])

DinoxSam2Config = namedtuple('DinoxSam2Config', [
    'api_token',
    'sam2_checkpoint',
    'sam2_model_config',
    'grounding_dino_config',
    'grounding_dino_checkpoint',
    'box_threshold',
    'text_threshold',
    'image_template_path',
    'crop_point'
])

box_threshold = 0.35
text_threshold = 0.25
sam2_checkpoint = "checkpoints/sam2.1_hiera_large.pt"
sam2_model_config = "sam2.1_hiera_l.yaml"
grounding_dino_config = "grounding_dino/groundingdino/config/GroundingDINO_SwinB_cfg.py"
grounding_dino_checkpoint = "gdino_checkpoints/groundingdino_swinb_cogcoor.pth"

ground_sam2_config = GroundSam2Config(
    sam2_checkpoint=os.path.join(project_root_path, external_gsam2_relative_path, sam2_checkpoint),
    sam2_model_config=sam2_model_config,
    grounding_dino_config=os.path.join(project_root_path, external_gsam2_relative_path, grounding_dino_config),
    grounding_dino_checkpoint=os.path.join(project_root_path, external_gsam2_relative_path, grounding_dino_checkpoint),
    box_threshold=box_threshold,
    text_threshold=text_threshold
)

api_token = "82c4f05eadf72bfae374da97c456344c"

