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
from launch.actions import DeclareLaunchArgument, OpaqueFunction+
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_utils import load_yaml 

def launch_setup(context, *args, **kwargs):
    robot_description = LaunchConfiguration("robot_description")
    robot_description_semantic = LaunchConfiguration("robot_description_semantic")
    moveit_config_package = LaunchConfiguration("moveit_config_package")
    kinematics_yaml_file = LaunchConfiguration("kinematics_yaml_file")

    kinematics_yaml = load_yaml(moveit_config_package.perform(context), kinematics_yaml_file)

    ompl_planning_yaml = load_yaml(moveit_config_package.perform(context), "config/ompl_planning.yaml")

    ompl_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": "default_planner_request_adapters/AddTimeOptimalParameterization" \
                + " default_planner_request_adapters/FixWorkspaceBounds" \
                + " default_planner_request_adapters/FixStartStateBounds" \
                + " default_planner_request_adapters/FixStartStateCollision" \
                + " default_planner_request_adapters/FixStartStatePathConstraints",
            "start_state_max_bounds_error": 0.1,
        }
    }
    ompl_planning_pipeline_config["move_group"].update(ompl_planning_yaml)

    rviz_config_file = PathJoinSubstitution([
        FindPackageShare(moveit_config_package),
        'rviz',
        'view_robot.rviz'
    ])

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_moveit",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[
            {"robot_description": robot_description.perform(context)},
            {"robot_description_semantic": robot_description_semantic.perfom(context)},
            ompl_planning_pipeline_config,
            {"robot_description_kinematics": kinematics_yaml}
        ]
    )

    return [rviz]


def generate_launch_description():

    declared_arguments = []

    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description",
            default_value="",
            description="URDF robot description as a string."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "robot_description_semantic",
            default_value="",
            description="SRDF robot semantic description as a string."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "moveit_config_package",
            default_value="denso_robot_moveit_config",
            description="Package containing MoveIt configuration files."
        )
    )
    declared_arguments.append(
        DeclareLaunchArgument(
            "kinematics_yaml_file",
            default_value="",
            description="Path to the kinematics.yaml configuration file, relative to the moveit_config_package share directory."
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
