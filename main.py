"""Take a picture of the scene and detect grasps."""
import argparse

import numpy as np
import open3d as o3d
import sapien as sapien
from PIL import Image

from config.object_varant import (banana_config, bottle_config, cup_config,
                                  drawer_config, table_config)
from gsnet import AnyGrasp
from utils import (create_box, create_capsule, create_mesh, create_sphere,
                   create_table, create_urdf)

parser = argparse.ArgumentParser()
parser.add_argument('--checkpoint_path', type=str, default='log/checkpoint_detection.tar', help='Model checkpoint path')
parser.add_argument('--max_gripper_width', type=float, default=0.1, help='Maximum gripper width (<=0.1m)')
parser.add_argument('--gripper_height', type=float, default=0.03, help='Gripper height')
parser.add_argument('--top_down_grasp', action='store_true', help='Output top-down grasps.')
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
cfgs = parser.parse_args()
cfgs.max_gripper_width = max(0, min(0.1, cfgs.max_gripper_width))

def main():
    anygrasp = AnyGrasp(cfgs)
    anygrasp.load_net()
    
    scene = sapien.Scene()
    scene.set_timestep(1 / 100.0)
    scene.add_ground(0)
    
    # trial scenario is a table on which a box, a sphere, a capsule, and a banana are placed
    table = create_table(
        scene,
        sapien.Pose(p=[0, 0, 1.0]),
        size=1.0,
        height=1.0,
    )
    
    box = create_box(
        scene,
        sapien.Pose(p=[0, 0, 1.0 + 0.05]),
        half_size=[0.05, 0.05, 0.05],
        color=[1.0, 0.0, 0.0],
        name="box",
    )
    
    sphere = create_sphere(
        scene,
        sapien.Pose(p=[0, -0.2, 1.0 + 0.05]),
        radius=0.05,
        color=[0.0, 1.0, 0.0],
        name="sphere",
    )
    
    capsule = create_capsule(
        scene,
        sapien.Pose(p=[0, 0.2, 1.0 + 0.05]),
        radius=0.05,
        half_length=0.05,
        color=[0.0, 0.0, 1.0],
        name="capsule",
    )
    
    banana = create_mesh(
        scene,
        sapien.Pose(p=[-0.2, 0, 1.0 + 0.05]),
        obj_path=banana_config["object_collision_meshes"],
        glb_path=banana_config["object_visual_meshes"],
        name=banana_config["object_name"],
    )
    # done
    
    scene.set_ambient_light([0.5, 0.5, 0.5])
    scene.add_directional_light([0, 1, -1], [0.5, 0.5, 0.5])
    
    # Camera settings
    near, far = 0.1, 100
    width, height = 640, 480
    
    # Camera is placed above the table and takes a shot downward
    cam_pos = np.array([0, 0, 3])
    forward = -cam_pos / np.linalg.norm(cam_pos)
    left = np.array([0, 1, 0])
    up = np.array([1, 0, 0])
    mat44 = np.eye(4)
    mat44[:3, :3] = np.stack([forward, left, up], axis=1)
    mat44[:3, 3] = cam_pos

    camera = scene.add_camera(
        name="camera",
        width=width,
        height=height,
        fovy=np.deg2rad(35),
        near=near,
        far=far,
    )
    camera.entity.set_pose(sapien.Pose(mat44))
    
    # viewer = scene.create_viewer()

    # viewer.set_camera_xyz(x=-2, y=0, z=2.5)
    # viewer.set_camera_rpy(r=0, p=-np.arctan2(2, 2), y=0)
    # viewer.window.set_camera_parameters(near=0.05, far=100, fovy=1)
    
    scene.step()  # run a physical step
    scene.update_render()  # sync pose from SAPIEN to renderer
    camera.take_picture()  # submit rendering jobs to the GPU

    # color and depth image
    rgba = camera.get_picture("Color")  # [H, W, 4]
    position = camera.get_picture("Position")  # [H, W, 4]
    
    # only need rgb and xyz
    points_opengl = position[..., :3][position[..., 3] < 1]
    color = rgba[..., :-1][position[..., 3] < 1].astype(np.float32)
    
    # no need for transformation to world frame
    # model_matrix = camera.get_model_matrix()
    # points_world = points_opengl @ model_matrix[:3, :3].T + model_matrix[:3, 3]
    # points_world[..., 2] = -points_world[..., 2]
    # points_world = points_world.astype(np.float32)
    
    points_opengl[..., 2] = -points_opengl[..., 2]
    points = points_opengl.astype(np.float32)
    
    # workspace limitation
    xmin, xmax = -2.0, 2.0
    ymin, ymax = -2.0, 2.0
    zmin, zmax = 0.0, 2.0
    lims = [xmin, xmax, ymin, ymax, zmin, zmax]
    
    # call SDK to get grasp, if --debug is not set, the cloud returned will always be None
    gg, cloud = anygrasp.get_grasp(points, color, lims=lims, apply_object_mask=True, dense_grasp=False, collision_detection=True)
    
    if len(gg) == 0:
        print('No Grasp detected after collision detection!')

    # show top-20 scores grasp pose
    gg = gg.nms().sort_by_score()
    gg_pick = gg[0:20]
    print(gg_pick.scores)
    print('grasp score:', gg_pick[0].score)
    
    # visualization
    if cfgs.debug:
        trans_mat = np.array([[1,0,0,0],[0,1,0,0],[0,0,-1,0],[0,0,0,1]])
        cloud.transform(trans_mat)
        grippers = gg.to_open3d_geometry_list()
        for gripper in grippers:
            gripper.transform(trans_mat)
        o3d.visualization.draw_geometries([*grippers, cloud])
        o3d.visualization.draw_geometries([grippers[0], cloud])
    
    # while not viewer.closed:
    #     scene.step()
    #     scene.update_render()
    #     viewer.render()
      
if __name__ == "__main__":
    main()