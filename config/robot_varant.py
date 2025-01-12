from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
panda_config = {
    "urdf_path": str(asset_dir / "robot_description/panda/panda_v3.urdf"),
    "srdf_path": str(asset_dir / "robot_description/panda/panda_v3.srdf"),
    "hand_name": "panda_hand",
    "position": [0, 0, 0],
    "orientation": [1, 0, 0, 0]
}

ur5_config = {
    "object_description": str(asset_dir / "robot_description/ur5/ur5.urdf"),
    "object_name": "gen3",
    "position": [0, 0, 0],
    "orientation": [1, 0, 0, 0]
}

sawyer_config = {
    "urdf_path": str(asset_dir / "robot_description/sawyer/sawyer.urdf"),
    "srdf_path": str(asset_dir / "robot_description/sawyer/sawyer.srdf"),
    "hand_name": "right_hand",
    "position": [0, 0, 0],
    "orientation": [1, 0, 0, 0]
}

gen3_config = {
    "urdf_path": str(asset_dir / "robot_description/kinova_gen3/kinova_gen3.urdf"),
    "srdf_path": str(asset_dir / "robot_description/kinova_gen3/kinova_gen3.srdf"),
    "hand_name": "tool_frame",
    "position": [0, 0, 0],
    "orientation": [1, 0, 0, 0]
}