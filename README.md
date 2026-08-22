# AnZym Zumo — Pololu Zumo micro-ROS GCS Robot

This repository contains the micro-ROS Arduino firmware and ROS 2 package for the **AnZym Zumo** robot, built on the **Pololu Zumo Shield v1.2** with an **Arduino UNO R4 WiFi** (Renesas RA4M1 + ESP32-S3).

---

## 🚀 Key Features
- **Wi-Fi micro-ROS UDP Transport**: Communicates over 2.4 GHz Wi-Fi to the micro-ROS agent at 10 Hz telemetry and 20 Hz motor control.
- **Packed 32-bit Motor Protocol**: Receives packed `std_msgs/msg/Int32` commands (`(Steering << 16) | (Throttle & 0xFFFF)`) for minimum network latency and zero memory fragmentation.
- **Live Battery & Motor Telemetry**: Publishes battery voltage (millivolts) and current motor PWM velocities on `/zt` (`std_msgs/msg/Float32MultiArray`).
- **GCS Teleop Integration**: Fully integrated with the AnZym Ground Control Station (GCS) dashboard with Bluetooth gamepad teleoperation.
- **Safety Watchdog**: Onboard 2.0s failsafe watchdog automatically stops motors if Wi-Fi packets stop.
- **Desktop Python Utilities**: Includes Tkinter live telemetry dashboard (`telemetry_gui`), keyboard teleop (`controller_node`), and joy translator (`joy_translator_node`).

---

## 🛠️ Hardware Configuration
- **Chassis / Shield**: Pololu Zumo Shield v1.2 for Arduino
- **Microcontroller**: Arduino UNO R4 WiFi (Renesas RA4M1 48MHz ARM Cortex-M4 + ESP32-S3)
- **Motor Driver**: Texas Instruments DRV8835 Dual Motor Driver
- **Pinout Mapping**:
  - **Left Motor Direction**: Pin 8 (`PHASE`)
  - **Left Motor Speed (PWM)**: Pin 10 (`ENABLE`)
  - **Right Motor Direction**: Pin 7 (`PHASE`)
  - **Right Motor Speed (PWM)**: Pin 9 (`ENABLE`)
  - **Battery Monitor**: Pin A1 (3:2 voltage divider, analog input)
  - **Status / Heartbeat LED**: Pin 13
  - **Buzzer**: Pin 3

---

## 📡 ROS 2 Interfaces & Topics

| Topic | Message Type | QoS | Direction | Description |
|---|---|---|---|---|
| `/cmd_vel` | `std_msgs/msg/Int32` | Best Effort, Depth 10 | GCS / Node ➔ Zumo | Packed 32-bit command: `(Steering << 16) \| (Throttle & 0xFFFF)` |
| `/zt` | `std_msgs/msg/Float32MultiArray` | Best Effort, Depth 10 | Zumo ➔ GCS / GUI | Array `[battery_mV, left_speed_pwm, right_speed_pwm]` |
| `/joy` | `sensor_msgs/msg/Joy` | Reliable | Gamepad ➔ joy_translator | Raw joystick input from workstation or GCS bridge |

---

## 📁 Repository Structure

```text
anzym_zumo/
├── src/
│   ├── ZumoMicroROS_Basic/
│   │   ├── ZumoMicroROS_Basic.ino       # Core Arduino UNO R4 WiFi micro-ROS firmware
│   │   ├── arduino_secrets.h.example    # Wi-Fi SSID, password, and agent IP template
│   │   └── arduino_secrets.h            # Local secrets configuration (git-ignored)
│   └── motor_py_pkg/                    # ROS 2 Python package for workstation control
│       ├── motor_py_pkg/
│       │   ├── joy_translator_node.py   # Translates /joy axes to packed /cmd_vel with slew rate
│       │   ├── controller_node.py       # Terminal WASD keyboard teleoperation
│       │   ├── telemetry_node.py        # Terminal live telemetry logger
│       │   └── telemetry_gui.py         # Tkinter visual telemetry dashboard
│       ├── launch/
│       │   └── zumo_joystick.launch.py  # Launches joy_node and joy_translator_node
│       └── package.xml
├── start_all.sh                         # Unified startup script for agent and workstation nodes
└── README.md
```

---

## ⚡ Setup & Flashing

### 1. Wi-Fi Configuration
Copy `src/ZumoMicroROS_Basic/arduino_secrets.h.example` to `src/ZumoMicroROS_Basic/arduino_secrets.h` and edit your Wi-Fi SSID, Password, and workstation micro-ROS Agent IP:
```bash
cp src/ZumoMicroROS_Basic/arduino_secrets.h.example src/ZumoMicroROS_Basic/arduino_secrets.h
```

### 2. Compile & Upload via Arduino CLI
```bash
# Compile for Arduino UNO R4 WiFi
arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi src/ZumoMicroROS_Basic/ZumoMicroROS_Basic.ino

# Upload over USB
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:renesas_uno:unor4wifi src/ZumoMicroROS_Basic/ZumoMicroROS_Basic.ino
```

---

## 🏃 Running the Robot System

### 1. Start the micro-ROS Agent (Docker)
```bash
docker run -d --name anzym-zumo-microros --restart always --net=host microros/micro-ros-agent:humble udp4 --port 8888
```

Or run natively via ROS 2:
```bash
ros2 run micro_ros_agent micro_ros_agent udp4 --port 8888
```

### 2. Launch Workstation Joystick Teleop
```bash
# Build the local package
colcon build --packages-select motor_py_pkg
source install/setup.bash

# Launch joystick teleop
ros2 launch motor_py_pkg zumo_joystick.launch.py
```

### 3. Launch Telemetry Dashboard (GUI)
```bash
ros2 run motor_py_pkg telemetry_gui
```

### 4. GCS Fleet Integration
In the **AnZym GCS Dashboard** (`http://localhost:5173`):
1. Click **+ Add Robot**.
2. Select the **`anzym_zumo`** platform template.
3. Configure the rosbridge / agent host IP.
4. Drive using the web gamepad with zero-latency packed integer commands.
