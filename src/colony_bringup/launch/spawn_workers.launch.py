import os
import sys

# colony_config modülünü launch dosyası içinde okuyabilmek için
sys.path.append('/home/necdet/Colony-OS/src/colony_config/colony_config')
from config import CC

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription, GroupAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import PushRosNamespace

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    
    num_workers = CC.NUM_WORKERS
    
    # Her robot için başlangıç pozisyonları
    start_positions = [
        {'x': '0.0', 'y': '0.0', 'z': '0.1'},
        {'x': '0.0', 'y': '1.0', 'z': '0.1'},
        {'x': '0.0', 'y': '-1.0', 'z': '0.1'},
        {'x': '1.0', 'y': '0.0', 'z': '0.1'},
        {'x': '1.0', 'y': '1.0', 'z': '0.1'}
    ]

    for i in range(num_workers):
        worker_id = f'worker_{i+1}'
        pos = start_positions[i % len(start_positions)]

        # Spawn robot in Gazebo
        spawn_node = Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-name', worker_id,
                '-topic', 'robot_description', # This uses the global robot_description for now
                '-x', pos['x'],
                '-y', pos['y'],
                '-z', pos['z']
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

        ld.add_action(spawn_node)
        ld.add_action(worker_ai_node)

    return ld
