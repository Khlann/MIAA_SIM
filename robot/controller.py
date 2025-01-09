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
        qpos = arm 
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