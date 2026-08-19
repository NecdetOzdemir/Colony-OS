#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import random
import uuid

from colony_config import CC
from colony_interfaces.msg import Task, Bid, WorkerStatus
from colony_interfaces.srv import AssignTask

class QueenNode(Node):
    def __init__(self):
        super().__init__('queen_node')
        self.get_logger().info('👑 Queen Node (Ana Üs) Başlatıldı!')

        self.algorithm = CC.ALGORITHM
        self.get_logger().info(f'Seçili Algoritma: {self.algorithm}')

        # --- DURUM (STATE) YÖNETİMİ ---
        self.workers = {}
        self.pending_tasks = []
        self.active_auctions = {}

        # --- YAYINCILAR (PUBLISHERS) ---
        self.auction_pub = self.create_publisher(Task, CC.TOPIC_TASK_BROADCAST, 10)

        # --- ABONELİKLER (SUBSCRIBERS) ---
        self.create_subscription(WorkerStatus, CC.TOPIC_WORKER_STATUS, self.worker_status_callback, 10)
        self.create_subscription(Bid, CC.TOPIC_BID, self.bid_callback, 10)

        # --- İSTEMCİLER (CLIENTS) ---
        self.assign_clients = {}

        # --- ZAMANLAYICILAR (TIMERS) ---
        self.create_timer(10.0, self.generate_random_task)
        self.create_timer(0.5, self.manage_auctions)

    def get_current_time_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def worker_status_callback(self, msg: WorkerStatus) -> None:
        """İşçilerin durumlarını (şarj, konum, meşguliyet) takip eder"""
        self.workers[msg.worker_id] = msg

    def generate_random_task(self) -> None:
        """Rastgele depo görevleri üretir"""
        if not self.workers:
            self.get_logger().info("Görev üretilemedi: Hiç aktif işçi yok.")
            return

        task = Task()
        task.task_id = str(uuid.uuid4())[:8]
        task.task_type = random.choice(CC.TASK_TYPES)
        task.object_id = random.choice(CC.OBJECT_TYPES)
        
        task.target_x = random.uniform(2.0, 8.0)
        task.target_y = random.uniform(-4.0, 4.0)
        task.target_z = 0.5
        
        task.priority = random.randint(1, 10)
        task.status = "PENDING"
        task.created_at = self.get_current_time_sec()

        self.pending_tasks.append(task)
        self.get_logger().info(f'Yeni Görev Üretildi: {task.task_id} ({task.task_type} {task.object_id})')

    def manage_auctions(self) -> None:
        """MRTA İhale Yöneticisi"""
        while self.pending_tasks:
            task = self.pending_tasks.pop(0)
            self.start_auction(task)

        current_time = self.get_current_time_sec()
        completed_auctions = []

        for task_id, auction in self.active_auctions.items():
            if current_time >= auction['timeout']:
                self.resolve_auction(task_id, auction)
                completed_auctions.append(task_id)

        for task_id in completed_auctions:
            del self.active_auctions[task_id]

    def start_auction(self, task: Task) -> None:
        """Yeni bir ihale başlatır"""
        self.active_auctions[task.task_id] = {
            'task': task,
            'bids': [],
            'timeout': self.get_current_time_sec() + CC.AUCTION_TIMEOUT_SEC
        }
        self.auction_pub.publish(task)
        self.get_logger().info(f'📢 İhale Açıldı: {task.task_id}')

    def bid_callback(self, msg: Bid) -> None:
        """İşçilerden gelen teklifleri toplar"""
        if msg.task_id in self.active_auctions:
            self.active_auctions[msg.task_id]['bids'].append(msg)
            self.get_logger().info(f'📥 Teklif Alındı: {msg.worker_id} -> Maliyet: {msg.cost:.2f}')

    def resolve_auction(self, task_id: str, auction: dict) -> None:
        """İhaleyi sonuçlandırır ve görevi atar"""
        bids = auction['bids']
        task = auction['task']

        if not bids or len(bids) < CC.AUCTION_MIN_BIDS:
            self.get_logger().warn(f'⚠️ İhale İptal: {task_id} için yeterli teklif gelmedi. Yeniden sıraya alınıyor.')
            self.pending_tasks.append(task)
            return

        winning_bid = min(bids, key=lambda b: b.cost)
        self.get_logger().info(f'🏆 İhaleyi Kazanan: {winning_bid.worker_id} (Görev: {task_id}, Maliyet: {winning_bid.cost:.2f})')

        self.assign_task_to_worker(task, winning_bid.worker_id)

    def assign_task_to_worker(self, task: Task, worker_id: str) -> None:
        """Görevi kazanan işçiye resmî olarak atar (Service çağrısı ile)"""
        # Burada /worker_1 gibi dinamik namespace kullanıldığı için config'den çekmek zor olabilir
        # Sadece servis ismini worker_id/assign_task yapalım
        srv_name = f'/{worker_id}/assign_task'
        
        if srv_name not in self.assign_clients:
            self.assign_clients[srv_name] = self.create_client(AssignTask, srv_name)
        
        client = self.assign_clients[srv_name]
        
        # ASENKRON KONTROL: wait_for_service yerine service_is_ready()
        if not client.service_is_ready():
            self.get_logger().error(f'{worker_id} servisi şu an hazır değil! Görev sıraya alınıyor.')
            self.pending_tasks.append(task)
            return

        req = AssignTask.Request()
        req.task = task
        req.worker_id = worker_id
        
        future = client.call_async(req)
        future.add_done_callback(lambda f: self.assign_callback(f, task.task_id, worker_id))

    def assign_callback(self, future, task_id: str, worker_id: str) -> None:
        try:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ Görev {task_id}, {worker_id} robotuna başarıyla atandı.')
            else:
                self.get_logger().error(f'❌ Görev {task_id} atanamadı: {response.message}')
        except Exception as e:
            self.get_logger().error(f'Service çağrısında hata: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = QueenNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
