# Copyright (c) 2021 DENSO WAVE INCORPORATED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: DENSO WAVE INCORPORATED

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    model = LaunchConfiguration('model').perform(context)
    ip_address = LaunchConfiguration('ip_address').perform(context)
    send_format = LaunchConfiguration('send_format').perform(context)
    recv_format = LaunchConfiguration('recv_format').perform(context)
    bcap_slave_control_cycle_msec = LaunchConfiguration(
        'bcap_slave_control_cycle_msec').perform(context)
    description_package = LaunchConfiguration('description_package').perform(context)
    description_file = LaunchConfiguration('description_file').perform(context)
    moveit_config_package = LaunchConfiguration('moveit_config_package').perform(context)
    moveit_config_file = LaunchConfiguration('moveit_config_file').perform(context)
    namespace = LaunchConfiguration('namespace').perform(context)
    rviz = LaunchConfiguration('rviz').perform(context)
    sim = LaunchConfiguration('sim').perform(context)
    basic_camera = LaunchConfiguration('basic_camera').perform(context)
    verbose = LaunchConfiguration('verbose').perform(context)
    controllers_file = LaunchConfiguration('controllers_file').perform(context)
    robot_controller = LaunchConfiguration('robot_controller').perform(context)
    xyz = LaunchConfiguration('xyz').perform(context)
    rpy = LaunchConfiguration('rpy').perform(context)

    # Evaluate robot description once (runs xacro)
    robot_description_str = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]), ' ',
        PathJoinSubstitution(
            [FindPackageShare(description_package), 'urdf', description_file]),
        ' ',
        'ip_address:=', ip_address, ' ',
        'model:=', model, ' ',
        'send_format:=', send_format, ' ',
        'recv_format:=', recv_format, ' ',
        'namespace:=', namespace, ' ',
        'verbose:=', verbose, ' ',
        'sim:=', sim, ' ',
        'basic_camera:=', basic_camera, ' ',
        'xyz:="', xyz, '" ',
        'rpy:="', rpy, '" '
    ]).perform(context)

    # Evaluate semantic description once (runs xacro)
    robot_description_semantic_str = Command([
        PathJoinSubstitution([FindExecutable(name='xacro')]), ' ',
        PathJoinSubstitution(
            [FindPackageShare(moveit_config_package), 'srdf', moveit_config_file]),
        ' ',
        'model:=', model, ' ',
        'namespace:=', namespace, ' '
    ]).perform(context)

    # Compute configuration file paths
    moveit_share = get_package_share_directory(moveit_config_package)
    bringup_share = get_package_share_directory('denso_robot_bringup')
    includes_dir = os.path.join(bringup_share, 'launch', 'includes')

    kinematics_yaml_file = os.path.join(moveit_share, 'config', 'kinematics.yaml')
    moveit_controllers_file = os.path.join(
        moveit_share, 'robots', model, 'config', 'moveit_controllers.yaml')
    robot_limits_file = os.path.join(
        moveit_share, 'robots', model, 'config', 'joint_limits.yaml')
    robot_controllers_file = os.path.join(
        moveit_share, 'robots', model, 'config', controllers_file)
    rviz_config_file = os.path.join(moveit_share, 'rviz', 'view_robot.rviz')

    # Static TF: world -> <namespace>base_link  (namespace is a plain prefix, not a path)
    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='log',
        arguments=[
            '--frame-id', 'world',
            '--child-frame-id', namespace + 'base_link'
        ])

    # --- Include sub-launch files ---

    robot_state_publisher_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'robot_state_publisher.launch.py')),
        launch_arguments={
            'robot_description': robot_description_str,
            'sim': sim,
        }.items())

    controllers_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'controllers.launch.py')),
        launch_arguments={
            'robot_description': robot_description_str,
            'robot_controllers_file': robot_controllers_file,
            'bcap_slave_control_cycle_msec': bcap_slave_control_cycle_msec,
            'sim': sim,
            'controllers': robot_controller,
        }.items())

    moveit_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'moveit.launch.py')),
        launch_arguments={
            'robot_description': robot_description_str,
            'robot_description_semantic': robot_description_semantic_str,
            'moveit_config_package': moveit_config_package,
            'kinematics_yaml_file': kinematics_yaml_file,
            'moveit_controllers_file': moveit_controllers_file,
            'robot_limits_file': robot_limits_file,
            'sim': sim,
        }.items())

    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'rviz.launch.py')),
        launch_arguments={
            'rviz': rviz,
            'robot_description': robot_description_str,
            'robot_description_semantic': robot_description_semantic_str,
            'moveit_config_package': moveit_config_package,
            'kinematics_yaml_file': kinematics_yaml_file,
            'rviz_config_file': rviz_config_file,
        }.items())

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'gazebo.launch.py')),
        launch_arguments={
            'sim': sim,
            'basic_camera': basic_camera,
            'model': model,
            'camera_topics': '/basic_camera',
        }.items())

    servo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(includes_dir, 'servo.launch.py')),
        launch_arguments={
            'robot_description': robot_description_str,
            'robot_description_semantic': robot_description_semantic_str,
            'moveit_config_package': moveit_config_package,
            'kinematics_yaml_file': kinematics_yaml_file,
            'sim': sim,
            'servo_node_name': 'servo_node_main',
        }.items())

    return [
        static_tf,
        robot_state_publisher_launch,
        controllers_launch,
        moveit_launch,
        rviz_launch,
        gazebo_launch,
        servo_launch,
    ]


def generate_launch_description():

    declared_arguments = []

    # Denso-specific arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            'model',
            choices=['vs050', 'vs060'],
            description='Type/series of used denso robot.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'send_format', default_value='288',
            description='Data format for sending commands to the robot.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'recv_format', default_value='292',
            description='Data format for receiving robot status.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'bcap_slave_control_cycle_msec', default_value='8.0',
            description='Control frequency.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'ip_address', default_value='192.168.0.1',
            description='IP address by which the robot can be reached.'))

    # Configuration arguments
    declared_arguments.append(
        DeclareLaunchArgument(
            'description_package', default_value='denso_robot_descriptions',
            description='Description package with robot URDF/XACRO files. Usually the argument'
                + ' is not set, it enables use of a custom description.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'description_file', default_value='denso_robot.urdf.xacro',
            description='URDF/XACRO description file with the robot.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'moveit_config_package', default_value='denso_robot_moveit_config',
            description='MoveIt config package with robot SRDF/XACRO files. Usually the argument'
                + ' is not set, it enables use of a custom moveit config.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'moveit_config_file', default_value='denso_robot.srdf.xacro',
            description='MoveIt SRDF/XACRO description file with the robot.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'namespace', default_value='',
            description='Prefix of the joint names, useful for'
                + ' multi-robot setup. If changed then also joint names in the controllers\''
                + ' configuration have to be updated.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'controllers_file', default_value='denso_robot_controllers.yaml',
            description='YAML file with the controllers configuration.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'robot_controller', default_value='denso_joint_trajectory_controller',
            description='Robot controller to start.'))
    declared_arguments.append(
        DeclareLaunchArgument('rviz', default_value='false', description='Launch RViz?'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'sim', default_value='true',
            description='Start robot with fake hardware mirroring command to its states.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'verbose', default_value='false',
            description='Print out additional debug information.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'basic_camera', default_value='false',
            description='Add basic_camera in J6.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'xyz', default_value='0 0 0',
            description='XYZ position of arm.'))
    declared_arguments.append(
        DeclareLaunchArgument(
            'rpy', default_value='0 0 0',
            description='RPY orientation of arm.'))

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
