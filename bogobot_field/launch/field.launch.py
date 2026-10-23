import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    pkg_share = get_package_share_directory('bogobot_field')
    world = LaunchConfiguration('world')

    return LaunchDescription([
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_share, 'worlds', 'robocup_field.sdf'),
            description='Ruta al mundo SDF'),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.join(pkg_share, 'models')),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(PathJoinSubstitution(
                [FindPackageShare('ros_gz_sim'), 'launch', 'gz_sim.launch.py'])),
            launch_arguments={'gz_args': [world, ' -r'], 'on_exit_shutdown': 'true'}.items()),
    ])
