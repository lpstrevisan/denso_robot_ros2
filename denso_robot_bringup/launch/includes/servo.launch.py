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
import sys
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

# Import shared utilities from parent launch directory
_launch_dir = os.path.join(get_package_share_directory("denso_robot_bringup"), "launch")
if _launch_dir not in sys.path:
    sys.path.insert(0, _launch_dir)
from launch_utils import load_yaml  # noqa: E402


def launch_setup(context, *args, **kwargs):
    robot_description = LaunchConfiguration("robot_description").perform(context)
    robot_description_semantic = LaunchConfiguration(
        "robot_description_semantic").perform(context)
    moveit_config_package = LaunchConfiguration("moveit_config_package").perform(context)
    kinematics_yaml_file = LaunchConfiguration("kinematics_yaml_file").perform(context)
    sim = LaunchConfiguration("sim").perform(context).lower() == "true"
    servo_node_name = LaunchConfiguration("servo_node_name").perform(context)

    servo_yaml = load_yaml(moveit_config_package, "config/moveit_servo.yaml")
    servo_params = {
        "moveit_servo": servo_yaml,
        "moveit_servo.use_gazebo": sim
    }

    # Apply optional overrides for multi-arm configurations
    override_map = {
        "moveit_servo.move_group_name": "move_group_name",
        "moveit_servo.planning_frame": "planning_frame",
        "moveit_servo.ee_frame_name": "ee_frame_name",
        "moveit_servo.robot_link_command_frame": "robot_link_command_frame",
        "moveit_servo.command_out_topic": "command_out_topic",
    }
    for param_key, arg_name in override_map.items():
        value = LaunchConfiguration(arg_name).perform(context)
        if value:
            servo_params[param_key] = value

    moveit_configs = (
        MoveItConfigsBuilder("denso_robot", package_name=moveit_config_package)
        .robot_description_kinematics(file_path=kinematics_yaml_file)
        .to_moveit_configs()
    )

    servo_node = Node(
        package="moveit_servo",
        executable="servo_node_main",
        name=servo_node_name,
        parameters=[
            servo_params,
            {"robot_description": robot_description},
            {"robot_description_semantic": robot_description_semantic},
            moveit_configs.robot_description_kinematics,
            {"use_sim_time": sim}
        ],
        output="screen",
    )

    return [servo_node]


def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            "robot_description", default_value="",
            description="URDF robot description as a string."),
        DeclareLaunchArgument(
            "robot_description_semantic", default_value="",
            description="SRDF robot semantic description as a string."),
        DeclareLaunchArgument(
            "moveit_config_package", default_value="denso_robot_moveit_config",
            description="Package containing MoveIt configuration files."),
        DeclareLaunchArgument(
            "kinematics_yaml_file", default_value="",
            description="Path to the kinematics.yaml configuration file, relative to the moveit_config_package share directory."),
        DeclareLaunchArgument(
            "sim", default_value="true",
            description="Use simulation time."),
        DeclareLaunchArgument(
            "servo_node_name", default_value="servo_node_main",
            description="Name for this servo node instance."),
        # Optional overrides for multi-arm setups
        DeclareLaunchArgument(
            "move_group_name", default_value="",
            description="Override: MoveIt move group name."),
        DeclareLaunchArgument(
            "planning_frame", default_value="",
            description="Override: planning reference frame."),
        DeclareLaunchArgument(
            "ee_frame_name", default_value="",
            description="Override: end-effector frame name."),
        DeclareLaunchArgument(
            "robot_link_command_frame", default_value="",
            description="Override: robot link command frame."),
        DeclareLaunchArgument(
            "command_out_topic", default_value="",
            description="Override: command output topic for the trajectory controller."),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
