import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray
import sys

class TelemetryDisplay(Node):
    def __init__(self):
        super().__init__('telemetry_display')
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'zumo_telemetry',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        print("Waiting for Zumo Telemetry...")

    def listener_callback(self, msg):
        data = msg.data
        if len(data) < 18:
            return

        # Clear screen code (ANSI)
        # print("\033[H\033[J", end="") 
        
        print("-" * 40)
        print(f"BATTERY: {data[0]:.0f} mV")
        print("-" * 40)
        print(f"MOTORS : L={data[16]:.0f}  R={data[17]:.0f}")
        print("-" * 40)
        print(f"ACCEL  : X={data[1]:.0f}  Y={data[2]:.0f}  Z={data[3]:.0f}")
        print(f"MAG    : X={data[4]:.0f}  Y={data[5]:.0f}  Z={data[6]:.0f}")
        print(f"GYRO   : X={data[7]:.0f}  Y={data[8]:.0f}  Z={data[9]:.0f}")
        print("-" * 40)
        print(f"LINES  : {data[10]:.0f} {data[11]:.0f} {data[12]:.0f} {data[13]:.0f} {data[14]:.0f} {data[15]:.0f}")
        print("-" * 40)
        print("")

def main(args=None):
    rclpy.init(args=args)
    node = TelemetryDisplay()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
