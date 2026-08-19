#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
import math

from colony_config import CC
from colony_interfaces.msg import Task, Bid, WorkerStatus
from colony_interfaces.srv import AssignTask
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry

class WorkerNode(Node):
    def __init__(self):
        super().__init__('worker_node')
        
        self.declare_parameter('worker_id', 'worker_1')
        self.worker_id = self.get_parameter('worker_id').value
        
        self.get_logger().info(f'🤖 {self.worker_id} (İşçi Robot) Başlatıldı!')

        # --- DURUM BİLGİLERİ ---
        self.state = "IDLE"
        self.battery = 100.0
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_task = None

        # --- YAYINCILAR VE ABONELİKLER ---
        self.status_pub = self.create_publisher(WorkerStatus, CC.TOPIC_WORKER_STATUS, 10)
        self.bid_pub = self.create_publisher(Bid, CC.TOPIC_BID, 10)
        
        self.create_subscription(Task, CC.TOPIC_TASK_BROADCAST, self.auction_callback, 10)
        self.create_subscription(Odometry, 'odom', self.odom_callback, 10)

        # --- SERVİS (GÖREV ATAMA) ---
        self.assign_srv = self.create_service(AssignTask, f'/{self.worker_id}/assign_task', self.assign_task_callback)

        # --- ACTION CLIENT (NAV2) ---
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        # --- ZAMANLAYICI ---
        self.create_timer(1.0, self.publish_status)

        # Asenkron manipülasyon zamanlayıcısı için referans
        self.manipulation_timer = None

    def get_current_time_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def odom_callback(self, msg: Odometry) -> None:
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def publish_status(self) -> None:
        msg = WorkerStatus()
        msg.worker_id = self.worker_id
        msg.state = self.state
        msg.pos_x = self.current_x
        msg.pos_y = self.current_y

        self.status_pub.publish(msg)

    def auction_callback(self, task: Task) -> None:
        if self.state != "IDLE" or self.battery < 20.0:
            return

        distance = math.hypot(task.target_x - self.current_x, task.target_y - self.current_y)
        cost = distance / CC.WORKER_MAX_SPEED

        bid = Bid()
        bid.worker_id = self.worker_id
        bid.task_id = task.task_id
        bid.cost = float(cost)
        self.bid_pub.publish(bid)
        self.get_logger().info(f'💸 {task.task_id} için teklif verildi. Maliyet: {cost:.2f}')

    def assign_task_callback(self, request, response):
        task = request.task
        
        if self.state != "IDLE":
            response.success = False
            response.message = "İşçi şu an meşgul."
            return response

        # Nav2 Server hazır mı diye asenkron (bloklamadan) kontrol et
        if not self.nav_client.server_is_ready():
            self.get_logger().error('Nav2 action server hazır değil!')
            response.success = False
            response.message = "Nav2 Server hazır değil."
            return response

        self.get_logger().info(f'📦 Görev Alındı: {task.task_id} -> Hedef: ({task.target_x:.2f}, {task.target_y:.2f})')
        self.current_task = task
        self.state = "NAVIGATING"
        
        # Görevi yürütmeye başla
        self.execute_task(task)

        response.success = True
        response.message = "Görev kabul edildi ve navigasyon başladı."
        return response

    def execute_task(self, task: Task) -> None:
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = task.target_x
        goal_msg.pose.pose.position.y = task.target_y
        goal_msg.pose.pose.orientation.w = 1.0
        
        send_goal_future = self.nav_client.send_goal_async(goal_msg)
        send_goal_future.add_done_callback(self.nav_goal_response_callback)

    def nav_goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Nav2 hedefi reddedildi!')
            self.state = "IDLE"
            self.current_task = None
            return

        self.get_logger().info('Nav2 hedefi kabul edildi, hareket ediliyor...')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.nav_result_callback)

    def nav_result_callback(self, future):
        """Navigasyon bittiğinde manipülasyona (MoveIt) geçer"""
        self.get_logger().info('📍 Hedefe ulaşıldı! Manipülasyon (Pick/Place) başlıyor...')
        self.state = "MANIPULATING"
        
        # ASENKRON BEKLEME: time.sleep(3.0) yerine tek seferlik timer kullanıyoruz
        self.manipulation_timer = self.create_timer(3.0, self.finish_manipulation)

    def finish_manipulation(self):
        """Manipülasyon tamamlandığında (timer tetiklendiğinde) çağrılır"""
        # Timer'ı iptal et (sadece 1 kez çalışması için)
        if self.manipulation_timer is not None:
            self.manipulation_timer.cancel()
            self.manipulation_timer = None

        self.get_logger().info(f'✅ Görev {self.current_task.task_id} tamamlandı!')
        self.state = "IDLE"
        self.current_task = None

def main(args=None):
    rclpy.init(args=args)
    node = WorkerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
