import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 1. Menyiapkan Data Proyeksi Komparasi Ekonomi (Skala 0-100)
# Nilai-nilai ini diestimasi berdasarkan narasi di Bab 3.4
kategori = [
    'Akurasi Pemilihan\nKomoditas', 
    'Efisiensi Biaya/\nPenghematan Pupuk', 
    'Penghematan Modal\nAwal (CAPEX)', 
    'Potensi Keberhasilan\nPanen'
]

# Data skor untuk kedua metode
konvensional = [55, 10, 15, 65]  # Nilai rendah karena spekulatif dan boros
digital_twin = [90, 85, 95, 92]  # Nilai tinggi karena presisi dan low-cost

x = np.arange(len(kategori))  # Lokasi label x
width = 0.35  # Lebar batang bar

# 2. Pengaturan Visual & Plotting
plt.figure(figsize=(11, 6))
plt.style.use('seaborn-v0_8-whitegrid') # Style grid yang bersih

# Membuat Bar Chart untuk Konvensional (Warna Merah Bata/Coral)
rects1 = plt.bar(x - width/2, konvensional, width, 
                 label='Konvensional (Tanpa Model)', 
                 color='#ef6c00', alpha=0.85, edgecolor='black', linewidth=1)

# Membuat Bar Chart untuk Digital Twin (Warna Hijau Tua/Forest)
rects2 = plt.bar(x + width/2, digital_twin, width, 
                 label='Digital Twin Hibrida (Usulan)', 
                 color='#2e7d32', alpha=0.9, edgecolor='black', linewidth=1)

# 3. Kustomisasi Label, Judul, dan Teks
plt.ylabel('Skala Optimalisasi & Efisiensi (%)', fontsize=12, fontweight='bold')
plt.title('Komparasi Indikator Keberlanjutan Ekonomi Lahan', fontsize=16, fontweight='black', pad=20)
plt.xticks(x, kategori, fontsize=11, fontweight='bold')
plt.ylim(0, 110) # Mengatur batas sumbu Y agar teks persentase tidak terpotong

plt.legend(loc='upper left', fontsize=11, frameon=True, shadow=True)

# Fungsi untuk menambahkan angka persentase di atas setiap batang
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.annotate(f'{height}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 5),  # 5 points offset vertikal
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

autolabel(rects1)
autolabel(rects2)

# 4. Menyimpan dan Menampilkan Gambar
plt.tight_layout()

# Membuat folder jika belum ada
nama_folder = "Hasil_Peta_DigitalTwin"
if not os.path.exists(nama_folder):
    os.makedirs(nama_folder)

# Simpan gambar dengan resolusi jurnal (300 dpi)
nama_file = f"{nama_folder}/Gambar_7_Optimalisasi_Ekonomi.png"
plt.savefig(nama_file, dpi=300, bbox_inches='tight')

print(f"✅ Berhasil! Gambar grafik komparasi ekonomi telah disimpan di: {nama_file}")
plt.show()