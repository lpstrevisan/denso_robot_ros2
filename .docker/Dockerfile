FROM ros:humble

ENV COLCON_WS=/root/denso_ws

RUN apt-get update && apt-get install -y git terminator

RUN apt-get update && apt-get install -y --no-install-recommends \
      ros-$ROS_DISTRO-moveit \ 
      ros-$ROS_DISTRO-moveit-servo \      
      ros-$ROS_DISTRO-ros2-control \
      ros-$ROS_DISTRO-ros2-controllers \
      build-essential \
      git \
      nano \
      terminator && \
    rm -rf /var/lib/apt/list/*

RUN mkdir -p $COLCON_WS/src
WORKDIR $COLCON_WS

COPY . src/denso_robot_ros2/

RUN rosdep install --ignore-src --from-paths src -y -r

RUN rm -rf src/denso_robot_ros2/

CMD ["bash"]