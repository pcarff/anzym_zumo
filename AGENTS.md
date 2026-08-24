# AGENTS.md — AnZym Zumo Micro-ROS Bot (`anzym_zumo`)

## Subsystem Architecture
- **Hardware**: Pololu Zumo Shield v1.2 with Arduino UNO R4 WiFi (Renesas RA4M1 48MHz Cortex-M4 + ESP32-S3 Wi-Fi coprocessor).
- **Transport**: micro-ROS UDP agent over Wi-Fi (`udp4 --port 8888`).
- **Motor Control**: TI DRV8835 Dual Motor Driver (Left: Phase 8, PWM 10; Right: Phase 7, PWM 9).
- **Protocol**:
  - Command: Packed 32-bit integer on `/cmd_vel` (`std_msgs/msg/Int32`): `(Steering << 16) | (Throttle & 0xFFFF)`.
  - Telemetry: `/zt` (`std_msgs/msg/Float32MultiArray`) -> `[battery_mV, left_speed_pwm, right_speed_pwm]`.
- **Failsafe**: 2.0s watchdog automatically engages motor brake if UDP packets stop.

## Compilation & Verification Commands
- **Compile Firmware**: `arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi src/ZumoMicroROS_Basic/ZumoMicroROS_Basic.ino`
- **Build Python Node**: `colcon build --packages-select motor_py_pkg`
- **Launch Agent**: `docker run -d --name anzym-zumo-microros --restart always --net=host microros/micro-ros-agent:humble udp4 --port 8888`

## Key Constraints
- Battery ADC scale factor is calibrated for 3:2 voltage divider on Pin A1.
- Never exceed PWM value of 255.
- Maintain non-blocking code inside `loop()` in Arduino sketch.
