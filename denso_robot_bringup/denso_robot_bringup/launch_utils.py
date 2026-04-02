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

from launch_ros.actions import Node
from launch.conditions import IfCondition, UnlessCondition
from ament_index_python.packages import get_package_share_directory
from launch_param_builder import ParameterBuilder

def control_node(robot_description, robot_controllers_path, bcap_slave_control_cycle_msec, sim):

    denso_robot_control_parameters = {
        'denso_bcap_slave_control_cycle_msec': bcap_slave_control_cycle_msec,
        'denso_config_file': get_package_share_directory('denso_robot_core') 
            + '/config/config.xml'
    }

    control_node = Node(
        package='controller_manager',
        executable='ros2_control_node',
        condition=UnlessCondition(sim),
        parameters=[
            robot_description,
            robot_controllers_path,
            denso_robot_control_parameters
        ],
        output={
            'stdout': 'screen',
            'stderr': 'screen',
        }
    )

    return control_node

def controller_spawner(controller):

    controller_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=[
            controller,
            '-c',
            '/controller_manager'
            ]
        )

    return controller_spawner

def move_group(move_config, use_sim_time, moveit_controllers_file=None):
    # Trajectory Execution Configuration
    moveit_controllers = {
        'moveit_controller_manager': 'moveit_simple_controller_manager' \
            + '/MoveItSimpleControllerManager',
    }

    trajectory_execution = {
        'moveit_manage_controllers': False,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01,
    }

    planning_scene_monitor_parameters = {
        'planning_scene_monitor_options': {
            'name': 'planning_scene_monitor',
            'robot_description': 'robot_description',
            'joint_state_topic': '/joint_states',
            'attached_collision_object_topic': '/move_group/planning_scene_monitor',
            'publish_planning_scene_topic': '/move_group/publish_planning_scene',
            'monitored_planning_scene_topic': '/move_group/monitored_planning_scene',
            'wait_for_initial_state_timeout': 10.0,
        },
    }

    occupancy_map_monitor_parameters = {
        'sensors': ['3D_sensor'],
        '3D_sensor': {
            'sensor_plugin': '', #'~'
        },
    }

    parameters = [
        move_config.to_dict(),
        moveit_controllers,
        trajectory_execution,
        planning_scene_monitor_parameters,
        occupancy_map_monitor_parameters,
        {'use_sim_time': use_sim_time}
    ]

    if moveit_controllers_file is not None:
        parameters.append(moveit_controllers_file)

    move_group = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=parameters
    )

    return move_group

def rviz(moveit_config, launch_rviz):

    rviz_config_file = moveit_config.package_path / 'rviz/view_robot.rviz'

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2_moveit',
        condition=IfCondition(launch_rviz),
        output='log',
        arguments=['-d', rviz_config_file],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.planning_pipelines,
            moveit_config.robot_description_kinematics
        ]
    )

    return rviz

def static_tf(child_frame):

    static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher',
        output='log',
        arguments=[
            '--frame-id', 'world',
            '--child-frame-id', child_frame
        ]
    )

    return static_tf

def robot_state_publisher(robot_description, use_sim_time):
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='both',
        parameters=[
            robot_description,
            {'use_sim_time': use_sim_time}
        ]
    )

    return robot_state_publisher

def moveit_servo(moveit_config, sim):

    servo_params = (
        ParameterBuilder('denso_robot_moveit_config')
        .yaml(
            file_path='config/moveit_servo.yaml'
        )
        .parameters('use_gazebo', sim)
        .to_dict()
    )

    servo_node = Node(
        package='moveit_servo',
        executable='servo_node_main',
        parameters=[
            servo_params,
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            {'use_sim_time': sim}
        ],
        output='screen',
    )
