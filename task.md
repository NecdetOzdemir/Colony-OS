# Colony-OS — TODO Listesi

> Son güncelleme: 2026-08-04
> Durum: 🔴 Başlamadı | 🟡 Devam Ediyor | 🟢 Tamamlandı
> Build: `colony_config` ✅ 0.85s | `colony_interfaces` ✅ 6.34s

---

## 🏗️ AŞAMA 0 — Proje Altyapısı & Konfigürasyon

- [x] **0.1** ROS 2 workspace iskeletini oluştur (`src/` dizini, `colcon build` testi)
- [x] **0.2** `colony_config` merkezi konfigürasyon paketi yaz
  - [x] **0.2.1** `config.py` — tüm global parametreler (robot sayısı, hız, port vs.)
  - [ ] **0.2.2** `params.yaml` — ROS 2 launch'ta parametre geçişi için
  - [x] **0.2.3** `__init__.py` — paketi import edilebilir yap
  - [x] **0.2.4** `package.xml` + `setup.py` dosyaları
- [x] **0.3** `.agents/AGENTS.md` ajan kurallarını yaz
- [x] **0.4** Proje `README.md` oluştur
- [x] **0.5** `.gitignore` ekle (build/, install/, log/ vs.)
- [x] **0.6** Eksik paket kurulumu (nav2-bringup, xacro, robot-state-publisher)

---

## 📦 AŞAMA 1 — colony_interfaces (Mesaj/Servis/Action Tanımları)

- [x] **1.1** Paket iskeletini oluştur (`package.xml`, `CMakeLists.txt`)
- [x] **1.2** `Task.msg` tanımla
  - [x] task_id, task_type (PICK/PLACE), object_id
  - [x] target_x, target_y, target_z (3D koordinat)
  - [x] priority, status
- [x] **1.3** `Bid.msg` tanımla
  - [x] worker_id, task_id, cost (tahmini mesafe/süre), timestamp
- [x] **1.4** `WorkerStatus.msg` tanımla
  - [x] worker_id, state (IDLE/BUSY/ERROR), current_task_id, position
- [x] **1.5** `AssignTask.srv` tanımla
  - [x] Request: task + worker_id
  - [x] Response: success + message
- [x] **1.6** `ExecuteTask.action` tanımla
  - [x] Goal: Task
  - [x] Result: success, completion_time
  - [x] Feedback: progress (0.0-1.0), current_phase
- [x] **1.7** `colcon build` ile derleme testi

---

## 🌍 AŞAMA 2 — colony_description (Robot & Dünya Modelleri)

