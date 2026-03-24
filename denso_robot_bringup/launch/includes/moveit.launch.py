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
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    robot_description = LaunchConfiguration("robot_description").perform(context)
    robot_description_semantic = LaunchConfiguration(
        "robot_description_semantic").perform(context)
    moveit_config_package = LaunchConfiguration("moveit_config_package").perform(context)
    kinematics_yaml_file = LaunchConfiguration("kinematics_yaml_file").perform(context)
    moveit_controllers_file = LaunchConfiguration("moveit_controllers_file").perform(context)
    robot_limits_file = LaunchConfiguration("robot_limits_file").perform(context)
    sim = LaunchConfiguration("sim").perform(context).lower() == "true"

    moveit_configs = (
        MoveItConfigsBuilder("denso_robot", package_name=moveit_config_package)
        .robot_description_kinematics(file_path=kinematics_yaml_file)
        .trajectory_execution(moveit_manage_controllers=False)
        .joint_limits(file_path=robot_limits_file)
        .planning_pipelines(pipelines=["ompl"])
        .planning_scene_monitor()
        .to_moveit_configs()
    )

    # Inject pre-built robot descriptions evaluated by the orchestrator
    moveit_configs.robot_description = {"robot_description": robot_description}
    moveit_configs.robot_description_semantic = {
        "robot_description_semantic": robot_description_semantic
    }
    # joint_limits YAML uses the move_group.ros__parameters namespace wrapper;
    # clear it from the dict and pass as a file path below so the node loads it correctly.
    moveit_configs.joint_limits = {}

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_configs.to_dict(),
            {
                "moveit_controller_manager": (
                    "moveit_simple_controller_manager/MoveItSimpleControllerManager"
                ),
                "trajectory_execution.allowed_execution_duration_scaling": 1.2,
                "trajectory_execution.allowed_goal_duration_margin": 0.5,
                "trajectory_execution.allowed_start_tolerance": 0.01,
            },
            moveit_controllers_file,
            robot_limits_file,
            {"use_sim_time": sim},
        ])

    return [move_group_node]


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
            "moveit_controllers_file", default_value="",
            description="Full path to the moveit_controllers.yaml configuration file."),
        DeclareLaunchArgument(
            "robot_limits_file", default_value="",
            description="Full path to the joint_limits.yaml configuration file."),
        DeclareLaunchArgument(
            "sim", default_value="true",
            description="Use simulation time."),
    ]

    return LaunchDescription(declared_arguments + [OpaqueFunction(function=launch_setup)])
