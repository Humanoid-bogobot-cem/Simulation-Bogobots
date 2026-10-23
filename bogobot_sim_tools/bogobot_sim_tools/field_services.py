import time

from bogobot_interfaces.srv import SpawnBall
from gz.msgs10.boolean_pb2 import Boolean
from gz.msgs10.empty_pb2 import Empty
from gz.msgs10.entity_factory_pb2 import EntityFactory
from gz.msgs10.entity_pb2 import Entity
from gz.msgs10.scene_pb2 import Scene
from gz.msgs10.world_control_pb2 import WorldControl
from gz.transport13 import Node as GzNode
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

BALL_NAME = 'ball'

class FieldServices(Node):

    def __init__(self):
        super().__init__('field_services')
        self.world = self.declare_parameter('world', 'robocup_field').value
        self.ball_model = self.declare_parameter('ball_model', 'model://ball').value
        self.ball_radius = self.declare_parameter('ball_radius', 0.0732).value #Radio del balón: aparece con su centro a esta altura, tocando el pasto
        penalty_x = self.declare_parameter('penalty_x', 3.0).value
        self.timeout_ms = self.declare_parameter('timeout_ms', 3000).value

        self.locations = {
            SpawnBall.Request.CENTER: (0.0, 0.0),
            SpawnBall.Request.PENALTY_POS_X: (penalty_x, 0.0),
            SpawnBall.Request.PENALTY_NEG_X: (-penalty_x, 0.0),
        }

        self.gz = GzNode()
        self.create_service(SpawnBall, 'spawn_ball', self.on_spawn_ball)
        self.create_service(Trigger, 'reset_ball', self.on_reset_ball)
        self.create_service(Trigger, 'reset_world', self.on_reset_world)
        self.get_logger().info(f'Servicios listos [{self.world}]')

    def gz_request(self, service, request, request_type, response_type):
        return self.gz.request(f'/world/{self.world}/{service}', request,
                               request_type, response_type, self.timeout_ms)

    def ball_names(self):
        """Nombres de los balones en el mundo: "ball" y "ball_<n>"."""
        ok, scene = self.gz_request('scene/info', Empty(), Empty, Scene)
        if not ok:
            raise RuntimeError(f'Gazebo no responde en /world/{self.world}/scene/info')
        return [m.name for m in scene.model
                if m.name == BALL_NAME or m.name.startswith(BALL_NAME + '_')]

    def spawn(self, name, x, y):
        req = EntityFactory()
        req.sdf_filename = self.ball_model
        req.name = name
        req.pose.position.x = x
        req.pose.position.y = y
        req.pose.position.z = self.ball_radius
        ok, rep = self.gz_request('create', req, EntityFactory, Boolean)
        return ok and rep.data

    def remove(self, name):
        req = Entity()
        req.name = name
        req.type = Entity.MODEL
        ok, rep = self.gz_request('remove', req, Entity, Boolean)
        return ok and rep.data

    def wait_until_gone(self, names, timeout_s=2.0):
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if not set(names) & set(self.ball_names()):
                return True
            time.sleep(0.05)
        return False

    def on_spawn_ball(self, request, response):
        if request.location == SpawnBall.Request.CUSTOM:
            x, y = request.x, request.y
        elif request.location in self.locations:
            x, y = self.locations[request.location]
        else:
            self.get_logger().error(f'location desconocida: {request.location}')
            response.success = False
            return response

        try:
            existing = set(self.ball_names())
        except RuntimeError as e:
            self.get_logger().error(str(e))
            response.success = False
            return response

        name, n = BALL_NAME, 1
        while name in existing:
            name, n = f'{BALL_NAME}_{n}', n + 1

        response.success = self.spawn(name, x, y)
        response.name = name if response.success else ''
        self.get_logger().info(f'spawn_ball {name} en ({x:.2f}, {y:.2f}): {response.success}')
        return response

    def on_reset_ball(self, request, response):
        try:
            names = self.ball_names()
            for name in names:
                self.remove(name)
            if not self.wait_until_gone(names):
                raise RuntimeError('Gazebo no terminó de borrar los balones')
        except RuntimeError as e:
            response.success, response.message = False, str(e)
            return response

        response.success = self.spawn(BALL_NAME, 0.0, 0.0)
        response.message = (f'borrados {len(names)} balones, "{BALL_NAME}" en el centro'
                            if response.success else 'no se pudo crear el balón')
        self.get_logger().info(f'reset_ball: {response.message}')
        return response

    def on_reset_world(self, request, response):
        req = WorldControl()
        req.reset.all = True
        ok, rep = self.gz_request('control', req, WorldControl, Boolean)
        response.success = ok and rep.data
        response.message = 'mundo reiniciado' if response.success else 'Gazebo no respondió'
        self.get_logger().info(f'reset_world: {response.message}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = FieldServices()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()
