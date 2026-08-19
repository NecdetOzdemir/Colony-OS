import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    ld = LaunchDescription()

    description_dir = get_package_share_directory('colony_description')
    world_file = os.path.join(description_dir, 'worlds', 'warehouse.sdf')

    # 1. Gazebo simülasyon motoru (Sadece dünya, SIFA robot yok)
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_file, '-r'],
        output='screen'
    )

    # 2. ROS 2 <-> Gazebo Zaman Köprüsü (/clock)
    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock'],
        output='screen'
    )

    ld.add_action(gazebo)
    ld.add_action(clock_bridge)
    return ld
