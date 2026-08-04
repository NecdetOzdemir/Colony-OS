# Colony-OS — Ajan Kuralları (AGENTS.md)

Bu dosya, Colony-OS projesinde çalışan AI ajanın uyması gereken kuralları tanımlar.
Her yeni sohbet veya görev başlangıcında bu kurallar otomatik olarak yüklenir.

---

## 🔁 TODO LİSTESİ GÜNCELLEME KURALLARI

> 📋 TODO listesi her zaman proje kökünde: `Colony-OS/task.md`

**Her görevin başında:**
1. `task.md` dosyasını oku (`/home/necdet/Colony-OS/task.md`) — hangi aşamada olduğunu anla
2. Başladığın görevi `[ ]` → `[/]` (devam ediyor) olarak işaretle
3. Görevin hangi paketi ve dosyayı etkilediğini belirle

**Her görevin sonunda:**
1. Tamamlanan alt görevleri `[/]` → `[x]` olarak işaretle
2. `task.md` son bölümündeki **İlerleme Özeti** tablosunu güncelle (tamamlanan/toplam/yüzde)
3. Yeni keşfedilen gereksinimler varsa TODO listesine ekle
4. Tarih satırını güncelle: `> Son güncelleme: YYYY-MM-DD`

**Asla:**
- Tamamlanmamış görevleri `[x]` olarak işaretleme
- TODO listesini güncellemeden bir sonraki göreve geçme

---

## ⚙️ KONFİGÜRASYON KURALLARI

**Altın Kural: Hiçbir pakete magic number veya hardcoded parametre yazma.**

Her parametre için şu hiyerarşiyi takip et:

```
colony_config/config.py  (ColonyConfig sınıfı)
        ↓
Tüm diğer paketler buradan import eder:
    from colony_config import CC
    num_workers = CC.NUM_WORKERS
```

**Kontrol Listesi — yeni bir değer eklerken:**
- [ ] Değer `colony_config/config.py`'da `ColonyConfig` sınıfına eklendi mi?
- [ ] Açıklayıcı bir yorum satırı yazıldı mı?
- [ ] Varsayılan değer makul mü?
- [ ] `validate()` metoduna kontrol eklendi mi? (kritik değerler için)

**Hangi değerler config'e gitmeli:**
- Robot sayıları, hız limitleri, toleranslar
- Algoritma seçimleri (AUCTION / FCFS)
- Topic/service isimleri
- Dosya yolları
- Senaryo parametreleri (görev sayısı, süre vs.)
- Dünya/sahne boyutları

---

## 📦 PAKET OLUŞTURMA KURALLARI

Her yeni ROS 2 paketi için şu dosyalar ZORUNLU:
- `package.xml` — paket tanımı
- `setup.py` — Python paketi kurulumu
- `resource/<paket_adı>` — ament index kaydı
- `<paket_adı>/__init__.py` — Python modül init
- `<paket_adı>/config.py`'dan **bağımlılık ekle**:
  ```xml
  <!-- package.xml'e ekle -->
  <depend>colony_config</depend>
  ```

---

## 🧪 TEST KURALLARI

- Her yeni Python modülü için `test/test_<modül>.py` yaz
- `colcon test` geçmedikçe aşamayı tamamlanmış sayma
- Mock/stub kullanarak simülatörden bağımsız test et (özellikle colony_queen için)

---

## 📝 KOD YAZMA KURALLARI

1. **Dil:** Python 3.10+ (type hints kullan)
2. **Dokümantasyon:** Her class ve public method için docstring
3. **Import sırası:**
   ```python
   # 1. Standart kütüphane
   import os, time
   # 2. Üçüncü taraf
   import rclpy
   # 3. Colony-OS (config her zaman ilk)
   from colony_config import CC
   from colony_interfaces.msg import Task
   ```
4. **Loglama:** `self.get_logger()` kullan, `print()` değil
5. **Hata yönetimi:** Kritik hataları `rclpy` exception handling ile yakala

---

## 🏗️ WORKSPACE YAPISI

```
Colony-OS/
├── src/
│   ├── colony_config/       ← MERKEZİ KONFİGÜRASYON (her zaman önce build et)
│   ├── colony_interfaces/   ← Mesaj/Servis/Action tanımları
│   ├── colony_description/  ← URDF/SDF modeller
│   ├── colony_queen/        ← MRTA algoritmaları
│   ├── colony_worker/       ← İşçi düğümleri
│   ├── colony_navigation/   ← Nav2 konfigürasyonu
│   ├── colony_manipulation/ ← MoveIt 2 konfigürasyonu
│   ├── colony_logger/       ← Performans kaydedici
│   └── colony_bringup/      ← Launch dosyaları
├── results/                 ← CSV çıktıları
├── analysis/                ← Analiz scriptleri
└── .agents/AGENTS.md        ← Bu dosya
```

**Build sırası önemli:**
```bash
# Her zaman colony_config ve colony_interfaces önce build edilmeli
colcon build --packages-select colony_config colony_interfaces
colcon build  # Geri kalanlar
```

---

## 🚦 AŞAMA GEÇİŞ KONTROL LİSTESİ

Bir aşamadan diğerine geçmeden önce:
- [ ] Aşamanın tüm görevleri `[x]` olarak işaretlendi
- [ ] `colcon build` hatasız tamamlandı
- [ ] `colcon test` geçti
- [ ] İlgili aşamanın kısa özeti task.md'ye eklendi

---

## 📊 BENCHMARK TEST KURALLARI

Test yaparken:
1. `colony_config`'de `ALGORITHM = "FCFS"` yap → testi çalıştır → CSV kaydet
2. `colony_config`'de `ALGORITHM = "AUCTION"` yap → testi çalıştır → CSV kaydet
3. `analysis/analyze_results.py` ile karşılaştır
4. Sonuçları `results/` klasörüne kaydet

**Asla** iki algoritmayı aynı anda aynı simülasyonda test etme.

---

## 🔧 HATA AYIKLAMA KURALLARI

1. Gazebo başlamıyorsa: `ign gazebo --version` ile sürüm kontrol et
2. ROS 2 topic görünmüyorsa: `source /opt/ros/humble/setup.bash` unutulmuş olabilir
3. Import hatası: `colony_config` paketi build edilip install edildi mi?
4. Nav2 çalışmıyorsa: `nav2-bringup` paketi kurulu mu? (`dpkg -l | grep nav2`)
