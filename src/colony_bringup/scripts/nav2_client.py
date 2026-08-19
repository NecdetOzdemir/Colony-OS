#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import sys

class Nav2Client(Node):
    def __init__(self):
        super().__init__('nav2_test_client')
        self._action_client = ActionClient(self, NavigateToPose, '/navigate_to_pose')

    def send_goal(self, x, y):
        self.get_logger().info('Action server bekleniyor...')
        self._action_client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0
        
        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Hedef gönderiliyor: X: {x}, Y: {y}')
        
        self._send_goal_future = self._action_client.send_goal_async(goal_msg, feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Hedef reddedildi!')
            return

        self.get_logger().info('Hedef kabul edildi, rotada ilerleniyor...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        # Sadece x ve y koordinatlarını yazdır (çok kalabalık olmaması için)
        x = feedback.current_pose.pose.position.x
        y = feedback.current_pose.pose.position.y
        self.get_logger().info(f'Mevcut Konum: X: {x:.2f}, Y: {y:.2f}')

    def get_result_callback(self, future):
        result = future.result().result
        status = future.result().status
        
        if status == 4: # SUCCEEDED
            self.get_logger().info('✅ Hedefe başarıyla ulaşıldı!')
        else:
            self.get_logger().info(f'❌ Hedef başarısız oldu. Durum kodu: {status}')
            
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    
    if len(sys.argv) < 3:
        print("Kullanım: python3 nav2_client.py <X_HEDEFI> <Y_HEDEFI>")
        print("Örnek: python3 nav2_client.py 2.0 2.0")
        sys.exit(1)
        
    x_target = sys.argv[1]
    y_target = sys.argv[2]

    nav2_client = Nav2Client()
    nav2_client.send_goal(x_target, y_target)
    
    rclpy.spin(nav2_client)

if __name__ == '__main__':
    main()
