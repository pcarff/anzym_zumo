import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
from std_msgs.msg import Int32
from rclpy.qos import QoSProfile, ReliabilityPolicy

class JoyTranslator(Node):
    def __init__(self):
        super().__init__('joy_translator')
        
        # Publisher to Zumo (Best Effort to match Arduino)
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher_ = self.create_publisher(Int32, 'cmd_vel', qos_profile)
        
        # Subscriber to Joystick
        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            10)
            
        # State storage (Target)
        self.target_throttle = 0
        self.target_steering = 0
        
        # Current State (for smoothing)
        self.current_throttle = 0.0
        self.current_steering = 0.0
        
        # Smoothing Factor (Max change per 50ms step)
        # 255 / 10 = 25 steps to full speed (approx 1.25 seconds) - Very smooth
        # Adjust this value: Higher = Faster response, Lower = Smoother
        self.slew_rate = 20.0 
        
        # Timer to republish commands at 20Hz (50ms)
        self.timer = self.create_timer(0.05, self.timer_callback)
            
        self.get_logger().info('Joy Translator Started. Left Stick Y: Throttle, Right Stick X: Steering')

    def timer_callback(self):
        # Slew Rate Limiter
        # Move current towards target by at most slew_rate
        
        # Throttle Smoothing
        diff_throttle = self.target_throttle - self.current_throttle
        if abs(diff_throttle) < self.slew_rate:
            self.current_throttle = float(self.target_throttle)
        else:
            self.current_throttle += self.slew_rate if diff_throttle > 0 else -self.slew_rate
            
        # Steering Smoothing
        diff_steering = self.target_steering - self.current_steering
        if abs(diff_steering) < self.slew_rate:
            self.current_steering = float(self.target_steering)
        else:
            self.current_steering += self.slew_rate if diff_steering > 0 else -self.slew_rate

        # Publish
        self.publish_command(int(self.current_throttle), int(self.current_steering))

    def joy_callback(self, msg):
        try:
            # Throttle (Left Stick Y)
            if len(msg.axes) > 1:
                raw_throttle = msg.axes[1] 
            else:
                raw_throttle = 0.0
                
            # Steering (Right Stick X)
            if len(msg.axes) > 2:
                raw_steering = msg.axes[2]
            else:
                raw_steering = 0.0

            # Update Targets
            self.target_throttle = int(raw_throttle * 255)
            self.target_steering = int(raw_steering * 255)
            
        except IndexError:
            pass

    def publish_command(self, throttle, steering):
        # Pack into Int32: (Steering << 16) | (Throttle & 0xFFFF)
        throttle_packed = throttle & 0xFFFF
        steering_packed = (steering << 16) & 0xFFFF0000
        packed_data = steering_packed | throttle_packed
        
        # Python handles large integers, but we need to ensure it fits in signed 32-bit for ROS
        if packed_data > 2147483647: packed_data -= 4294967296

        msg_out = Int32()
        msg_out.data = int(packed_data)
        self.publisher_.publish(msg_out)

def main(args=None):
    rclpy.init(args=args)
    node = JoyTranslator()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
