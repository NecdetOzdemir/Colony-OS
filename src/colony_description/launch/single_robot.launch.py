import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    world_file = os.path.join(description_dir, 'worlds', 'warehouse.sdf')
    xacro_file = os.path.join(description_dir, 'urdf', 'worker.urdf.xacro')

    worker_id = 'worker_1'

    # URDF xacro parse with robot_name=worker_1
    doc = xacro.process_file(xacro_file, mappings={'robot_name': worker_id})
    robot_desc = doc.toprettyxml(indent='  ')

    # 1. Gazebo simülasyonu
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen'
    )

    # 2. Tek Robot için Robot State Publisher (worker_1)
    rsp_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        namespace=worker_id,
        output='screen',
        parameters=[{
            'robot_description': robot_desc, 
            'use_sim_time': True,
            'frame_prefix': f'{worker_id}/'
        }],
        remappings=[
            ('/tf', '/tf'),
            ('/tf_static', '/tf_static')
        ]
    )

    # 3. Gazebo'da Tek Robot Spawn Etme
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', worker_id,
            '-topic', f'/{worker_id}/robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15'
        ],
        output='screen'
    )

    # 4. Gazebo <-> ROS 2 Köprüsü (Sensörler, tf ve saat için)
    bridge_node = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        namespace=worker_id,
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
            f'/{worker_id}/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan'
        ],
        output='screen'
    )

    # 5. Controller Spawners (ros2_control)
    diff_drive_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace=worker_id,
        arguments=["diff_drive_controller", "-c", f"/{worker_id}/controller_manager"],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        namespace=worker_id,
        arguments=["joint_state_broadcaster", "-c", f"/{worker_id}/controller_manager"],
        output="screen",
    )

    ld.add_action(gazebo)
    ld.add_action(rsp_node)
    ld.add_action(spawn_node)
    ld.add_action(bridge_node)
    
    # Controllers should spawn after the spawn_node finishes, but for simplicity we add them here.
    # Typically we use RegisterEventHandler for this, but standard addition often works if ignition is fast.
    ld.add_action(diff_drive_spawner)
    ld.add_action(joint_state_broadcaster_spawner)

    return ld
