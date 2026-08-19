import os
import sys
import xacro

# colony_config modülünü launch dosyası içinde okuyabilmek için
sys.path.append('/home/necdet/Colony-OS/src/colony_config/colony_config')
from config import CC

from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from nav2_common.launch import RewrittenYaml
from launch.actions import IncludeLaunchDescription, GroupAction, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import PushRosNamespace, SetRemap

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    xacro_file = os.path.join(description_dir, 'urdf', 'worker.urdf.xacro')
    
    num_workers = CC.NUM_WORKERS
    
    # Nav2'deki initial_pose ile eşleşmesi için ilk robot 4.0, 0.0 noktasında başlatılıyor.
    start_positions = [
        {'x': '4.0', 'y': '0.0', 'z': '0.15'},
        {'x': '-3.0', 'y': '6.0', 'z': '0.15'},
        {'x': '0.0',  'y': '6.0', 'z': '0.15'},
        {'x': '3.0',  'y': '6.0', 'z': '0.15'},
        {'x': '6.0',  'y': '6.0', 'z': '0.15'}
    ]

    for i in range(num_workers):
        worker_id = f'worker_{i+1}'
        pos = start_positions[i % len(start_positions)]

        # URDF xacro parse with robot_name
        doc = xacro.process_file(xacro_file, mappings={'robot_name': worker_id})
        robot_desc = doc.toprettyxml(indent='  ')

        # Robot State Publisher (Per Robot)
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

        # Spawn robot in Gazebo (Per Robot)
        spawn_node = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', worker_id,
                '-topic', f'/{worker_id}/robot_description',
                '-x', pos['x'],
                '-y', pos['y'],
                '-z', pos['z']
            ],
            output='screen'
        )

        # Gazebo-ROS Bridge (Per Robot)
        bridge_node = Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            namespace=worker_id,
            arguments=[
                f'/{worker_id}/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
                f'/model/{worker_id}/cmd_vel@geometry_msgs/msg/Twist]ignition.msgs.Twist',
                f'/model/{worker_id}/odometry@nav_msgs/msg/Odometry[ignition.msgs.Odometry',
                f'/model/{worker_id}/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V'
            ],
            remappings=[
                (f'/model/{worker_id}/cmd_vel', f'/{worker_id}/cmd_vel'),
                (f'/model/{worker_id}/odometry', f'/{worker_id}/odom'),
                (f'/model/{worker_id}/tf', '/tf')
            ],
            output='screen'
        )
        
        # Worker Node (AI)
        worker_ai_node = Node(
            package='colony_worker',
            executable='worker',
            name='worker_node',
            namespace=worker_id,
            parameters=[{'worker_id': worker_id}],
            output='screen'
        )

        # Stagger spawning to prevent Gazebo Lidar race condition
        delay_sec = float(i * 3.0)
        
        # Controllers (Arm)
        jsb_spawner = Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '-c', f'/{worker_id}/controller_manager'],
            output='screen'
        )

        arm_spawner = Node(
            package='controller_manager',
            executable='spawner',
            arguments=['arm_controller', '-c', f'/{worker_id}/controller_manager'],
            output='screen'
        )

        move_group_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('colony_moveit_config'), 'launch', 'move_group.launch.py')
            ),
            launch_arguments={'robot_name': worker_id}.items()
        )

        worker_group = GroupAction([
            rsp_node,
            spawn_node,
            bridge_node,
            worker_ai_node,
            TimerAction(period=5.0, actions=[jsb_spawner]),
            TimerAction(period=6.0, actions=[arm_spawner]),
            TimerAction(period=8.0, actions=[move_group_launch])
        ])

        delayed_worker_group = TimerAction(
            period=delay_sec,
            actions=[worker_group]
        )

        ld.add_action(delayed_worker_group)

    return ld
