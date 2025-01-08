from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
robot_config = {
    "robot_description": str(asset_dir / "robot_description/xarm7/xarm7.urdf"),
    "robot_name": "xarm7"
}