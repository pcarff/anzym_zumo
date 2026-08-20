# AnZym Zumo — Pololu Zumo micro-ROS GCS Robot

This repository contains the micro-ROS Arduino firmware and ROS 2 package for the **AnZym Zumo** robot, built on the **Pololu Zumo Shield v1.2** with an **Arduino UNO R4 WiFi** (Renesas RA4M1 + ESP32-S3).

---

## Features
- **Wi-Fi micro-ROS UDP Transport**: Communicates over 2.4 GHz Wi-Fi to the micro-ROS agent at 10 Hz telemetry and 20 Hz motor control.
- **Packed 32-bit Motor Protocol**: Receives packed `std_msgs/msg/Int32` commands (`(Steering << 16) | (Throttle & 0xFFFF)`) for minimum network latency and zero memory fragmentation.
- **Live Battery & Motor Telemetry**: Publishes battery voltage (millivolts) and current motor PWM velocities on `/zt` (`std_msgs/msg/Float32MultiArray`).
- **GCS Teleop Integration**: Fully integrated with the AnZym Ground Control Station (GCS) dashboard with Bluetooth gamepad teleoperation.
- **Safety Watchdog**: Onboard 2.0s failsafe watchdog automatically stops motors if Wi-Fi packets stop.

---

## Hardware Configuration
- **Chassis / Shield**: Pololu Zumo Shield v1.2 for Arduino
- **Microcontroller**: Arduino UNO R4 WiFi
- **Motor Driver**: Texas Instruments DRV8835 Dual Motor Driver
- **Pinout**:
  - Left Motor Direction: Pin 8 (PHASE)
  - Left Motor Speed (PWM): Pin 10 (ENABLE)
  - Right Motor Direction: Pin 7 (PHASE)
  - Right Motor Speed (PWM): Pin 9 (ENABLE)
  - Battery Monitor: Pin A1 (3:2 divider)
  - Status LED: Pin 13

---

## Setup & Flashing

### 1. Wi-Fi Configuration
Copy `src/ZumoMicroROS_Basic/arduino_secrets.h.example` to `src/ZumoMicroROS_Basic/arduino_secrets.h` and edit your Wi-Fi SSID and Password:
```bash
cp src/ZumoMicroROS_Basic/arduino_secrets.h.example src/ZumoMicroROS_Basic/arduino_secrets.h
```

### 2. Compile & Upload via Arduino CLI
```bash
arduino-cli compile --fqbn arduino:renesas_uno:unor4wifi src/ZumoMicroROS_Basic/ZumoMicroROS_Basic.ino
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:renesas_uno:unor4wifi src/ZumoMicroROS_Basic/ZumoMicroROS_Basic.ino
```

---

## Running the micro-ROS Agent
```bash
docker run -d --name anzym-zumo-microros --restart always --net=host microros/micro-ros-agent:humble udp4 --port 8888
```
