import sapien


def demo(fix_root_link, balance_passive_force):
    scene = sapien.Scene()
    scene.add_ground(0)

    scene.set_ambient_light([0.5, 0.5, 0.5])
    scene.add_directional_light([0, 1, -1], [0.5, 0.5, 0.5])

    viewer = scene.create_viewer()
    viewer.set_camera_xyz(x=-2, y=0, z=1)
    viewer.set_camera_rpy(r=0, p=-0.3, y=0)

    # Load URDF
    loader = scene.create_urdf_loader()
    loader.fix_root_link = fix_root_link
    robot = loader.load("asset/robot_description/panda/panda_v2.urdf")
    robot.set_root_pose(sapien.Pose([0, 0, 0], [1, 0, 0, 0]))

    while not viewer.closed:
        for _ in range(4):  # render every 4 steps
            if balance_passive_force:
                qf = robot.compute_passive_force(
                    gravity=True,
                    coriolis_and_centrifugal=True,
                )
                robot.set_qf(qf)
            scene.step()
        scene.update_render()
        viewer.render()


def main():
    demo(
        fix_root_link=True,
        balance_passive_force=True,
    )


if __name__ == "__main__":
    main()