from setuptools import find_packages, setup

package_name = 'motor_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/zumo_joystick.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pcarff',
    maintainer_email='pcarff@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'controller_node = motor_py_pkg.controller_node:main',
            'joy_translator_node = motor_py_pkg.joy_translator_node:main',
            'telemetry_node = motor_py_pkg.telemetry_node:main',
            'telemetry_gui = motor_py_pkg.telemetry_gui:main',
        ],
    },
)
