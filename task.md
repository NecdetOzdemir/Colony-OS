# 🐝 Colony-OS — Proje Ana Görev Panosu (Sıfırdan Başlangıç)

> **Proje Adı:** Colony-OS (Çoklu Robot Görev Dağıtım ve Yönetim Sistemi)  
> **Kullanım Amacı:** Bitirme Projesi Teslimi  
> **Çalışma Metodu:** Human-in-the-Loop (Her aşamada kod yazımı + Gazebo/RViz canlı insan onayı)  
> **Son Güncelleme:** 2026-08-04  

---

## ⚙️ AŞAMA 0 — Proje Mimarisi & Merkezi Konfigürasyon (`colony_config`)
- [x] **0.1** `colony_config` paket iskeleti ve `ColonyConfig` sınıfı
- [x] **0.2** Parametre doğrulama (`validate()` metodu)
- [x] **[İNSAN ONAYLANDI]** `python3 -c "from colony_config import CC; print(CC.NUM_WORKERS)"` komutu terminalde hatasız çıktı veriyor.

---

## 📦 AŞAMA 1 — Mesaj & Servis Tanımları (`colony_interfaces`)
- [x] **1.1** `Task.msg` (Görev ID, Hedef X/Y/Z, Tipi, Öncelik)
- [x] **1.2** `Bid.msg` (Robot ID, Görev ID, Maliyet)
- [x] **1.3** `WorkerStatus.msg` (Robot ID, Durum, Batarya Seviyesi, Konum X/Y)
- [x] **1.4** `AssignTask.srv` (Görev atama servisi)
- [x] **[İNSAN ONAYLANDI]** `ros2 interface show colony_interfaces/msg/Task` komutu mesaj yapısını ekrana bastı.

---

## 🏛️ AŞAMA 2 — Depo Dünyası & Fiziksel Çevre (`colony_description`)
- [x] **2.1** Gazebo depo dünyası (`warehouse.sdf`) ve duvarlar/raflar
- [x] **2.2** Sadece haritayı başlatan `world.launch.py`
- [x] **[İNSAN ONAYLANDI]** Gazebo açıldığında SIFIR ROBOT ile temiz depo haritası (duvarlar + raflar) görüntülendi. ROS `/clock` bağlı.

---

## 🤖 AŞAMA 3 — Tek Robot URDF & Fiziksel Doğrulama
- [x] **3.1** İşçi Robot URDF/Xacro (Husky şasi + 3-DOF Robot Kolu + Lidar)
- [x] **3.2** Gazebo DiffDrive, Lidar ve ROS 2 Control eklentilerinin tanımı
- [x] **3.3** Tek robotu başlatan `single_robot.launch.py`
- [x] **[İNSAN ONAYLANDI]** Gazebo ve RViz'de robot parçaları titrameden sabit duruyor. Topic izolasyonu (`/worker_1/scan`, `/worker_1/odom` vb.) tamam.

---

## 👥 AŞAMA 4 — Çoklu Robot Doğuşu & Namespace İzolasyonu
- [ ] **4.1** 3 robotun (`worker_1`, `worker_2`, `worker_3`) farklı koordinatlarda spawn edilmesi
- [ ] **4.2** İzole `robot_state_publisher` ve `ros_gz_bridge` (`/worker_1/cmd_vel`, `/worker_2/cmd_vel` vb.)
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Robotlar Gazebo'da birbirlerinin üstüne binmeden ayrık doğdu mu? TF çakışması var mı?

---

## 🗺️ AŞAMA 5 — Otonom Sürüş & Navigasyon (`colony_navigation` - Nav2)
- [ ] **5.1** Nav2 konfigürasyonu (AMCL, Costmaps, Planner, Controller)
- [ ] **5.2** Tek robot için `2D Goal Pose` harita testi
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Robot RViz'de harita üzerinde verilen hedefe engellere çarpmadan gidiyor mu?

---

