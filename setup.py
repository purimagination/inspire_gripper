from setuptools import setup

package_name = 'inspire_gripper'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='hanzx',
    maintainer_email='thefoxfoxfox@outlook.com',
    description='ROS 2 Package for Inspire Gripper',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'service = inspire_gripper.inspire_gripper_server:main',
            'client = inspire_gripper.inspire_gripper_client:main',
        ],
    },
)
