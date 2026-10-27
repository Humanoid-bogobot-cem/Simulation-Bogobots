from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FileContent, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.descriptions import ParameterValue


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    urdf = FileContent(
        PathJoinSubstitution([FindPackageShare('bogobot_rviz'),'urdf','humanoid_main.urdf']))
    rviz_config = PathJoinSubstitution([FindPackageShare('bogobot_rviz'), 'urdf', 'rviz_conf.rviz'])
    #path_to_urdf = get_package_share_path('robot_simulation') / 'urdf' / 'humanoid_main.urdf'

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': urdf}]),
        Node(
            package='bogobot_rviz',
            executable='joint_publisher',
            name='joint_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}]),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}]),
    ])