- [x] **2.1** Paket iskeletini oluştur
- [x] **2.2** Depo dünyası SDF dosyası (`warehouse.sdf`)
  - [x] Zemin, duvarlar
  - [x] Raf sistemi (en az 4 raf — `colony_config`'den boyutlar gelecek)
  - [x] Pick istasyonları (A, B, C tipi)
  - [x] Place istasyonları
  - [x] Işıklandırma
- [x] **2.3** A/B/C tipi nesne SDF modelleri
- [x] **2.4** Husky mobil taban URDF/xacro
  - [x] Tekerlek fizik özellikleri
  - [x] Sanal Lidar sensörü (laser_scan)
  - [x] Odometri plugin
  - [x] diff_drive_controller
- [x] **2.5** Worker robot birleştirme (Husky + basit kol ya da sadece mobil)
- [x] **2.6** Gazebo'da spawn testi (tek robot)
- [x] **2.7** `ros_gz_bridge` topic mapping testi (LaserScan, Odometry, Cmd_vel)

---

## 🧭 AŞAMA 3 — colony_navigation (İşçi Navigasyonu)

- [ ] **3.1** Nav2 bringup kurulumu ve test
- [ ] **3.2** `nav2_params.yaml` konfigürasyonu
  - [ ] AMCL (localization) parametreleri
  - [ ] Planner (NavFn) parametreleri
  - [ ] Controller (DWB) parametreleri
  - [ ] Costmap parametreleri (global + local)
- [ ] **3.3** Harita oluşturma (statik `/map` topic veya map_server)
- [ ] **3.4** Tek robot otonom navigasyon testi (hedefe gitme)
- [ ] **3.5** Dinamik engelden kaçınma testi (birden fazla robot)
- [ ] **3.6** `NavigateToPose` action ile programatik hedef gönderme

---

## 🦾 AŞAMA 4 — colony_manipulation (Nesne Alma/Bırakma)

- [ ] **4.1** MoveIt 2 konfigürasyonu (SRDF, kinematics.yaml)
- [ ] **4.2** Temel pick & place motioni testi
- [ ] **4.3** Simüle gripper (nesneyi attach/detach etme)
- [ ] **4.4** Pick & place action client helper yazma
- [ ] **4.5** Nav2 + MoveIt entegrasyonu (robotic pipeline testi)

---

## 👑 AŞAMA 5 — colony_queen (Kraliçe MRTA Algoritması)

- [ ] **5.1** Paket iskeletini oluştur
- [ ] **5.2** `fcfs_allocator.py` — Baseline FCFS algoritması
  - [ ] Task queue yönetimi
  - [ ] İlk boşta olan worker'a atama
  - [ ] ROS 2 action server entegrasyonu
- [ ] **5.3** `auction_allocator.py` — Açık Artırma algoritması
  - [ ] İlan yayınlama (Task broadcast)
  - [ ] Bid toplama (timeout ile)
  - [ ] Minimum maliyet değerlendirme
  - [ ] Görev atama kararı
  - [ ] ROS 2 action server entegrasyonu
- [ ] **5.4** `queen_node.py` — Ana Kraliçe ROS 2 node
  - [ ] Algoritmayı `colony_config`'den seç (FCFS / AUCTION)
  - [ ] Task listesi yönetimi
  - [ ] Worker durumu takibi
- [ ] **5.5** Birim testleri (simülatörsüz, mock worker ile)
  - [ ] FCFS doğruluk testi
  - [ ] Auction teklif toplama testi
  - [ ] Edge case: tek worker, 0 worker

---

## 🤖 AŞAMA 6 — colony_worker (İşçi Robot Düğümleri)

- [ ] **6.1** Paket iskeletini oluştur
- [ ] **6.2** `worker_node.py` — Ana işçi ROS 2 node
  - [ ] Kraliçe'ye kayıt (register)
  - [ ] Durum yayınlama (WorkerStatus publisher)
  - [ ] Bid hesaplama ve gönderme
  - [ ] Görev alma (action server)
- [ ] **6.3** `bid_calculator.py` — Maliyet hesaplama modülü
  - [ ] Nav2 planlama servisi ile mesafe/süre hesabı
  - [ ] Mevcut görev yükü faktörü
- [ ] **6.4** Çoklu worker namespace testi (worker_1, worker_2, ...)
- [ ] **6.5** Worker'ın Kraliçe ile tam iletişim testi

---

## 📊 AŞAMA 7 — colony_logger (Performans Kaydedici)

- [ ] **7.1** `performance_logger.py` ROS 2 node
  - [ ] Görev başlangıç/bitiş zamanlarını kaydet
  - [ ] Worker utilization oranını kaydet
  - [ ] `.csv` dosyasına yaz (`colony_config`'den dosya yolu)
- [ ] **7.2** CSV formatı tanımla:
  - [ ] task_id, algorithm, worker_id, start_time, end_time, duration, distance
- [ ] **7.3** Gerçek zamanlı istatistik yayınlama (ROS 2 topic)

---

## 🚀 AŞAMA 8 — colony_bringup (Launch Dosyaları)

- [ ] **8.1** `simulation.launch.py` — Tüm sistemi tek komutla başlat
  - [ ] Gazebo dünyasını başlat
  - [ ] N adet worker robot spawn et (`colony_config`'den N gelir)
  - [ ] Nav2 stack başlat
  - [ ] Kraliçe node başlat
  - [ ] Logger başlat
- [ ] **8.2** `benchmark.launch.py` — Benchmark test launcher
  - [ ] FCFS modu
  - [ ] Auction modu
  - [ ] Otomatik senaryo başlatma
- [ ] **8.3** Sistem entegrasyon testi (tüm bileşenler birlikte)

---

## 🧪 AŞAMA 9 — Benchmark Testleri (İP 5)

- [ ] **9.1** Test senaryosu tanımla (`colony_config`'den parametreler)
  - [ ] 5 İşçi robot
  - [ ] 50 görev (A/B/C tipi karma)
  - [ ] 10 dakika simülasyon süresi
- [ ] **9.2** FCFS algoritması ile tam senaryo testi
- [ ] **9.3** Auction algoritması ile tam senaryo testi
- [ ] **9.4** CSV verileri topla
- [ ] **9.5** Python analiz scripti (`analysis/analyze_results.py`)
  - [ ] Ortalama görev tamamlama süresi
  - [ ] Throughput (görev/dak)
  - [ ] Utilization oranı (%)
  - [ ] Matplotlib grafikleri
- [ ] **9.6** Sonuçları yorumla — Auction vs FCFS karşılaştırma raporu

---

## 📈 İlerleme Özeti

| Aşama | Tamamlanan | Toplam | % |
|-------|-----------|--------|---|
| 0 - Altyapı | 6 | 6 | **100%** ✅ |
| 1 - Interfaces | 7 | 7 | **100%** ✅ |
| 2 - Description | 7 | 7 | **100%** ✅ |
| 3 - Navigation | 0 | 6 | 0% |
| 4 - Manipulation | 0 | 5 | 0% |
| 5 - Queen | 0 | 5 | 0% |
| 6 - Worker | 0 | 5 | 0% |
| 7 - Logger | 0 | 3 | 0% |
| 8 - Bringup | 0 | 3 | 0% |
| 9 - Benchmark | 0 | 6 | 0% |
| **TOPLAM** | **20** | **53** | **37%** |
