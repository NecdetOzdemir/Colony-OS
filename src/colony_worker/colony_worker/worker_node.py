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
        self.nav_sim_timer = None

    def get_current_time_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def odom_callback(self, msg: Odometry) -> None:
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y

    def publish_status(self) -> None:
        # Batarya düşüşü simülasyonu
        if self.state in ["NAVIGATING", "MANIPULATING"]:
            self.battery = max(0.0, self.battery - CC.BATTERY_DRAIN_PER_SEC)

        msg = WorkerStatus()
        msg.worker_id = self.worker_id
        msg.state = self.state
        msg.pos_x = self.current_x
        msg.pos_y = self.current_y
        msg.pos_yaw = 0.0
        msg.battery_level = float(self.battery)
        msg.current_task_id = self.current_task.task_id if self.current_task else ""
        msg.progress = 50.0 if self.state == "NAVIGATING" else (100.0 if self.state == "MANIPULATING" else 0.0)
        msg.timestamp = self.get_current_time_sec()

        self.status_pub.publish(msg)

    def auction_callback(self, task: Task) -> None:
        if self.state != "IDLE" or self.battery < CC.BATTERY_MIN_BID_THRESHOLD:
            return

        distance = math.hypot(task.target_x - self.current_x, task.target_y - self.current_y)
        cost = distance / CC.WORKER_MAX_SPEED

        bid = Bid()
        bid.worker_id = self.worker_id
        bid.task_id = task.task_id
        bid.cost = float(cost)
        bid.timestamp = self.get_current_time_sec()
        bid.worker_x = self.current_x
        bid.worker_y = self.current_y
        
        self.bid_pub.publish(bid)
        self.get_logger().info(f'💸 {task.task_id} için teklif verildi. Maliyet: {cost:.2f}')

    def assign_task_callback(self, request, response):
        task = request.task
        
        if self.state != "IDLE":
            response.success = False
            response.message = "İşçi şu an meşgul."
            return response

        # Nav2 Server hazır mı diye asenkron (bloklamadan) kontrol et (Eğer Nav2 açıksa)
        if CC.NAV2_ENABLED and not self.nav_client.server_is_ready():
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
        if not CC.NAV2_ENABLED:
            self.get_logger().info('⚠️ Nav2 KAPALI: Sürüş 3 saniye simüle edilecek...')
            self.nav_sim_timer = self.create_timer(3.0, self.nav_result_callback)
            return

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

    def nav_result_callback(self, future=None):
        """Navigasyon bittiğinde manipülasyona (MoveIt) geçer"""
        # Eğer Nav2 kapalıysa ve timer tetiklediyse, o timer'ı iptal et
        if self.nav_sim_timer is not None:
            self.nav_sim_timer.cancel()
            self.nav_sim_timer = None

        self.get_logger().info('📍 Hedefe ulaşıldı! Manipülasyon (Pick/Place) başlıyor...')
        self.state = "MANIPULATING"
        
        # Konumu hedefe eşitle (simülasyon için)
        if self.current_task:
            self.current_x = self.current_task.target_x
            self.current_y = self.current_task.target_y

        # ASENKRON BEKLEME: time.sleep(3.0) yerine tek seferlik timer kullanıyoruz
        self.manipulation_timer = self.create_timer(3.0, self.finish_manipulation)

    def finish_manipulation(self):
        """Manipülasyon tamamlandığında (timer tetiklendiğinde) çağrılır"""
        # Timer'ı iptal et (sadece 1 kez çalışması için)
        if self.manipulation_timer is not None:
            self.manipulation_timer.cancel()
            self.manipulation_timer = None

        self.get_logger().info(f'✅ Görev {self.current_task.task_id} tamamlandı!')
        
        # Batarya şarjını simüle et
        self.battery = min(100.0, self.battery + CC.BATTERY_CHARGE_PER_TASK)
        self.get_logger().info(f'🔋 Şarj durumu: {self.battery:.1f}%')

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
