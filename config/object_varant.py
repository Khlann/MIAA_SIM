from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
table_config = {
    "object_description": str(asset_dir / "scene/table/table.urdf"),
    "object_name": "table"
}