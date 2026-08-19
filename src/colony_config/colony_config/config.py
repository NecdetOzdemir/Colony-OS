"""
Colony-OS — Merkezi Konfigürasyon Kütüphanesi
==============================================
Tüm paketler parametrelerini buradan çeker.
Bir şeyi değiştirmek istediğinde SADECE bu dosyaya bak.

Kullanım:
    from colony_config import ColonyConfig as CC
    n = CC.NUM_WORKERS
    CC.validate()
"""

from __future__ import annotations
import os
from pathlib import Path


# ─────────────────────────────────────────────
#  PROJE KÖK DİZİNİ
# ─────────────────────────────────────────────
_THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = _THIS_FILE.parents[3]          # Colony-OS/
RESULTS_DIR  = PROJECT_ROOT / "results"
ANALYSIS_DIR = PROJECT_ROOT / "analysis"


class ColonyConfig:
    """
    Tüm Colony-OS parametrelerini tek yerden yönet.
    Değerleri değiştirmek için bu sınıfın niteliklerini düzenle.
    Asla başka paketin içine sabit değer (magic number) yazma.
    """

    # ─────────────────────────────────────────
    #  SİMÜLASYON PLATFORMU
    # ─────────────────────────────────────────
    SIMULATOR: str = "gazebo"               # "gazebo" | "isaac_sim"
    GAZEBO_VERSION: str = "fortress"        # Ignition Gazebo Fortress 6.17.1
    ROS_DISTRO: str = "humble"

    # ─────────────────────────────────────────
    #  ROBOT FILOSU
    # ─────────────────────────────────────────
    NUM_WORKERS: int = 1                    # Kaç tane İşçi robot
    WORKER_NAMESPACE: str = "worker"        # worker_1, worker_2, ...
    WORKER_MAX_SPEED: float = 0.5           # m/s — mobil taban max hız
    WORKER_MAX_ANGULAR_SPEED: float = 1.0   # rad/s

    # ─────────────────────────────────────────
    #  GÖREV & SENARYO
    # ─────────────────────────────────────────
    TOTAL_TASKS: int = 50                   # Benchmark senaryosundaki toplam görev sayısı
    TASK_TYPES: list = ["PICK", "PLACE"]    # Görev tipleri
    OBJECT_TYPES: list = ["A", "B", "C"]   # Nesne tipleri (A/B/C)
    SCENARIO_DURATION_SEC: int = 600        # 10 dakika = 600 saniye

    # ─────────────────────────────────────────
    #  GÖREV ATAMA ALGORİTMASI
    # ─────────────────────────────────────────
    ALGORITHM: str = "AUCTION"              # "AUCTION" | "FCFS"
    AUCTION_TIMEOUT_SEC: float = 2.0        # Teklifleri bekleme süresi (saniye)
    AUCTION_MIN_BIDS: int = 1               # En az kaç teklif gelmeli
    BID_COST_METRIC: str = "distance"       # "distance" | "time" | "weighted"

    # ─────────────────────────────────────────
    #  NAVİGASYON (Nav2)
    # ─────────────────────────────────────────
    GOAL_TOLERANCE_XY: float = 0.15         # metre — hedefe ulaşma toleransı
    GOAL_TOLERANCE_YAW: float = 0.1         # radyan
    PLANNER: str = "NavfnPlanner"           # "NavfnPlanner" | "SmacPlanner"
    CONTROLLER: str = "DWBLocalPlanner"

    # ─────────────────────────────────────────
    #  DÜNYA / SAHNE
    # ─────────────────────────────────────────
    WORLD_FILE: str = "warehouse.sdf"
    WAREHOUSE_WIDTH: float = 20.0           # metre
    WAREHOUSE_HEIGHT: float = 15.0          # metre
    NUM_SHELVES: int = 6
    NUM_PICK_STATIONS: int = 3              # A, B, C
    NUM_PLACE_STATIONS: int = 2

    # ─────────────────────────────────────────
    #  LOGLAMA & ÇIKTI
    # ─────────────────────────────────────────
    LOG_DIR: Path = RESULTS_DIR
    LOG_FILENAME_PREFIX: str = "colony_benchmark"
    LOG_CSV_COLUMNS: list = [
        "run_id", "algorithm", "task_id", "object_type",
        "worker_id", "start_time", "end_time",
        "duration_sec", "travel_distance_m", "num_bids_received"
    ]
    STATS_PUBLISH_RATE_HZ: float = 1.0      # İstatistik yayınlama sıklığı

    # ─────────────────────────────────────────
    #  ROS 2 TOPIC / SERVİS İSİMLERİ
    # ─────────────────────────────────────────
    TOPIC_TASK_BROADCAST: str = "/colony/task_broadcast"
    TOPIC_BID: str = "/colony/bid"
    TOPIC_WORKER_STATUS: str = "/colony/worker_status"
    TOPIC_STATS: str = "/colony/stats"
    SERVICE_ASSIGN_TASK: str = "/colony/assign_task"
    ACTION_EXECUTE_TASK: str = "/colony/execute_task"

    # ─────────────────────────────────────────
    #  YARDIMCI METODLAR
    # ─────────────────────────────────────────

    @classmethod
    def validate(cls) -> None:
        """Konfigürasyon değerlerinin tutarlı olup olmadığını kontrol et."""
        assert cls.NUM_WORKERS >= 1, "En az 1 işçi robot olmalı"
        assert cls.TOTAL_TASKS >= 1, "En az 1 görev olmalı"
        assert cls.ALGORITHM in ("AUCTION", "FCFS"), \
            f"Geçersiz algoritma: {cls.ALGORITHM}. 'AUCTION' veya 'FCFS' olmalı."
        assert cls.AUCTION_TIMEOUT_SEC > 0, "Auction timeout pozitif olmalı"
        assert cls.SIMULATOR in ("gazebo", "isaac_sim"), \
            f"Geçersiz simülatör: {cls.SIMULATOR}"
        assert cls.LOG_DIR.exists() or True, "LOG_DIR oluşturulacak"
        print(f"[ColonyConfig] ✅ Konfigürasyon geçerli.")
        print(f"  Simülatör  : {cls.SIMULATOR} ({cls.GAZEBO_VERSION})")
        print(f"  Algoritma  : {cls.ALGORITHM}")
        print(f"  İşçi sayısı: {cls.NUM_WORKERS}")
        print(f"  Görev sayısı: {cls.TOTAL_TASKS}")

    @classmethod
    def worker_namespace(cls, worker_id: int) -> str:
        """worker_1, worker_2, ... formatında namespace döndür."""
        return f"{cls.WORKER_NAMESPACE}_{worker_id}"

    @classmethod
    def log_filepath(cls, algorithm: str | None = None) -> Path:
        """Çalışmaya özgü CSV dosya yolunu döndür."""
        import datetime
        algo = algorithm or cls.ALGORITHM
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        return cls.LOG_DIR / f"{cls.LOG_FILENAME_PREFIX}_{algo}_{ts}.csv"

    @classmethod
    def summary(cls) -> dict:
        """Tüm ayarları dict olarak döndür (loglama için)."""
        return {k: v for k, v in cls.__dict__.items()
                if not k.startswith("_") and not callable(v)}


# Modül seviyesinde alias — kısa kullanım için
CC = ColonyConfig
