import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
import sys
import select
import termios
import tty

msg = """
Control Your Zumo!
---------------------------
Moving around:
   w
a  s  d
   x

w/x : increase/decrease linear velocity
a/d : increase/decrease angular velocity
space key, s : force stop

CTRL-C to quit
"""

from rclpy.qos import QoSProfile, ReliabilityPolicy

class ZumoController(Node):
    def __init__(self):
        super().__init__('zumo_controller')
        qos_profile = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.publisher_ = self.create_publisher(Int32, 'cmd_vel', qos_profile)
        self.speed = 0.5
        self.turn = 1.0
        self.x = 0.0
        self.th = 0.0
        self.status = 0

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def run(self):
        try:
            print(msg)
            while True:
                # ... (key handling same as before)
                key = self.get_key()
                if key == 'w':
                    self.x = self.speed
                    self.th = 0.0
                elif key == 'x':
                    self.x = -self.speed
                    self.th = 0.0
                elif key == 'a':
                    self.x = 0.0
                    self.th = self.turn
                elif key == 'd':
                    self.x = 0.0
                    self.th = -self.turn
                elif key == ' ' or key == 's':
                    self.x = 0.0
                    self.th = 0.0
                elif key == '\x03':
                    break

                # Packing Logic
                # Scale to +/- 255
                throttle = int(self.x * 255)
                steering = int(self.th * 255)
                
                # Pack into Int32: (Steering << 16) | (Throttle & 0xFFFF)
                # Handle negative numbers for bitwise operations
                throttle_packed = throttle & 0xFFFF
                steering_packed = (steering << 16) & 0xFFFF0000
                packed_data = steering_packed | throttle_packed
                
                # Python handles large integers, but we need to ensure it fits in signed 32-bit for ROS
                if packed_data > 2147483647: packed_data -= 4294967296

                msg_out = Int32()
                msg_out.data = int(packed_data)
                self.publisher_.publish(msg_out)
                # print(f"Published: {msg_out.data}") # Uncomment for verbose debug

        except Exception as e:
            print(e)

        finally:
            msg_out = Int32()
            msg_out.data = 0
            self.publisher_.publish(msg_out)


def main(args=None):
    global settings
    settings = termios.tcgetattr(sys.stdin)
    
    rclpy.init(args=args)
    controller = ZumoController()
    controller.run()
    controller.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
