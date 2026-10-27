import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [f'q{i}' for i in range(1, 19)]


class JointPublisher(Node):

    def __init__(self):
        super().__init__('joint_publisher')
        self.declare_parameter('rate', 30.0)
        self.declare_parameter('amplitude', 0.5)
        self.declare_parameter('frequency', 0.5)

        self.publisher = self.create_publisher(JointState, 'joint_states', 10)
        rate = self.get_parameter('rate').value
        self.timer = self.create_timer(1.0 / rate, self.publish_joints)
        self.start = self.get_clock().now()

    def publish_joints(self):
        t = (self.get_clock().now() - self.start).nanoseconds * 1e-9
        amplitude = self.get_parameter('amplitude').value
        frequency = self.get_parameter('frequency').value

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        # Movimiento estatico
        msg.position = [0.0] * len(JOINT_NAMES)
        msg.position[JOINT_NAMES.index('q3')] = amplitude * math.sin(2 * math.pi * frequency * t)
        self.publisher.publish(msg)





def main(args=None):
    rclpy.init(args=args)
    node = JointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
