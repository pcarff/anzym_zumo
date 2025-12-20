#!/bin/bash

# Zumo Robot Startup Script

# 1. Source micro-ROS workspace
if [ -f ~/microros_ws/install/setup.bash ]; then
    source ~/microros_ws/install/setup.bash
else
    echo "Error: micro-ROS workspace not found!"
    exit 1
fi

# 2. Source Zumo workspace
if [ -f ~/zumo_ws/install/setup.bash ]; then
    source ~/zumo_ws/install/setup.bash
else
    echo "Error: Zumo workspace not found! Did you run 'colcon build' in ~/zumo_ws?"
    exit 1
fi

echo "---------------------------------------------------"
echo "Starting Zumo Control System"
echo "Agent IP: 192.168.8.225 (Ensure this matches your secrets)"
echo "---------------------------------------------------"

# 3. Launch everything
# We use a subshell or background process for the agent?
# Better: Create a combined launch configuration here or run agent in background.

# Option A: Run agent in background, then launch nodes.
# Trap exit to kill agent when script stops.
trap 'kill $(jobs -p)' EXIT

echo "Starting micro-ROS Agent..."
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888 &
AGENT_PID=$!

# Wait a moment for agent to start
sleep 2

echo "Starting Joystick Control..."
ros2 launch motor_py_pkg zumo_joystick.launch.py

# When launch file exits, the trap will kill the agent.
wait $AGENT_PID
