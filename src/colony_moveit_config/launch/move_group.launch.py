import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import yaml

def load_file(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return file.read()
    except EnvironmentError:
        return None

def load_yaml(package_name, file_path):
    package_path = get_package_share_directory(package_name)
    absolute_file_path = os.path.join(package_path, file_path)
    try:
        with open(absolute_file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError:
        return None

import subprocess

def generate_launch_description():
    robot_name = LaunchConfiguration('robot_name')
    robot_name_arg = DeclareLaunchArgument('robot_name', default_value='worker_1')

    # Execute xacro to get URDF string (using subprocess at launch time isn't dynamic with LaunchConfiguration)
    # Since we need this string in parameters, it's easier to just assume worker_1 for now or execute it directly.
    # We will hardcode worker_1 in this script for simplicity for Phase 6.
    xacro_file = os.path.join(get_package_share_directory('colony_description'), 'urdf', 'worker.urdf.xacro')
    robot_description_config = subprocess.check_output(['xacro', xacro_file, 'robot_name:=worker_1']).decode('utf-8')
    robot_description = {'robot_description': robot_description_config}

    robot_description_semantic_config = load_file(
        'colony_moveit_config', 'config/worker.srdf'
    )
    robot_description_semantic = {
        'robot_description_semantic': robot_description_semantic_config
    }

    kinematics_yaml = load_yaml(
        'colony_moveit_config', 'config/kinematics.yaml'
    )
    robot_description_kinematics = {'robot_description_kinematics': kinematics_yaml}
    
    controllers_yaml_path = os.path.join(
        get_package_share_directory('colony_moveit_config'), 'config', 'moveit_controllers.yaml'
    )

    joint_limits_yaml = load_yaml(
        'colony_moveit_config', 'config/joint_limits.yaml'
    )
    robot_description_planning = {
        'robot_description_planning': joint_limits_yaml
    }

    ompl_yaml = load_yaml('colony_moveit_config', 'config/ompl_planning.yaml')
    ompl_planning_pipeline_config = {
        'move_group': {
            'planning_plugin': 'ompl_interface/OMPLPlanner',
            'request_adapters': 'default_planner_request_adapters/AddTimeOptimalParameterization default_planner_request_adapters/FixWorkspaceBounds default_planner_request_adapters/FixStartStateBounds default_planner_request_adapters/FixStartStateCollision default_planner_request_adapters/FixStartStatePathConstraints',
            'start_state_max_bounds_error': 0.1,
        }
    }
    if ompl_yaml:
        ompl_planning_pipeline_config.update(ompl_yaml)

    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 2.0,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.0
    }

    # move_group Node
    run_move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            robot_description,
            robot_description_semantic,
            robot_description_kinematics,
            robot_description_planning,
            ompl_planning_pipeline_config,
            controllers_yaml_path,
            trajectory_execution,
            {'use_sim_time': True}
        ],
        namespace=robot_name
    )

    # MoveIt'in öneki olmayan (unprefixed) base_link'i bulabilmesi için TF köprüsü
    tf_bridge_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='moveit_tf_bridge',
        arguments=['0', '0', '0', '0', '0', '0', [LaunchConfiguration('robot_name'), '/base_link'], 'base_link'],
        output='screen'
    )

    return LaunchDescription([robot_name_arg, run_move_group_node, tf_bridge_node])
