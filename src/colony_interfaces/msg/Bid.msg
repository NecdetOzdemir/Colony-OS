# Colony-OS — Bid (Teklif) Mesajı
# İşçinin, Kraliçe'nin açtığı ihalede verdiği teklif

# Teklifi veren işçinin kimliği (örn: "worker_1")
string worker_id

# Hangi göreve teklif veriliyor
string task_id

# Maliyet tahmini — düşük = daha iyi (mesafe veya süre)
# Nav2 planlama servisiyle hesaplanır
float64 cost

# Teklif verildiği zaman (Unix epoch, saniye)
float64 timestamp

# İşçinin şu anki konumu (teklif anında)
float64 worker_x
float64 worker_y
