#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import csv
import os
import time

from colony_config import CC
from colony_interfaces.msg import Task, WorkerStatus

class DataLoggerNode(Node):
    def __init__(self):
        super().__init__('data_logger_node')
        self.get_logger().info('📊 Data Logger (Veri Toplayıcı) Başlatıldı!')

        # Parametreler
        self.results_dir = os.path.join(os.path.expanduser('~'), 'Colony-OS', 'results')
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

        # Dosya ismi algoritma ve tarih içeriyor
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.csv_file = os.path.join(self.results_dir, f'experiment_{CC.ALGORITHM}_{timestamp}.csv')

        # Veri yapıları
        self.total_tasks_created = 0
        self.worker_stats = {}  # {worker_id: {'tasks_completed': 0, 'battery_used': 0.0, 'last_battery': 100.0}}
        self.start_time = time.time()

        # CSV başlık yaz
        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Algorithm', 'TotalTasksCreated', 'ActiveWorkers', 'AvgBattery'])

        # Subscriptions
        self.create_subscription(Task, '/auction/tasks', self.task_callback, 10)
        self.create_subscription(WorkerStatus, '/worker_status', self.worker_status_callback, 10)

        # Periyodik kayıt (5 saniyede bir CSV'ye satır ekle)
        self.create_timer(5.0, self.log_to_csv)

    def task_callback(self, msg):
        self.total_tasks_created += 1

    def worker_status_callback(self, msg):
        wid = msg.worker_id
        if wid not in self.worker_stats:
            self.worker_stats[wid] = {
                'tasks_completed': 0,
                'battery_used': 0.0,
                'last_battery': msg.battery_level
            }
        
        # Batarya tüketimi hesabı
        battery_diff = self.worker_stats[wid]['last_battery'] - msg.battery_level
        if battery_diff > 0:
            self.worker_stats[wid]['battery_used'] += battery_diff
        
        self.worker_stats[wid]['last_battery'] = msg.battery_level
        
        # Görev tamamlama sayacı eklenebilir (AssignTask response vs)
        # Şimdilik batarya odaklı.

    def log_to_csv(self):
        active_workers = len(self.worker_stats)
        if active_workers == 0:
            avg_battery = 0.0
        else:
            avg_battery = sum([v['last_battery'] for v in self.worker_stats.values()]) / active_workers

        current_time = time.time() - self.start_time

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f'{current_time:.2f}', CC.ALGORITHM, self.total_tasks_created, active_workers, f'{avg_battery:.2f}'])

def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
