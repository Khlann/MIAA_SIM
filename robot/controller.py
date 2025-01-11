import sapien
import cv2
import time

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
        # 创建物理材质
        material = self.scene.create_physical_material(
            static_friction=0.9,    # 静摩擦系数
            dynamic_friction=0.9,   # 动摩擦系数
            restitution=0.1        # 弹性系数
        )
        
        # 设置加载器的默认物理材质
        loader.default_physical_material = material
        object = loader.load(object_config['object_description'])
        object.set_root_pose(sapien.Pose(position,orientation))
        return object
    def add_multiple_objects(self):
        
        loader = self.scene.create_urdf_loader()
        loader.fix_root_link = True
        
        # 加载第一个物体
        obj1_config = {
            'object_description': '/home/arlen/arlen/fyp/asset/robot_description/panda/panda_v3.urdf',
            'position': [0.5, 0, 0],
            'orientation': [1, 0, 0, 0]
        }
        # object1 = loader.load(obj1_config['object_description'])
        # object1.set_root_pose(sapien.Pose(obj1_config['position'], obj1_config['orientation']))
        
        # 加载第二个物体
        obj2_config = {
            'object_description': '/home/arlen/arlen/fyp/asset/robot_description/xarm7_m/xarm7.urdf',
            'position': [0.2, 0, 0],
            'orientation': [1, 0, 0, 0]
        }
        # object2 = loader.load(obj2_config['object_description'])
        # object2.set_root_pose(sapien.Pose(obj2_config['position'], obj2_config['orientation']))
        object1 = loader.load_multiple(obj1_config['object_description'])
        object2 = loader.load_multiple(obj2_config['object_description'])
        object1[0][0].set_root_pose(sapien.Pose(obj1_config['position'], obj1_config['orientation']))
        object2[0][0].set_root_pose(sapien.Pose(obj2_config['position'], obj2_config['orientation']))
        return object1[0][0],object2[0][0]
        # objects = loader.load_multiple(obj1_config['object_description'])  
        # for obj in objects:
        #     obj.set_root_pose(sapien.Pose(obj1_config['position'], obj1_config['orientation']))
        # 使用 load_multiple 替代 load
        # objects1 = loader.load_multiple(obj1_config['object_description'])
        # for obj in objects1:
        #     #去list化
        #     obj = obj[0]
        #     obj.set_root_pose(sapien.Pose(obj1_config['position'], obj1_config['orientation']))
        
        # objects2 = loader.load_multiple(obj2_config['object_description'])
        # for obj in objects2:
        #     obj.set_root_pose(sapien.Pose(obj2_config['position'], obj2_config['orientation']))
        
        # return objects1, objects2    
    
    def set_robot_pose(self,object,arm):
        # arm_init_qpos = [4.71, 2.84, 0, 0.75, 4.62, 4.48, 4.88]
        # gripper_init_qpos = [0, 0, 0, 0, 0, 0]
        # init_qpos = arm_init_qpos + gripper_init_qpos

        qpos = arm 
        object.set_qpos(qpos)
            
    def visualize(self,objects):
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
                    # qf = object.compute_passive_force(
                    #     gravity=True,
                    #     coriolis_and_centrifugal=False,
                    # )
                    # object.set_qf(qf)
                    # for obj in objects:
                    #     qf = obj.compute_passive_force(
                    #         gravity=True,
                    #         coriolis_and_centrifugal=False,
                    #     )
                    #     obj.set_qf(qf)
                    pass
                self.scene.step()
            self.scene.update_render()
            self.viewer.render()
    def create_box(
        self,
        pose,
        half_size,
        color=None,
        name="",
    ) -> sapien.Entity:
        """Create a box.

        Args:
            scene: sapien.Scene to create a box.
            pose: 6D pose of the box.
            half_size: [3], half size along x, y, z axes.
            color: [4], rgba
            name: name of the actor.

        Returns:
            sapien.Entity
        """
        entity = sapien.Entity()
        entity.set_name(name)
        pose = sapien.Pose(pose)
        entity.set_pose(pose)

        # create PhysX dynamic rigid body
        rigid_component = sapien.physx.PhysxRigidDynamicComponent()
        material = self.scene.create_physical_material(
            static_friction=0.9,
            dynamic_friction=0.9,
            restitution=0.1
        )
        rigid_component.attach(
            sapien.physx.PhysxCollisionShapeBox(
                half_size=half_size, material=material
            )
        )

        # create render body for visualization
        render_component = sapien.render.RenderBodyComponent()
        render_component.attach(
            # add a box visual shape with given size and rendering material
            sapien.render.RenderShapeBox(
                half_size, sapien.render.RenderMaterial(base_color=[*color[:3], 1])
            )
        )

        entity.add_component(rigid_component)
        entity.add_component(render_component)
        entity.set_pose(pose)

        # in general, entity should only be added to scene after it is fully built
        self.scene.add_entity(entity)

        # name and pose may be changed after added to scene
        # entity.set_name(name)
        # entity.set_pose(pose)

        return entity
    
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
        mesh = builder.build_dynamic(name="mesh")
        mesh.set_pose(sapien.Pose(p=position))
        # mesh.set_material(sapien.PxMaterial(
        #     static_friction=0.5,
        #     dynamic_friction=0.3,
        #     restitution=0.1
        # ))
        
        return mesh

    def visualize_trajectory(self, object, pose1, pose2, steps=100):
        """
        Visualize robot movement from pose1 to pose2 with real-time joint state printing
        
        Args:
            object: robot object
            pose1: starting pose
            pose2: target pose
            steps: number of interpolation steps
        """
        import numpy as np
        import time
        
        # Linear interpolation between poses
        for step in range(steps):
            # Calculate interpolated pose
            alpha = step / steps
            current_pose = [p1 + (p2 - p1) * alpha 
                          for p1, p2 in zip(pose1, pose2)]
            
            # Set robot pose
            object.set_qpos(current_pose)
            
            # Get current joint states
            current_qpos = object.get_qpos()
            current_qvel = object.get_qvel()
            
            # Print joint states
            print("\nStep:", step)
            print("Joint Positions:")
            for i, pos in enumerate(current_qpos):
                print(f"Joint {i}: {pos:.4f}")
            print("\nJoint Velocities:")
            for i, vel in enumerate(current_qvel):
                print(f"Joint {i}: {vel:.4f}")
            
            # Physics simulation steps
            for _ in range(4):
                qf = object.compute_passive_force(
                    gravity=True,
                    coriolis_and_centrifugal=True,
                )
                object.set_qf(qf)
                self.scene.step()
            
            # Render
            self.scene.update_render()
            self.viewer.render()
            
            # Add delay to slow down the movement
            # time.sleep(0.1)  # 增加 0.1 秒延迟
    
    # def visualize_trajectory_close_gripper(self, object, pose1, pose2):
        # 