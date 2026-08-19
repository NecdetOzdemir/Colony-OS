import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import xacro

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    navigation_dir = get_package_share_directory('colony_navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    
    world_file = os.path.join(description_dir, 'worlds', 'warehouse.sdf')
    xacro_file = os.path.join(description_dir, 'urdf', 'worker.urdf.xacro')
    map_yaml_file = os.path.join(navigation_dir, 'maps', 'warehouse.yaml')
    nav2_params_file = os.path.join(navigation_dir, 'config', 'nav2_params.yaml')

    worker_id = 'worker_1'

    # 1. Gazebo simülasyonu
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen'
    )

    # URDF xacro parse with robot_name=worker_1
    doc = xacro.process_file(xacro_file, mappings={'robot_name': worker_id})
    robot_desc = doc.toprettyxml(indent='  ')

    # 2. Robot State Publisher (worker_1)
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

    # 3. Gazebo'da worker_1 Spawn Etme (Açık Alanda)
    spawn_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', worker_id,
            '-topic', f'/{worker_id}/robot_description',
            '-x', '2.0',
            '-y', '0.0',
            '-z', '0.15'
        ],
        output='screen'
    )

    # 4. Gazebo <-> ROS 2 Köprüsü
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

    # 5. Nav2 Otonom Navigasyon Stack
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': map_yaml_file,
            'use_sim_time': 'true',
            'params_file': nav2_params_file,
            'autostart': 'true'
        }.items()
    )

    # 6. RViz2 Görselleştirme
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', os.path.join(nav2_bringup_dir, 'rviz', 'nav2_default_view.rviz')]
    )

    ld.add_action(gazebo)
    ld.add_action(rsp_node)
    ld.add_action(spawn_node)
    ld.add_action(bridge_node)
    ld.add_action(nav2_bringup)
    ld.add_action(rviz_node)

    return ld
