# Colony-OS — Task Mesajı
# Kraliçe'nin İşçilere atadığı görev tanımı

# Görev kimliği (benzersiz)
string task_id

# Görev tipi: "PICK" veya "PLACE"
string task_type

# Nesne tipi: "A", "B" veya "C"
string object_id

# Hedef 3D koordinat (metre, Gazebo world frame)
float64 target_x
float64 target_y
float64 target_z

# Öncelik: yüksek sayı = yüksek öncelik (0-10)
int32 priority

# Durum: "PENDING" | "ASSIGNED" | "IN_PROGRESS" | "DONE" | "FAILED"
string status

# Görev oluşturulma zamanı (Unix epoch, saniye)
float64 created_at
