#!/usr/bin/env python3

from std_srvs.srv import SetBool
import rclpy
from rclpy.node import Node
import sys


class InspireGripperClientAsync(Node):

    def __init__(self):
        super().__init__('inspire_gripper_client_async')
        self.cli = self.create_client(SetBool, 'gripper_setting')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('service not available, waiting again...')
        self.req = SetBool.Request()

    def send_request(self, gripper_settig):
        self.req.data = gripper_settig
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main():
    rclpy.init()

    minimal_client = InspireGripperClientAsync()
    if(int(sys.argv[1]) == 0):
        data = False
    elif(int(sys.argv[1]) == 1):
        data = True
    else:
        print('Wrong input Command')
    response = minimal_client.send_request(data)
    minimal_client.get_logger().info(
        'Response of Inspire Gripper: %d' %
        (response.success))

    minimal_client.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()