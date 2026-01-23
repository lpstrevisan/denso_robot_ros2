# MoveIt Servo

**MoveIt Servo** allows for real-time control of the robotic arm by sending continuous velocity commands. Unlike point-to-point trajectory planning, Servo is ideal for teleoperation, visual servoing, and motions where reactivity is required.

Commands can be sent in Joint Space or Cartesian Space (Twist).

Some useful links:

[MoveIt Servo Docs](https://moveit.picknik.ai/main/doc/examples/realtime_servo/realtime_servo_tutorial.html)

[MoveIt Servo Humble GitHub](https://github.com/moveit/moveit2/tree/humble/moveit_ros/moveit_servo)

## Usage

### 1. Service Commands (Start / Pause / Stop)

The servo node must be activated or managed via ROS2 service calls. Use the following commands to handle the servo state.

* **Start Servo:** Activates the servo control.
```bash
ros2 service call /servo_node/start_servo std_srvs/srv/Trigger {}

```


* **Pause Servo:** Pauses motion while keeping the servo active.
```bash
ros2 service call /servo_node/pause_servo std_srvs/srv/Trigger {}

```


* **Unpause Servo:** Resumes motion after a pause.
```bash
ros2 service call /servo_node/unpause_servo std_srvs/srv/Trigger {}

```


* **Stop Servo:** Completely stops the servo control.
```bash
ros2 service call /servo_node/stop_servo std_srvs/srv/Trigger {}

```



### 2. Motion Commands

To move the robot, publish messages to the appropriate topics.

**NOTE**: Ensure the `frame_id` matches your robot's reference frame (commonly `base_link` or `world`).

#### 2.1 Joint Jog (Joint Space Control)

Sends angular velocities to specific joints.

* **Unit**: Radians per second (rad/s)
```bash
ros2 topic pub /servo_node/delta_joint_cmds control_msgs/msg/JointJog "{
  header: {frame_id: 'base_link', stamp: 'now'},
  joint_names: ['joint_1', 'joint_2', ...],
  velocities: [<velocity_joint_1>, <velocity_joint_1>, ...]
}"

```



#### 2.2 Twist Stamped (Cartesian Control)

Sends linear and angular velocities to the End Effector. 

* **Linear Unit**: Meters per second (m/s)
* **Angular Unit**: Radians per second (rad/s)
```bash
ros2 topic pub /servo_node/delta_twist_cmds geometry_msgs/msg/TwistStamped "{
  header: {frame_id: 'base_link', stamp: 'now'},
  twist: {
    linear: {x: <velocity_x>, y: <velocity_y>, z: <velocity_z>},
    angular: {x: <velocity_roll>, y: <velocity_pitch>, z: <velocity_yaw>}
  }
}"

```
