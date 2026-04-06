FROM ros:humble

ENV COLCON_WS=/root/denso_ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-$ROS_DISTRO-moveit \
    ros-$ROS_DISTRO-moveit-servo \  
    ros-$ROS_DISTRO-ros2-control \
    ros-$ROS_DISTRO-ros2-controllers \
    terminator \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p $COLCON_WS
WORKDIR $COLCON_WS

COPY . src/

RUN apt-get update \
  && rosdep install --ignore-src --from-paths src -y -r \
  && rm -rf /var/lib/apt/lists/*

RUN rm -rf src/*

CMD ["bash"]