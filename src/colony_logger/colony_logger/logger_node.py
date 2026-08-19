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

        self.results_dir = os.path.join(os.path.expanduser('~'), 'Colony-OS', 'results')
        os.makedirs(self.results_dir, exist_ok=True)

        # Dosya ismi algoritma ve tarih içeriyor
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        self.csv_file = os.path.join(self.results_dir, f'experiment_{CC.ALGORITHM}_{timestamp}.csv')

        self.total_tasks_created = 0
        self.worker_stats = {}  

        self.start_time = self.get_current_time_sec()

        with open(self.csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Algorithm', 'TotalTasksCreated', 'ActiveWorkers', 'AvgBattery'])

        self.create_subscription(Task, CC.TOPIC_TASK_BROADCAST, self.task_callback, 10)
        self.create_subscription(WorkerStatus, CC.TOPIC_WORKER_STATUS, self.worker_status_callback, 10)

        self.create_timer(5.0, self.log_to_csv)

    def get_current_time_sec(self) -> float:
        return self.get_clock().now().nanoseconds / 1e9

    def task_callback(self, msg: Task) -> None:
        self.total_tasks_created += 1

    def worker_status_callback(self, msg: WorkerStatus) -> None:
        wid = msg.worker_id
        if wid not in self.worker_stats:
            self.worker_stats[wid] = {
                'tasks_completed': 0
            }

    def log_to_csv(self) -> None:
        active_workers = len(self.worker_stats)
        current_time = self.get_current_time_sec() - self.start_time

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([f'{current_time:.2f}', CC.ALGORITHM, self.total_tasks_created, active_workers, '0.00'])

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
