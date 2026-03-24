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
    moveit_controllers_file = LaunchConfiguration("moveit_controllers_file").perform(context)
    robot_limits_file = LaunchConfiguration("robot_limits_file").perform(context)
    sim = LaunchConfiguration("sim").perform(context).lower() == "true"

    kinematics_yaml = load_yaml(moveit_config_package, kinematics_yaml_file)
    robot_description_kinematics = {"robot_description_kinematics": kinematics_yaml}

    ompl_planning_pipeline_config = {
        "move_group": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": (
                "default_planner_request_adapters/AddTimeOptimalParameterization"
                " default_planner_request_adapters/FixWorkspaceBounds"
                " default_planner_request_adapters/FixStartStateBounds"
                " default_planner_request_adapters/FixStartStateCollision"
                " default_planner_request_adapters/FixStartStatePathConstraints"
            ),
            "start_state_max_bounds_error": 0.1,
        }
    }
    ompl_planning_yaml = load_yaml(moveit_config_package, "config/ompl_planning.yaml")
    ompl_planning_pipeline_config["move_group"].update(ompl_planning_yaml)

    trajectory_execution = {
        "moveit_manage_controllers": False,
        "trajectory_execution.allowed_execution_duration_scaling": 1.2,
        "trajectory_execution.allowed_goal_duration_margin": 0.5,
        "trajectory_execution.allowed_start_tolerance": 0.01,
    }

    moveit_controllers = {
        "moveit_controller_manager": (
            "moveit_simple_controller_manager/MoveItSimpleControllerManager"
        ),
    }

    planning_scene_monitor_parameters = {
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "planning_scene_monitor_options": {
            "name": "planning_scene_monitor",
            "robot_description": "robot_description",
            "joint_state_topic": "/joint_states",
            "attached_collision_object_topic": "/move_group/planning_scene_monitor",
            "publish_planning_scene_topic": "/move_group/publish_planning_scene",
            "monitored_planning_scene_topic": "/move_group/monitored_planning_scene",
            "wait_for_initial_state_timeout": 10.0,
        },
    }

    occupancy_map_monitor_parameters = {
        "sensors": ["3D_sensor"],
        "3D_sensor": {
            "sensor_plugin": "",  # '~'
        },
    }

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            {"robot_description": robot_description},
            {"robot_description_semantic": robot_description_semantic},
            robot_description_kinematics,
            robot_limits_file,
            ompl_planning_pipeline_config,
            trajectory_execution,
            moveit_controllers,
            moveit_controllers_file,
            occupancy_map_monitor_parameters,
            planning_scene_monitor_parameters,
            {"use_sim_time": sim}
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
