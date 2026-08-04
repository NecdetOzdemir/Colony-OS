#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import time
import random
import uuid

from colony_config import CC
from colony_interfaces.msg import Task, Bid, WorkerStatus
from colony_interfaces.srv import AssignTask

class QueenNode(Node):
    def __init__(self):
        super().__init__('queen_node')
        self.get_logger().info('👑 Queen Node (Ana Üs) Başlatıldı!')

        # Algoritma kontrolü
        self.algorithm = CC.ALGORITHM
        self.get_logger().info(f'Seçili Algoritma: {self.algorithm}')

        # --- DURUM (STATE) YÖNETİMİ ---
        self.workers = {}  # {worker_id: WorkerStatus}
        self.pending_tasks = []  # Bekleyen görevler (Task)
        self.active_auctions = {} # {task_id: {'task': Task, 'bids': [Bid], 'timeout': time.time() + 2.0}}

        # --- YAYINCILAR (PUBLISHERS) ---
        self.auction_pub = self.create_publisher(Task, 'auction/tasks', 10)

        # --- ABONELİKLER (SUBSCRIBERS) ---
        self.create_subscription(WorkerStatus, 'worker_status', self.worker_status_callback, 10)
        self.create_subscription(Bid, 'auction/bids', self.bid_callback, 10)

        # --- İSTEMCİLER (CLIENTS) ---
        # Her işçi için AssignTask istemcisi oluşturulacak (Dinamik)
        self.assign_clients = {}

        # --- ZAMANLAYICILAR (TIMERS) ---
        # 1. Görev Üretici (Task Generator)
        self.create_timer(10.0, self.generate_random_task)
        # 2. İhale Yöneticisi (Auction Manager)
        self.create_timer(0.5, self.manage_auctions)

    def worker_status_callback(self, msg):
        """İşçilerin durumlarını (şarj, konum, meşguliyet) takip eder"""
        self.workers[msg.worker_id] = msg
        # TODO: Şarjı bitmek üzere olan işçileri Ana Üs'se (Base Station) çağır

    def generate_random_task(self):
        """Rastgele depo görevleri üretir"""
        if len(self.workers) == 0:
            self.get_logger().info("Görev üretilemedi: Hiç aktif işçi yok.")
            return

        task = Task()
        task.task_id = str(uuid.uuid4())[:8]
        task.task_type = random.choice(["PICK", "PLACE"])
        task.object_id = random.choice(["A", "B", "C"])
        
        # Rastgele hedefler (depo sınırları içinde)
        task.target_x = random.uniform(2.0, 8.0)
        task.target_y = random.uniform(-4.0, 4.0)
        task.target_z = 0.5
        
        task.priority = random.randint(1, 10)
        task.status = "PENDING"
        task.created_at = time.time()

        self.pending_tasks.append(task)
        self.get_logger().info(f'Yeni Görev Üretildi: {task.task_id} ({task.task_type} {task.object_id})')

    def manage_auctions(self):
        """MRTA İhale Yöneticisi"""
        # 1. Bekleyen görevleri ihaleye çıkar
        while self.pending_tasks:
            task = self.pending_tasks.pop(0)
            self.start_auction(task)

        # 2. Süresi dolan ihaleleri sonuçlandır
        current_time = time.time()
        completed_auctions = []

        for task_id, auction in self.active_auctions.items():
            if current_time >= auction['timeout']:
                self.resolve_auction(task_id, auction)
                completed_auctions.append(task_id)

        # Bitmiş ihaleleri temizle
        for task_id in completed_auctions:
            del self.active_auctions[task_id]

    def start_auction(self, task):
        """Yeni bir ihale başlatır"""
        self.active_auctions[task.task_id] = {
            'task': task,
            'bids': [],
            'timeout': time.time() + 2.0  # 2 saniye teklif toplama süresi
        }
        self.auction_pub.publish(task)
        self.get_logger().info(f'📢 İhale Açıldı: {task.task_id}')

    def bid_callback(self, msg):
        """İşçilerden gelen teklifleri toplar"""
        if msg.task_id in self.active_auctions:
            self.active_auctions[msg.task_id]['bids'].append(msg)
            self.get_logger().info(f'📥 Teklif Alındı: {msg.worker_id} -> Maliyet: {msg.cost:.2f}')

    def resolve_auction(self, task_id, auction):
        """İhaleyi sonuçlandırır ve görevi atar"""
        bids = auction['bids']
        task = auction['task']

        if not bids:
            self.get_logger().warn(f'⚠️ İhale İptal: {task_id} için hiç teklif gelmedi. Yeniden sıraya alınıyor.')
            self.pending_tasks.append(task)
            return

        # En düşük maliyetli teklifi bul
        winning_bid = min(bids, key=lambda b: b.cost)
        self.get_logger().info(f'🏆 İhaleyi Kazanan: {winning_bid.worker_id} (Görev: {task_id}, Maliyet: {winning_bid.cost:.2f})')

        self.assign_task_to_worker(task, winning_bid.worker_id)

    def assign_task_to_worker(self, task, worker_id):
        """Görevi kazanan işçiye resmî olarak atar (Service çağrısı ile)"""
        srv_name = f'/{worker_id}/assign_task'
        
        if srv_name not in self.assign_clients:
            self.assign_clients[srv_name] = self.create_client(AssignTask, srv_name)
        
        client = self.assign_clients[srv_name]
        
        if not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().error(f'{worker_id} servisi ulaşılamaz durumda!')
            # İşçi çökmüş olabilir, görevi tekrar sıraya al
            self.pending_tasks.append(task)
            return

        req = AssignTask.Request()
        req.task = task
        req.worker_id = worker_id
        
        # Asenkron servis çağrısı
        future = client.call_async(req)
        future.add_done_callback(lambda f: self.assign_callback(f, task.task_id, worker_id))

    def assign_callback(self, future, task_id, worker_id):
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
