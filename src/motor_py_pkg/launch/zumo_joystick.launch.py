from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # Joy Node (Reads the hardware)
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen'
        ),
        # Translator Node (Converts to Zumo commands)
        Node(
            package='motor_py_pkg',
            executable='joy_translator_node',
            name='joy_translator',
            output='screen'
        ),
        # Telemetry GUI
        Node(
            package='motor_py_pkg',
            executable='telemetry_gui',
            name='telemetry_display',
            output='screen',
            emulate_tty=True
        )
    ])
