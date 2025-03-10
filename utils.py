"""Utilize from the source code from Sapien's doc."""
import sapien as sapien
import numpy as np

def create_box(
    scene: sapien.Scene,
    pose: sapien.Pose,
    half_size,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a box.

    Args:
        scene: sapien.Scene to create a box.
        pose: 6D pose of the box.
        half_size: [3], half size along x, y, z axes.
        color: [3] or [4], rgb or rgba
        name: name of the actor.

    Returns:
        sapien.Entity
    """
    half_size = np.array(half_size)
    builder: sapien.ActorBuilder = scene.create_actor_builder()
    builder.add_box_collision(half_size=half_size)  # Add collision shape
    builder.add_box_visual(half_size=half_size, material=color)  # Add visual shape
    box: sapien.Entity = builder.build(name=name)
    box.set_pose(pose)
    return box


def create_sphere(
    scene: sapien.Scene,
    pose: sapien.Pose,
    radius,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a sphere. See create_box."""
    builder = scene.create_actor_builder()
    builder.add_sphere_collision(radius=radius)
    builder.add_sphere_visual(radius=radius, material=color)
    sphere = builder.build(name=name)
    sphere.set_pose(pose)
    return sphere


def create_capsule(
    scene: sapien.Scene,
    pose: sapien.Pose,
    radius,
    half_length,
    color=None,
    name="",
) -> sapien.Entity:
    """Create a capsule (x-axis <-> half_length). See create_box."""
    builder = scene.create_actor_builder()
    builder.add_capsule_collision(radius=radius, half_length=half_length)
    builder.add_capsule_visual(radius=radius, half_length=half_length, material=color)
    capsule = builder.build(name=name)
    capsule.set_pose(pose)
    return capsule


def create_table(
    scene: sapien.Scene,
    pose: sapien.Pose,
    size,
    height,
    thickness=0.1,
    color=(0.8, 0.6, 0.4),
    name="table",
) -> sapien.Entity:
    """Create a table (a collection of collision and visual shapes)."""
    builder = scene.create_actor_builder()

    # Tabletop
    tabletop_pose = sapien.Pose(
        [0.0, 0.0, -thickness / 2]
    )  # Make the top surface's z equal to 0
    tabletop_half_size = [size / 2, size / 2, thickness / 2]
    builder.add_box_collision(pose=tabletop_pose, half_size=tabletop_half_size)
    builder.add_box_visual(
        pose=tabletop_pose, half_size=tabletop_half_size, material=color
    )

    # Table legs (x4)
    for i in [-1, 1]:
        for j in [-1, 1]:
            x = i * (size - thickness) / 2
            y = j * (size - thickness) / 2
            table_leg_pose = sapien.Pose([x, y, -height / 2])
            table_leg_half_size = [thickness / 2, thickness / 2, height / 2]
            builder.add_box_collision(
                pose=table_leg_pose, half_size=table_leg_half_size
            )
            builder.add_box_visual(
                pose=table_leg_pose, half_size=table_leg_half_size, material=color
            )

    table = builder.build(name=name)
    table.set_pose(pose)
    return table


def create_mesh(
    scene: sapien.Scene,
    pose: sapien.Pose,
    obj_path,
    glb_path,
    name="",
) -> sapien.Entity:
    """Create actor from mesh file. See create_box."""
    builder = scene.create_actor_builder()
    builder.add_convex_collision_from_file(filename=obj_path)
    builder.add_visual_from_file(filename=glb_path)
    mesh = builder.build(name="mesh")
    mesh.set_pose(pose)
    return mesh


def create_urdf(
    scene: sapien.Scene,
    pose: sapien.Pose,
    path,
    fix_root_link=False,
) -> sapien.Entity:
    """Create actor from urdf file. See create_box."""
    loader = scene.create_urdf_loader()
    loader.fix_root_link = fix_root_link
    actor = loader.load(path)
    if fix_root_link:
        actor.set_root_pose(pose)
    else:
        actor.set_pose(pose)
    return actor