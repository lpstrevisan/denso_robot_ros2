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
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder

# Import shared utilities from parent launch directory
_launch_dir = os.path.join(get_package_share_directory("denso_robot_bringup"), "launch")
if _launch_dir not in sys.path:
    sys.path.insert(0, _launch_dir)


def launch_setup(context, *args, **kwargs):
    rviz = LaunchConfiguration("rviz").perform(context)
    robot_description = LaunchConfiguration("robot_description").perform(context)
    robot_description_semantic = LaunchConfiguration(
        "robot_description_semantic").perform(context)
    moveit_config_package = LaunchConfiguration("moveit_config_package").perform(context)
    kinematics_yaml_file = LaunchConfiguration("kinematics_yaml_file").perform(context)
    rviz_config_file = LaunchConfiguration("rviz_config_file").perform(context)

    moveit_configs = (
        MoveItConfigsBuilder("denso_robot", package_name=moveit_config_package)
        .robot_description_kinematics(file_path=kinematics_yaml_file)
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )

    rviz_node = Node(
        package="rviz2",
        condition=IfCondition(rviz),
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            {"robot_description": robot_description},
            {"robot_description_semantic": robot_description_semantic},
            moveit_configs.robot_description_kinematics,
            moveit_configs.planning_pipelines,
        ])

    return [rviz_node]


def generate_launch_description():

    declared_arguments = [
        DeclareLaunchArgument(
            "rviz", default_value="false",
            description="Launch RViz."),
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
            "rviz_config_file", default_value="",
            description="Full path to the RViz configuration file."),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
