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

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def launch_setup(context, *args, **kwargs):
    robot_description = LaunchConfiguration("robot_description")
    sim = LaunchConfiguration("sim")

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="both",
        parameters=[
            {"robot_description": robot_description.perform(context)},
            {"use_sim_time": sim}
        ]
    )

    return [robot_state_publisher]

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
            "sim",
            default_value="true", 
            description="Use simulation time."
        )
    )

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
