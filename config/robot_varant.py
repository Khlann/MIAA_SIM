from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
robot_config = {
    # "object_description": str(asset_dir / "robot_description/ur5/ur5.urdf"),
    # "object_description": str(asset_dir / "robot_description/sawyer/sawyer.urdf"),
    # "object_description": str(asset_dir / "robot_description/xarm7_m/xarm7.urdf"),
    "object_description": str(asset_dir / "robot_description/panda/panda_v3.urdf"),
    "object_name": "panda"
}
