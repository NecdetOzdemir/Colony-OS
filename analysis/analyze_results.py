#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def analyze_logs():
    results_dir = os.path.join(os.path.expanduser('~'), 'Colony-OS', 'results')
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    
    if not csv_files:
        print("CSV dosyası bulunamadı. Lütfen önce simülasyonu ve logger'ı çalıştırın.")
        return

    plt.figure(figsize=(10, 6))

    for file in csv_files:
        df = pd.read_csv(file)
        algo = df['Algorithm'].iloc[0] if not df.empty else "Bilinmiyor"
        
        plt.plot(df['Timestamp'], df['AvgBattery'], label=f'{algo} - Ortalama Batarya')

    plt.title('Zamanla Ortalama Batarya Tüketimi (FCFS vs AUCTION)')
    plt.xlabel('Zaman (saniye)')
    plt.ylabel('Ortalama Batarya Seviyesi (%)')
    plt.legend()
    plt.grid(True)
    
    save_path = os.path.join(results_dir, 'battery_analysis.png')
    plt.savefig(save_path)
    print(f"Analiz grafiği kaydedildi: {save_path}")

if __name__ == '__main__':
    analyze_logs()
