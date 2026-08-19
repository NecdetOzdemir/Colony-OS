# Colony-OS — WorkerStatus Mesajı
# İşçinin Kraliçe'ye düzenli olarak bildirdiği durum

# İşçi kimliği (örn: "worker_1")
string worker_id

# Durum: "IDLE" | "BUSY" | "NAVIGATING" | "MANIPULATING" | "ERROR"
string state

# Üstlendiği mevcut görevin ID'si (boşta ise "")
string current_task_id

# İşçinin anlık konumu (Gazebo world frame)
float64 pos_x
float64 pos_y
float64 pos_yaw

# Mevcut görevdeki ilerleme (0.0 - 1.0), boşta ise 0.0
float32 progress

# Durum mesajı güncellenme zamanı
float64 timestamp
float32 battery_level
