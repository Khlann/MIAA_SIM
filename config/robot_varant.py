from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
robot_config = {
    "object_description": str(asset_dir / "robot_description/ur_description/urdf/ur5.urdf"),
    "object_name": "ur5e"
}