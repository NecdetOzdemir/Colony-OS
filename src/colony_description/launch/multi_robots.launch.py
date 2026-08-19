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

    # 1. Gazebo simülasyonu
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen'
    )
    ld.add_action(gazebo)

    # 3 Adet Robot ve Başlangıç Konumları (AÇIK ALANDA - Raflardan tamamen uzakta)
    # Raflar X: -7.0 ile -1.0 arasında olduğu için robotları X: +2.0 bölgesinde açık alana koyuyoruz!
    workers = [
        {'id': 'worker_1', 'x': '2.0', 'y': '-2.5', 'z': '0.15'},
        {'id': 'worker_2', 'x': '2.0', 'y': '0.0', 'z': '0.15'},
        {'id': 'worker_3', 'x': '2.0', 'y': '2.5', 'z': '0.15'}
    ]

    for w in workers:
        worker_id = w['id']

        # URDF xacro parse with robot_name=worker_X
        doc = xacro.process_file(xacro_file, mappings={'robot_name': worker_id})
        robot_desc = doc.toprettyxml(indent='  ')

        # Robot State Publisher (Her robot için izole)
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

        # Spawn robot in Gazebo
        spawn_node = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', worker_id,
                '-topic', f'/{worker_id}/robot_description',
                '-x', w['x'],
                '-y', w['y'],
                '-z', w['z']
            ],
            output='screen'
        )

        # Gazebo <-> ROS 2 Köprüsü (Her robot için izole)
        bridge_node = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            namespace=worker_id,
            arguments=[
                '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
                '/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
                f'/{worker_id}/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
                f'/{worker_id}/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
                f'/{worker_id}/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
                f'/{worker_id}/wheel_joint_states@sensor_msgs/msg/JointState[ignition.msgs.Model'
            ],
            remappings=[
                (f'/{worker_id}/wheel_joint_states', f'/{worker_id}/joint_states')
            ],
            output='screen'
        )

        ld.add_action(rsp_node)
        ld.add_action(spawn_node)
        ld.add_action(bridge_node)

    return ld
