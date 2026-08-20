#include <micro_ros_arduino.h>
#include <stdio.h>
#include <rcl/rcl.h>
#include <rcl/error_handling.h>
#include <rclc/rclc.h>
#include <rclc/executor.h>

#include <std_msgs/msg/int32.h>
#include <std_msgs/msg/float32_multi_array.h>
#include "arduino_secrets.h" 

// --- Motor Pins (Zumo Shield v1.2) ---
#define RIGHT_DIR_PIN 7
#define LEFT_DIR_PIN  8
#define RIGHT_PWM_PIN 9
#define LEFT_PWM_PIN  10
#define LED_PIN 13
#define BATTERY_PIN A1

// --- Telemetry Objects ---
rcl_publisher_t telemetry_pub;
std_msgs__msg__Float32MultiArray telemetry_msg;
float telemetry_data[3]; // Optimizing: sending only Batt, L_Speed, R_Speed (12 bytes vs 72 bytes)

// --- Motor Settings ---
#define MAX_SPEED 255
#define DEADBAND 20
#define FLIP_RIGHT_MOTOR false

// --- Macros ---
#define RCCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){error_loop();}}
#define RCSOFTCHECK(fn) { rcl_ret_t temp_rc = fn; if((temp_rc != RCL_RET_OK)){}}

// --- Function Prototypes ---
void error_loop();
void setLeftSpeed(int speed);
void setRightSpeed(int speed);

// --- ROS Objects ---
rcl_subscription_t subscriber;
std_msgs__msg__Int32 msg;
rclc_executor_t executor;
rclc_support_t support;
rcl_allocator_t allocator; // Global allocator to prevent stack corruption
rcl_node_t node;

// --- Globals ---
unsigned long lastMessageTime = 0;
int current_left_speed = 0;
int current_right_speed = 0;

void error_loop(){
  while(1){
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(100);
  }
}

void subscription_callback(const void * msgin)
{
  const std_msgs__msg__Int32 * msg = (const std_msgs__msg__Int32 *)msgin;
  
  lastMessageTime = millis();

  // Unpack Int32: High 16 bits = Steering, Low 16 bits = Throttle
  // Using int16_t casts to handle negative numbers correctly
  int16_t throttle = (int16_t)(msg->data & 0xFFFF);
  int16_t steering = (int16_t)(msg->data >> 16);

  // Deadband (already handled in controller, but good to keep)
  if (abs(throttle) < DEADBAND) throttle = 0;
  if (abs(steering) < DEADBAND) steering = 0;

  // Mixing
  int leftSpeed = throttle - steering;
  int rightSpeed = throttle + steering;

  // Constrain
  leftSpeed = constrain(leftSpeed, -MAX_SPEED, MAX_SPEED);
  rightSpeed = constrain(rightSpeed, -MAX_SPEED, MAX_SPEED);

  setLeftSpeed(leftSpeed);
  setRightSpeed(rightSpeed);
}

void setup() {
  Serial.begin(115200);
  Serial.println("Zumo Micro-ROS Node Starting...");

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  

  // Initialize Motor Pins
  pinMode(RIGHT_DIR_PIN, OUTPUT);
  pinMode(LEFT_DIR_PIN, OUTPUT);
  pinMode(RIGHT_PWM_PIN, OUTPUT);
  pinMode(LEFT_PWM_PIN, OUTPUT);

  // Quick 600ms motor spin test on boot to verify motor driver
  setLeftSpeed(150);
  setRightSpeed(150);
  delay(600);
  setLeftSpeed(0);
  setRightSpeed(0);

  char agent_ip[] = "192.168.8.223";
  size_t agent_port = 8888;
  
  // Standard Transport
  set_microros_wifi_transports(SECRET_SSID, SECRET_PASS, agent_ip, agent_port);

  allocator = rcl_get_default_allocator();

  //create init_options
  RCCHECK(rclc_support_init(&support, 0, NULL, &allocator));

  // create node
  RCCHECK(rclc_node_init_default(&node, "zn", "", &support)); // "zumo_node" -> "zn"

  // create subscriber
  RCCHECK(rclc_subscription_init_best_effort(
    &subscriber,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Int32),
    "cmd_vel"));

  // create telemetry publisher
  RCCHECK(rclc_publisher_init_best_effort(
    &telemetry_pub,
    &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, Float32MultiArray),
    "zt")); // "zumo_telemetry" -> "zt"
    
  // create executor (1 handle: 1 sub) - Timer removed to save RAM
  RCCHECK(rclc_executor_init(&executor, &support.context, 1, &allocator));
  RCCHECK(rclc_executor_add_subscription(&executor, &subscriber, &msg, &subscription_callback, ON_NEW_DATA));
}

void loop() {
  // 10ms timeout for better responsiveness
  RCSOFTCHECK(rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10)));

  // --- Telemetry Section (Run every 100ms) ---
  static unsigned long lastTelemetryTime = 0;
  if (millis() - lastTelemetryTime > 100) {
    lastTelemetryTime = millis();
    
    // 1. Read Battery (Zumo uses 3/2 divider on A1)
    float battery_mv = (float)analogRead(BATTERY_PIN) * (5000.0f / 1023.0f) * 1.5f;
    
    // 2. Populate Data (Reduced set)
    telemetry_data[0] = battery_mv;
    telemetry_data[1] = (float)current_left_speed;
    telemetry_data[2] = (float)current_right_speed;

    // 3. Publish
    telemetry_msg.data.data = telemetry_data;
    telemetry_msg.data.size = 3;
    telemetry_msg.data.capacity = 3;
    
    RCSOFTCHECK(rcl_publish(&telemetry_pub, &telemetry_msg, NULL));
  }

  // Safety Timeout: Stop motors if no message for 2 seconds
  if (millis() - lastMessageTime > 2000) {
    setLeftSpeed(0);
    setRightSpeed(0);
  }
  
  // Heartbeat debug every 1 second
  static unsigned long lastHeartbeat = 0;
  if (millis() - lastHeartbeat > 1000) {
    lastHeartbeat = millis();
    Serial.println("Alive...");
  }
}

void setLeftSpeed(int speed) {
  current_left_speed = speed; // Update global for telemetry
  bool reverse = false;
  if (speed < 0) {
    speed = -speed;
    reverse = true;
  }
  if (speed > MAX_SPEED) speed = MAX_SPEED;
  digitalWrite(LEFT_DIR_PIN, reverse ? HIGH : LOW);
  analogWrite(LEFT_PWM_PIN, speed);
}

void setRightSpeed(int speed) {
  current_right_speed = speed; // Update global for telemetry
  bool reverse = false;
  if (speed < 0) {
    speed = -speed;
    reverse = true;
  }
  if (speed > MAX_SPEED) speed = MAX_SPEED;
  
  // Apply Flip Logic
  if (FLIP_RIGHT_MOTOR) reverse = !reverse;
  
  digitalWrite(RIGHT_DIR_PIN, reverse ? HIGH : LOW);
  analogWrite(RIGHT_PWM_PIN, speed);
}
