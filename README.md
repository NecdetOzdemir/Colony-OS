# 🐝 Colony-OS

> **Bitirme Projesi** — Çoklu Robot Yönetim Sistemi (MRTA)
> Hiyerarşik "Kraliçe-İşçi" mimarisine dayanan otonom depo otomasyonu.

---

## 📋 TODO & İLERLEME

> Projenin güncel durumunu görmek için:

### 👉 **[task.md — Görev Listesi & İlerleme](./task.md)**

```
4 / 58 görev tamamlandı  (%7)
████░░░░░░░░░░░░░░░░░░░░  Devam Ediyor
```

---

## ⚡ Hızlı Başlangıç

```bash
# 1. ROS 2 ortamını yükle
source /opt/ros/humble/setup.bash

# 2. Önce colony_config derle (diğer paketler buna bağlı)
colcon build --packages-select colony_config colony_interfaces

# 3. Tüm paketi derle
colcon build

# 4. Ortamı aktifleştir
source install/setup.bash

# 5. Simülasyonu başlat
ros2 launch colony_bringup simulation.launch.py

# 6. Benchmark testi (FCFS vs Auction)
ros2 launch colony_bringup benchmark.launch.py
```

---

## 🗂️ Proje Yapısı

```
Colony-OS/
├── 📋 task.md               ← BURAYA BAK — görev listesi & ilerleme
├── src/
│   ├── colony_config/       ← ⚙️  Merkezi konfigürasyon (önce build)
│   ├── colony_interfaces/   ← 📨  Mesaj/Servis/Action tanımları
│   ├── colony_description/  ← 🌍  Robot ve dünya modelleri (URDF/SDF)
│   ├── colony_queen/        ← 👑  Kraliçe MRTA algoritması (ANA KATKI)
│   ├── colony_worker/       ← 🤖  İşçi robot düğümleri
│   ├── colony_navigation/   ← 🧭  Nav2 konfigürasyonu
│   ├── colony_manipulation/ ← 🦾  MoveIt 2 konfigürasyonu
│   ├── colony_logger/       ← 📊  Performans kaydedici
│   └── colony_bringup/      ← 🚀  Launch dosyaları
├── results/                 ← 📁  Benchmark CSV çıktıları
└── analysis/                ← 📈  Python analiz scriptleri
```

---

## ⚙️ Konfigürasyon

**Tüm parametreler tek dosyadan yönetilir:**
👉 [`src/colony_config/colony_config/config.py`](./src/colony_config/colony_config/config.py)

```python
from colony_config import CC

CC.ALGORITHM       # "AUCTION" veya "FCFS"
CC.NUM_WORKERS     # Kaç robot? (default: 5)
CC.TOTAL_TASKS     # Kaç görev? (default: 50)
CC.AUCTION_TIMEOUT_SEC  # Teklif bekleme süresi
```

> ⚠️ **Kural:** Hiçbir pakete sabit sayı yazma. Her şey `CC.*`'dan gelir.

---

## 🔬 Sistem Ortamı

| Bileşen | Sürüm |
|---------|-------|
| Simülatör | Ignition Gazebo Fortress **6.17.1** |
| ROS | ROS 2 **Humble** Hawksbill |
| Navigasyon | Nav2 |
| Manipülasyon | MoveIt 2 **2.5.9** |
| Python | 3.10.12 |

---

## 📐 Mimari

```
                  ┌─────────────────┐
                  │  👑 KRALIÇE     │
                  │  (Queen Node)   │
                  │                 │
                  │  AUCTION / FCFS │
                  └────────┬────────┘
                           │ Görev Ata
              ┌────────────┼────────────┐
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │ 🤖 İşçi1 │ │ 🤖 İşçi2 │ │ 🤖 İşçi3 │
       │          │ │          │ │          │
       │ Nav2     │ │ Nav2     │ │ Nav2     │
       │ MoveIt2  │ │ MoveIt2  │ │ MoveIt2  │
       └────┬─────┘ └────┬─────┘ └────┬─────┘
            │             │             │
            └─────────────┴─────────────┘
                          │
                 ┌────────▼────────┐
                 │  🌍 Ignition    │
                 │     Gazebo      │
                 │  (Depo Dünyası) │
                 └─────────────────┘
```

---

## 📚 Referanslar

- [ROS 2 Humble Docs](https://docs.ros.org/en/humble/)
- [Nav2 Docs](https://navigation.ros.org/)
- [MoveIt 2 Docs](https://moveit.picknik.ai/)
- [Ignition Gazebo Fortress](https://gazebosim.org/docs/fortress)

---

*Bilgisayar Mühendisliği Bitirme Projesi — Colony-OS*
