import sapien
import cv2

class Controller:
    def __init__(self):
        self.scene = sapien.Scene()
        self.scene.add_ground(0)

        self.scene.set_ambient_light([0.5, 0.5, 0.5])
        self.scene.add_directional_light([0, 1, -1], [0.5, 0.5, 0.5])

        self.viewer = self.scene.create_viewer()
        self.viewer.set_camera_xyz(x=-2, y=0, z=1)
        self.viewer.set_camera_rpy(r=0, p=-0.3, y=0)
            
    def add_object(self,object_config,position,orientation):
        # loader = self.scene.create_urdf_loader()
        # loader.fix_root_link = False
        loader: sapien.URDFLoader = self.scene.create_urdf_loader()
        loader.fix_root_link = True
        object = loader.load(object_config['object_description'])
        object.set_root_pose(sapien.Pose(position,orientation))
        return object
    
    def set_robot_pose(self,object,arm):
        # arm_init_qpos = [4.71, 2.84, 0, 0.75, 4.62, 4.48, 4.88]
        # gripper_init_qpos = [0, 0, 0, 0, 0, 0]
        # init_qpos = arm_init_qpos + gripper_init_qpos
        finger = [0.0, 0.0]
        qpos = arm + finger
        object.set_qpos(qpos)
            
    def visualize(self,object):
        # while True:
        #     for _ in range(4):
        #         self.scene.step()
        #     self.scene.update_render()
        #     self.viewer.render()
        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break
        # self.viewer.close()
        while not self.viewer.closed:
            for _ in range(4):  # render every 4 steps
                if True:
                    qf = object.compute_passive_force(
                        gravity=True,
                        coriolis_and_centrifugal=True,
                    )
                    object.set_qf(qf)
                self.scene.step()
            self.scene.update_render()
            self.viewer.render()

    def create_table(
        self,
        pose: sapien.Pose,
        size,
        height,
        thickness=0.1,
        color=(0.8, 0.6, 0.4),
        name="table",
    ) -> sapien.Entity:
        """Create a table (a collection of collision and visual shapes)."""
        builder = self.scene.create_actor_builder()

        # Tabletop
        tabletop_pose = sapien.Pose(
            [0.0, 0.0, -thickness / 2]
        )  # Make the top surface's z equal to 0
        tabletop_half_size = [size / 2, size , thickness / 2]
        builder.add_box_collision(pose=tabletop_pose, half_size=tabletop_half_size)
        builder.add_box_visual(
            pose=tabletop_pose, half_size=tabletop_half_size, material=color
        )

        # Table legs (x4)
        for i in [-1, 1]:
            for j in [-1, 1]:
                x = i * (size - thickness) / 2
                y = j * (size - thickness) 
                table_leg_pose = sapien.Pose([x, y, -height / 2])
                table_leg_half_size = [thickness / 2, thickness / 2, height / 2]
                builder.add_box_collision(
                    pose=table_leg_pose, half_size=table_leg_half_size
                )
                builder.add_box_visual(
                    pose=table_leg_pose, half_size=table_leg_half_size, material=color
                )

        table = builder.build(name=name)
        pose = sapien.Pose(pose)
        table.set_pose(pose)
        return table

    def add_obj(self,object_config,position,orientation):
        builder = self.scene.create_actor_builder()
        builder.add_convex_collision_from_file(
            filename=object_config['object_collision_meshes']
        )
        builder.add_visual_from_file(filename=object_config['object_visual_meshes'])
        mesh = builder.build(name="mesh")
        mesh.set_pose(sapien.Pose(p=position))