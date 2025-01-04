import pybullet as p
import pybullet_data
import time

def control_joint(robot_id, joint_name, target_position, max_force=500):
    """
    Control a specific joint to move to a target position.
    
    :param robot_id: The ID of the robot in the simulation.
    :param joint_name: The name of the joint to control.
    :param target_position: The target position for the joint.
    :param max_force: The maximum force to apply to the joint.
    """
    num_joints = p.getNumJoints(robot_id)
    
    for joint_index in range(num_joints):
        joint_info = p.getJointInfo(robot_id, joint_index)
        current_joint_name = joint_info[1].decode('utf-8')
        
        if current_joint_name == joint_name:
            p.setJointMotorControl2(
                bodyIndex=robot_id,
                jointIndex=joint_index,
                controlMode=p.POSITION_CONTROL,
                targetPosition=target_position,
                force=max_force
            )
            break

# Connect to PyBullet's physics server
p.connect(p.GUI)

# Set the search path to find URDF files
p.setAdditionalSearchPath(pybullet_data.getDataPath())

# Load the ground plane
plane_id = p.loadURDF("plane.urdf")

# Load the URDF file
# Replace 'hand_left.urdf' with the path to your URDF file
robot_id = p.loadURDF("/home/arlen/arlen/fyp/hand_left.urdf")

# Example usage of control_joint
joint_name_to_control = "a1"  # Replace with the actual joint name you want to control
target_position = 0.5  # Replace with the desired target position for the joint

# Control the joint
control_joint(robot_id, joint_name_to_control, target_position)
# Get the number of joints
num_joints = p.getNumJoints(robot_id)

# Print joint information and initial values
for joint_index in range(num_joints):
    joint_info = p.getJointInfo(robot_id, joint_index)
    joint_name = joint_info[1].decode('utf-8')  # Joint name is in bytes, decode to string
    joint_state = p.getJointState(robot_id, joint_index)
    joint_position = joint_state[0]  # Get the joint position
    print(f"Joint {joint_index}: {joint_name}, Initial Position: {joint_position}")
    
# Optionally, set the gravity for the simulation
p.setGravity(0, 0, -9.81)

# Run the simulation for a few seconds
for _ in range(10000):
    p.stepSimulation()
    time.sleep(1./240.)  # Sleep to simulate real-time

# Disconnect from the physics server
p.disconnect()