from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
table_config = {
    "object_description": str(asset_dir / "scene/table/table.urdf"),
    "object_name": "table"
}

banana_config = {
    "object_collision_meshes": str(asset_dir / "object/banana/collision.obj"),
    "object_visual_meshes": str(asset_dir / "object/banana/visual.glb"),
    "object_name": "banana"
}