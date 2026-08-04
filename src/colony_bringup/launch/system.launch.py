import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    ld = LaunchDescription()

    # Paket yolları
    description_dir = get_package_share_directory('colony_description')
    navigation_dir = get_package_share_directory('colony_navigation')
    bringup_dir = get_package_share_directory('colony_bringup')
    
    world_file = os.path.join(description_dir, 'worlds', 'warehouse.sdf')
    xacro_file = os.path.join(description_dir, 'urdf', 'worker.urdf.xacro')

    doc = xacro.process_file(xacro_file)
    robot_desc = doc.toprettyxml(indent='  ')

    # 1. Gazebo
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen'
    )

    # 2. Robot State Publisher
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # 3. Gazebo-ROS Bridge
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'
        ],
        output='screen'
    )

    # 4. Nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(navigation_dir, 'launch', 'navigation.launch.py')
        )
    )

    # 5. Kraliçe (Queen Node)
    queen_node = Node(
        package='colony_queen',
        executable='queen',
        name='queen_node',
        output='screen'
    )

    # 6. Logger Node
    logger_node = Node(
        package='colony_logger',
        executable='logger',
        name='data_logger_node',
        output='screen'
    )

    # 7. İşçileri Spawn Et (Workers)
    spawn_workers = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(bringup_dir, 'launch', 'spawn_workers.launch.py')
        )
    )

    ld.add_action(gazebo)
    ld.add_action(rsp_node)
    ld.add_action(bridge_node)
    ld.add_action(nav2_launch)
    ld.add_action(queen_node)
    ld.add_action(logger_node)
    ld.add_action(spawn_workers)

    return ld
