import numpy as np
import gymnasium as gym
import sapien
from mani_skill.envs.sapien_env import BaseEnv
from mani_skill.utils import gym_utils
# choose random task
env_name = "Empty-v1"
# env_name = "TurnFaucet-v1"
# env_name = "PickClutterYCB-v1"

env = gym.make(
    env_name,
    render_mode = "human",
    robot_uids="panda",
    sensor_configs=dict(shader_pack="default"),
    human_render_camera_configs=dict(shader_pack="default"),
    init_robot_base_pos = sapien.Pose([-0.6, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]),
)

# reset the environment
env.reset()

for j in range(1000):

    for i in range(50):
        # action = env.action_space.sample() if env.action_space is not None else None
        action = np.array([0.0 for _ in range(8)])
        obs, reward, terminated, truncated, info = env.step(action)  # take action in the environment
        env.render()  # render on display
    env.reset()  # reset the environment