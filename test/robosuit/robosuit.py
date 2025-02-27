import mujoco
from robosuite.models import MujocoWorldBase
from robosuite.models.robots import Panda
from robosuite.models.grippers import gripper_factory
from robosuite.models.arenas import TableArena
from robosuite.models.objects import BallObject
from robosuite.utils.mjcf_utils import new_joint


# 创建世界基础框架
world = MujocoWorldBase()

# 创建机器人
mujoco_robot = Panda()

# 创建抓持器并添加到机器人上
gripper = gripper_factory('PandaGripper')
mujoco_robot.add_gripper(gripper)

# 设置机器人的位置
mujoco_robot.set_base_xpos([0, 0, 0])

# 将机器人合并到世界中
world.merge(mujoco_robot)

# 创建桌子
mujoco_arena = TableArena()

# 设置桌子的位置
mujoco_arena.set_origin([0.8, 0, 0])

# 将桌子合并到世界中
world.merge(mujoco_arena)

# 创建球对象
sphere = BallObject(
    name="sphere",
    size=[0.04],
    rgba=[0, 0.5, 0.5, 1]).get_obj()

# 设置球的位置
sphere.set('pos', '1.0 0 1.0')

# 将球添加到世界主体中
world.worldbody.append(sphere)

# 获取 Mujoco 模型
model = world.get_model(mode="mujoco")

# 创建 Mujoco 数据对象
data = mujoco.MjData(model)

# 运行模拟 1 秒
while data.time < 10:
    mujoco.mj_step(model, data)