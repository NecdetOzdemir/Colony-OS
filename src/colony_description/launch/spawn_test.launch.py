import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_dir = get_package_share_directory('colony_description')
    
    # 1. World file
    world_file = os.path.join(pkg_dir, 'worlds', 'warehouse.sdf')
    
    # 2. Xacro to URDF string
    xacro_file = os.path.join(pkg_dir, 'urdf', 'worker.urdf.xacro')
    doc = xacro.process_file(xacro_file)
    robot_desc = doc.toprettyxml(indent='  ')

    # 3. Robot State Publisher
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc}]
    )

    # 4. Ignition Gazebo 
    ign_gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', world_file],
        output='screen'
    )

    # 5. Spawn Robot in Gazebo
    # Use ros_gz_sim create (Ignition Gazebo uses ros_gz_sim for this)
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=['-string', robot_desc,
                   '-name', 'worker_1',
                   '-allow_renaming', 'true',
                   '-x', '0.0', '-y', '0.0', '-z', '0.5']
    )

    # 6. Bridge (ROS 2 <-> Gazebo)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V'
        ],
        output='screen'
    )

    return LaunchDescription([
        node_robot_state_publisher,
        ign_gazebo,
        spawn_entity,
        bridge
    ])
