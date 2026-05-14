# DENSO Robot ROS 2 - Docker

Docker environment for DENSO robots with ROS 2 Jazzy, with support for RViz2 and Gazebo Harmonic.

## Starting the Container

Choose the command according to your hardware:

**CPU only:**
```bash
ROS_DOMAIN_ID=<your_id> docker compose run --name denso_ros_jazzy_cpu --build cpu
```

**With NVIDIA GPU:**
```bash
ROS_DOMAIN_ID=<your_id> docker compose run --name denso_ros_jazzy_gpu --build gpu
```

> ⚠️ **ROS_DOMAIN_ID** isolates ROS 2 communication over the network using DDS. **To avoid interference between different computers running ROS 2 on the same network, a different domain ID should be set for each computer**. On Linux, safe values are **0–101** and **215–232**. For more details, see the [ROS 2 Jazzy documentation](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Domain-ID.html).


## Subsequent Executions

**CPU:**
```bash
docker start -ai denso_ros_jazzy_cpu
```

**NVIDIA GPU:**
```bash
docker start -ai denso_ros_jazzy_gpu
```

To exit the container, run:
```bash
exit
```

### Available Tools

* **Terminator**: terminal with tab and split-screen support.
```bash
terminator -u
```

## Running ROS 2 with DENSO
Inside the container, run:
```bash
source install/setup.bash
```

and

```bash
ros2 launch denso_robot_bringup denso_robot_bringup.launch.py model:=<robot_model> sim:=<boolean> gz_cam:=<boolean> ip_address:=<robot_ip_address>
```

- `model` (**required**) — robot model (`"cobotta"`, `"vs060"`, `"vs050"`).
- `ip_address` (if `sim:=false`) — robot IP address.
- `sim` (default: _true_) — whether the robot is simulated (Gazebo) or connected via RC8 controller.
- `gz_cam` (default: _false_) — whether the simulated robot has a camera attached to its flange

For more information, see [SlaveMode robot control](../denso_robot_control/README.md).