## 🚦 AŞAMA 6 — Çoklu Robot Navigasyonu (Multi-Robot Nav2)
- [ ] **6.1** 3 robot için eşzamanlı Nav2 başlatılması
- [ ] **6.2** Her robota kendi isim uzayı (`/worker_X`) altında hedef verilmesi
- [ ] **[İNSAN ONAYI BEKLENİYOR]** 3 robot aynı haritada birbirlerine çarpmadan kendi hedeflerine ulaşıyor mu?

---

## 🦾 AŞAMA 7 — Manipülasyon & Kol Kontrolü (`colony_manipulation` - MoveIt 2)
- [ ] **7.1** MoveIt 2 SRDF ve kinematics konfigürasyonu
- [ ] **7.2** Robot kolunun Pick/Place eylemi simülasyonu
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Robot hedefe ulaştığında robot kolu kalkıp nesneyi alma hareketi yapıyor mu?

---

## 👑 AŞAMA 8 — Kraliçe & İşçi İhale Mantığı (`colony_queen` & `colony_worker`)
- [ ] **8.1** Kraliçe (`queen_node.py`): Rasgele görev açma ve İhale (Auction) yönetimi
- [ ] **8.2** İşçi (`worker_node.py`): Mesafe/batarya maliyet hesabı yapıp teklif (Bid) atma
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Terminalde ihalelerin açıldığı, tekliflerin toplandığı ve en yakın robota görevin verildiği izleniyor mu?

---

## 📊 AŞAMA 9 — Veri Toplama & Tam Sistem Entegrasyonu (`colony_logger` & `colony_bringup`)
- [ ] **9.1** `logger_node.py` ile batarya ve süre metriklerinin CSV'ye kaydedilmesi
- [ ] **9.2** Tüm sistemin `system.launch.py` ile tek komutta ayağa kaldırılması
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Tek tıkla tüm sistem (Gazebo + Nav2 + Queen + Worker + Logger) sorunsuz çalışıyor mu?

---

## 📈 AŞAMA 10 — Benchmark & Grafik Raporlaması (Bitirme Projesi Finali)
- [ ] **10.1** FCFS vs. AUCTION algoritmalarının simülasyon testleri
- [ ] **10.2** `analysis/analyze_results.py` ile karşılaştırma grafiklerinin (.png) üretilmesi
- [ ] **[İNSAN ONAYI BEKLENİYOR]** Grafikler ve rapor bitirme projesi sunumuna hazır mı?

---

## 📊 İlerleme Tablosu

| Aşama | Adı | Durum | Tamamlanan / Toplam | % |
|-------|-----|-------|---------------------|---|
| **0** | Proje Mimarisi & Config | 🟢 **Tamamlandı** | 2 / 2 | 100% ✅ |
| **1** | Mesaj & Servisler | 🟢 **Tamamlandı** | 4 / 4 | 100% ✅ |
| **2** | Depo Dünyası & Fizik | 🟢 **Tamamlandı** | 2 / 2 | 100% ✅ |
| **3** | Tek Robot URDF & TF | 🟢 **Tamamlandı** | 3 / 3 | 100% ✅ |
| **4** | Çoklu Robot & Namespace | 🟡 Bekliyor | 0 / 2 | 0% |
| **5** | Tek Robot Navigasyon | 🟡 Bekliyor | 0 / 2 | 0% |
| **6** | Çoklu Robot Navigasyon | 🟡 Bekliyor | 0 / 2 | 0% |
| **7** | Manipülasyon & Kol | 🟡 Bekliyor | 0 / 2 | 0% |
| **8** | Kraliçe & İşçi MRTA | 🟡 Bekliyor | 0 / 2 | 0% |
| **9** | Entegrasyon & Logger | 🟡 Bekliyor | 0 / 2 | 0% |
| **10**| Benchmark & Final | 🟡 Bekliyor | 0 / 2 | 0% |
| **TOPLAM** | **Colony-OS** | 🟡 **Devam Ediyor** | **11 / 25** | **44%** |
