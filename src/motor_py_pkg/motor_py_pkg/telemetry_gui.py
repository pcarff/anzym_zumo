import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Float32MultiArray
import tkinter as tk
from tkinter import ttk
import threading

class TelemetryGUI(Node):
    def __init__(self, root):
        super().__init__('telemetry_gui')
        self.root = root
        self.root.title("Zumo Telemetry Dashboard")
        self.root.geometry("600x500")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # --- Variables ---
        self.var_battery = tk.StringVar(value="0 mV")
        self.var_motors = tk.StringVar(value="L: 0 | R: 0")
        self.var_imu = tk.StringVar(value="Accel: -, -, -\nMag: -, -, -\nGyro: -, -, -")
        
        # --- Layout ---
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="Zumo Robot Status", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Battery Section
        batt_frame = ttk.LabelFrame(main_frame, text="Power", padding="10")
        batt_frame.pack(fill=tk.X, pady=5)
        self.batt_bar = ttk.Progressbar(batt_frame, orient=tk.HORIZONTAL, length=400, mode='determinate', maximum=6000)
        self.batt_bar.pack(pady=5)
        ttk.Label(batt_frame, textvariable=self.var_battery, font=("Consolas", 12)).pack()
        
        # Motors Section
        motor_frame = ttk.LabelFrame(main_frame, text="Motors", padding="10")
        motor_frame.pack(fill=tk.X, pady=5)
        
        m_inner = ttk.Frame(motor_frame)
        m_inner.pack(fill=tk.X)
        
        # Left Motor
        self.l_motor = ttk.Progressbar(m_inner, orient=tk.VERTICAL, length=100, mode='determinate', maximum=255)
        self.l_motor.pack(side=tk.LEFT, padx=30)
        
        # Right Motor
        self.r_motor = ttk.Progressbar(m_inner, orient=tk.VERTICAL, length=100, mode='determinate', maximum=255)
        self.r_motor.pack(side=tk.RIGHT, padx=30)
        
        ttk.Label(motor_frame, textvariable=self.var_motors, font=("Consolas", 12)).pack(pady=5)

        # Line Sensors Section
        line_frame = ttk.LabelFrame(main_frame, text="Line Sensors", padding="10")
        line_frame.pack(fill=tk.X, pady=5)
        
        self.line_bars = []
        l_inner = ttk.Frame(line_frame)
        l_inner.pack()
        
        for i in range(6):
            bar = ttk.Progressbar(l_inner, orient=tk.VERTICAL, length=60, mode='determinate', maximum=1000)
            bar.pack(side=tk.LEFT, padx=5)
            self.line_bars.append(bar)

        # IMU Section
        imu_frame = ttk.LabelFrame(main_frame, text="IMU Data", padding="10")
        imu_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(imu_frame, textvariable=self.var_imu, font=("Consolas", 10), justify=tk.LEFT).pack()

        # ROS Connection
        # Arduino uses Best Effort, so we must too!
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.subscription = self.create_subscription(
            Float32MultiArray,
            'zt',
            self.listener_callback,
            qos_profile) # Updated QoS

    def listener_callback(self, msg):
        data = msg.data
        if len(data) < 3:
            return
            
        try:
            # Battery
            batt_mv = data[0]
            self.var_battery.set(f"{batt_mv:.0f} mV")
            self.batt_bar['value'] = batt_mv
            
            # Motors
            self.l_motor['value'] = abs(data[1])
            self.r_motor['value'] = abs(data[2])
            self.var_motors.set(f"L: {data[1]:.0f} | R: {data[2]:.0f}")
            
            # IMU & Line (Not sent effectively to save RAM)
            # Keeping UI placeholders static or last known state
            
        except Exception as e:
            print(f"GUI Update Error: {e}")
            


def ros_spin_thread(node):
    rclpy.spin(node)

def main(args=None):
    rclpy.init(args=args)
    
    root = tk.Tk()
    gui = TelemetryGUI(root)
    
    # Run ROS in separate thread
    t = threading.Thread(target=ros_spin_thread, args=(gui,), daemon=True)
    t.start()
    
    # Run Tkinter mainloop
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        gui.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
