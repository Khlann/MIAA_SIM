from pathlib import Path
ROOT_DIR = Path(__file__).parent.parent
asset_dir = ROOT_DIR / "asset"
table_config = {
    "urdf_path": str(asset_dir / "scene/table/table.urdf"),
    "object_name": "table",
    "position": [0, 0, 0],
    "orientation": [1, 0, 0, 0]
}

banana_config = {
    "object_collision_meshes": str(asset_dir / "object/banana/collision.obj"),
    "object_visual_meshes": str(asset_dir / "object/banana/visual.glb"),
    "object_name": "banana"
}
cup_config = {
    "object_collision_meshes": str(asset_dir / "object/cup/textured.obj"),
    "object_visual_meshes": str(asset_dir / "object/cup/base.glb"),
    "object_name": "cup",
    "position": [0.5, 0, 0],
    "orientation": [1, 0, 0, 0]
}

bottle_config = {
    "urdf_path": str(asset_dir / "object/3517/mobility.urdf"),
    "object_name": "bottle",
    "position": [0.5, 0, 0],
    "orientation": [1, 0, 0, 0]
}
drawer_config = {
    "urdf_path": str(asset_dir / "object/19179/mobility.urdf"),
    "object_name": "drawer",
    "position": [1.5, 0, 0],
    "orientation": [1, 0, 0, 0]
}