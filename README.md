# inspire_gripper
This is a ROS 2 package for the [inspire two-finger paraller gripper](https://www.inspire-robots.com/product/ddjs/).

## Dependencies
```sh
pip install pyserial
sudo apt remove brltty
```

## Permissions
```sh
# enable all connected USB devices
sudo chmod a+rw /dev/ttyUSB*
```

## Installation

```sh
# cd to your ROS 2 Workspace
cd colcon_ws/src
git clone https://github.com/purimagination/inspire_gripper.git
cd ..
colcon build
source install setup.bash
```

## How to Use

```sh
# Terminal 1, Launch the Service
cd colcon_ws
source install/setup.bash
ros2 run inspire_gripper service 

# Terminal 2, Call the Service
cd colcon_ws
source install/setup.bash
ros2 run inspire_gripper client 0 # Open the Gripper
ros2 run inspire_gripper client 1 # Close the Gripper
```
