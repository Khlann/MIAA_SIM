# Third Party
import torch

# cuRobo
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import RobotConfig
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.ik_solver import IKSolver, IKSolverConfig


tensor_args = TensorDeviceType()

config_file = load_yaml(join_path(get_robot_configs_path(), "franka.yml"))
urdf_file = config_file["robot_cfg"]["kinematics"][
    "urdf_path"
]  # Send global path starting with "/"
base_link = config_file["robot_cfg"]["kinematics"]["base_link"]
ee_link = config_file["robot_cfg"]["kinematics"]["ee_link"]
robot_cfg = RobotConfig.from_basic(urdf_file, base_link, ee_link, tensor_args)

ik_config = IKSolverConfig.load_from_robot_config(
    robot_cfg,
    None,
    rotation_threshold=0.05,
    position_threshold=0.005,
    num_seeds=20,
    self_collision_check=False,
    self_collision_opt=False,
    tensor_args=tensor_args,
    use_cuda_graph=True,
)
ik_solver = IKSolver(ik_config)

q_sample = ik_solver.sample_configs(5000)
kin_state = ik_solver.fk(q_sample)
goal = Pose(kin_state.ee_position, kin_state.ee_quaternion)
result = ik_solver.solve_batch(goal)
q_solution = result.solution[result.success]