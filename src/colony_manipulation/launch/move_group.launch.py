import os
import yaml
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    with open(absolute_file_path, 'r') as file:
        return yaml.safe_load(file)

def generate_launch_description():
    description_pkg_path = get_package_share_directory('colony_description')
    manipulation_pkg_path = get_package_share_directory('colony_manipulation')
    
    # Robot Description
    xacro_file = os.path.join(description_pkg_path, 'urdf', 'worker.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_description = {'robot_description': doc.toprettyxml(indent='  ')}
    
    # SRDF
    with open(os.path.join(manipulation_pkg_path, 'config', 'worker.srdf'), 'r') as f:
        robot_description_semantic = {'robot_description_semantic': f.read()}
        
    # Kinematics
    kinematics_yaml = load_yaml('colony_manipulation', 'config/kinematics.yaml')
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}

    # Joint Limits
    joint_limits_yaml = load_yaml('colony_manipulation', 'config/joint_limits.yaml')
    robot_description_planning = {'robot_description_planning': joint_limits_yaml}

    # MoveIt controllers
    moveit_controllers = load_yaml('colony_manipulation', 'config/moveit_controllers.yaml')
    moveit_controllers_dict = {
        'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager',
        'moveit_manage_controllers': True
    }
    moveit_controllers_dict.update(moveit_controllers)
    
    # Trajectory Execution
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    # Move Group Node
    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            trajectory_execution,
            moveit_controllers_dict,
            {'use_sim_time': True}
        ],
    )

    # Spawn Controllers for ros2_control (in Gazebo)
    spawn_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "-c", "/controller_manager"],
        output="screen",
    )
    spawn_arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "-c", "/controller_manager"],
        output="screen",
    )

    return LaunchDescription([
        run_move_group_node,
        spawn_joint_state_broadcaster,
        spawn_arm_controller
    ])
