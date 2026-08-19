import os
import subprocess
import yaml
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, SetRemap
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    bringup_dir = get_package_share_directory('colony_bringup')
    
    world_file = os.path.join(description_dir, 'worlds', 'warehouse.sdf')

    # Ensure Gazebo can find ign_ros2_control plugin
    ign_plugin_path = os.environ.get('IGN_GAZEBO_SYSTEM_PLUGIN_PATH', '')
    ign_plugin_path += ':/opt/ros/humble/lib' if ign_plugin_path else '/opt/ros/humble/lib'

    # 1. Gazebo
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen',
        additional_env={
            'LIBGL_ALWAYS_SOFTWARE': '1',
            'IGN_GAZEBO_SYSTEM_PLUGIN_PATH': ign_plugin_path
        }
    )

    # 2. Global Bridges (Clock)
    global_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.gmsgs.Clock'
        ],
        output='screen'
    )

    # 3. Kraliçe (Queen Node)
    queen_node = Node(
        package='colony_queen',
        executable='queen',
        name='queen_node',
        output='screen'
    )

    # 4. Logger Node
    logger_node = Node(
        package='colony_logger',
        executable='logger',
        name='data_logger_node',
        output='screen'
    )

    # 5. İşçileri Spawn Et (Workers)
    spawn_workers = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'spawn_workers.launch.py')
        )
    )

    # 6. Map Server (Aşama 5.2)
    nav_dir = get_package_share_directory('colony_navigation')
    map_yaml_file = os.path.join(nav_dir, 'maps', 'warehouse.yaml')
    
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'yaml_filename': map_yaml_file}
        ]
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
            {
                'use_sim_time': True,
                'base_frame_id': 'worker_1/base_link',
                'odom_frame_id': 'worker_1/odom',
                'global_frame_id': 'map',
                'scan_topic': '/worker_1/scan'
            }
        ],
        remappings=[
            ('/tf', 'tf'),
            ('/tf_static', 'tf_static'),
            ('/initialpose', '/worker_1/initialpose')
        ]
    )
    
    lifecycle_manager_map = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map',
        output='screen',
        parameters=[
            {'use_sim_time': True},
            {'autostart': True},
            {'node_names': ['map_server', 'amcl']},
            {'bond_timeout': 60.0}
        ]
    )

    delayed_map_lifecycle = TimerAction(
        period=5.0,
        actions=[lifecycle_manager_map]
    )

    # Load URDF and SRDF for RViz
    xacro_file = os.path.join(description_dir, 'urdf', 'worker.urdf.xacro')
    robot_description_config = subprocess.check_output(['xacro', xacro_file, 'robot_name:=worker_1']).decode('utf-8')
    
    srdf_file = os.path.join(get_package_share_directory('colony_moveit_config'), 'config', 'worker.srdf')
    with open(srdf_file, 'r') as f:
        semantic_content = f.read()

    kinematics_file = os.path.join(get_package_share_directory('colony_moveit_config'), 'config', 'kinematics.yaml')
    with open(kinematics_file, 'r') as f:
        kinematics_content = yaml.safe_load(f)

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', os.path.join(bringup_dir, 'rviz', 'worker.rviz')],
        parameters=[
            {'robot_description': robot_description_config},
            {'robot_description_semantic': semantic_content},
            {'robot_description_kinematics': kinematics_content}
        ],
        output='screen'
    )

    # 7. Nav2 Otonom Sürüş (Aşama 5.4)
    nav2_navigation = GroupAction(
        actions=[
            SetRemap(src='/cmd_vel', dst='/worker_1/cmd_vel'),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'True',
                    'params_file': os.path.join(nav_dir, 'config', 'nav2_params.yaml'),
                    'autostart': 'True'
                }.items()
            )
        ]
    )

    delayed_nav2_navigation = TimerAction(
        period=8.0,
        actions=[nav2_navigation]
    )

    ld.add_action(gazebo)
    ld.add_action(global_bridge)
    ld.add_action(queen_node)
    ld.add_action(logger_node)
    ld.add_action(spawn_workers)
    ld.add_action(map_server_node)
    ld.add_action(amcl_node)
    ld.add_action(delayed_map_lifecycle)
    ld.add_action(rviz_node)
    ld.add_action(delayed_nav2_navigation)

    return ld
