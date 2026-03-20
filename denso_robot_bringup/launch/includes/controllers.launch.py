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
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def launch_setup(context, *args, **kwargs):
    robot_description = LaunchConfiguration("robot_description").perform(context)
    robot_controllers_file = LaunchConfiguration("robot_controllers_file").perform(context)
    bcap_slave_control_cycle_msec = LaunchConfiguration(
        "bcap_slave_control_cycle_msec").perform(context)
    sim = LaunchConfiguration("sim").perform(context)
    controllers = LaunchConfiguration("controllers").perform(context).split()

    denso_robot_core_pkg = get_package_share_directory("denso_robot_core")

    denso_robot_control_parameters = {
        "denso_bcap_slave_control_cycle_msec": bcap_slave_control_cycle_msec,
        "denso_config_file": PathJoinSubstitution(
            [denso_robot_core_pkg, "config", "config.xml"])
    }

    control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        condition=UnlessCondition(sim),
        parameters=[
            {"robot_description": robot_description},
            robot_controllers_file,
            denso_robot_control_parameters
        ],
        output={
            "stdout": "screen",
            "stderr": "screen",
        })

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["denso_joint_state_broadcaster", "--controller-manager", "/controller_manager"])

    controller_spawners = [
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[ctrl, "-c", "/controller_manager"])
        for ctrl in controllers
    ]

    return [control_node, joint_state_broadcaster_spawner] + controller_spawners


def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            "robot_description", default_value="",
            description="URDF robot description as a string."),
        DeclareLaunchArgument(
            "robot_controllers_file", default_value="",
            description="Full path to the controllers YAML configuration file."),
        DeclareLaunchArgument(
            "bcap_slave_control_cycle_msec", default_value="8.0",
            description="Control cycle in milliseconds."),
        DeclareLaunchArgument(
            "sim", default_value="true",
            description="Simulation mode (skips the hardware ros2_control_node)."),
        DeclareLaunchArgument(
            "controllers", default_value="denso_joint_trajectory_controller",
            description="Space-separated list of controller names to spawn."),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
