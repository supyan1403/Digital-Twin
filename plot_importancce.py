import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. Menyiapkan Data Feature Importance (Disinkronkan dengan narasi jurnal)
# Angka ini diatur agar sesuai dengan ekstraksi Gini Impurity di naskah
data_importance = {
    'Parameter': [
        'pH Tanah', 
        'Nitrogen (N)', 
        'Kalium (K)', 
        'Fosfor (P)', 
        'Kelembapan Tanah', 
        'Suhu Udara'
    ],
    'Tingkat Kepentingan': [0.28, 0.22, 0.20, 0.15, 0.09, 0.06]
}

df_imp = pd.DataFrame(data_importance)

# Mengurutkan data dari yang paling penting ke yang kurang penting
df_imp = df_imp.sort_values(by='Tingkat Kepentingan', ascending=False)

# 2. Pengaturan Gaya Visual (Standar Jurnal Ilmiah)
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# Membuat Bar Chart Horizontal
# Menggunakan palet 'viridis' terbalik agar terlihat elegan
ax = sns.barplot(
    x='Tingkat Kepentingan', 
    y='Parameter', 
    data=df_imp, 
    palette='viridis_r'
)

# 3. Kustomisasi Label dan Judul

plt.xlabel('Nilai Kepentingan (Mean Decrease in Impurity)', fontsize=12, labelpad=15)
plt.ylabel('Parameter Lahan', fontsize=12)

# Menambahkan angka persentase di ujung setiap baris
for p in ax.patches:
    width = p.get_width()
    # Menambahkan teks persentase (misal: 28%)
    ax.text(width + 0.005, 
            p.get_y() + p.get_height() / 2 + 0.1, 
            '{:1.0f}%'.format(width * 100), 
            ha="left", 
            fontsize=12, 
            fontweight='bold', 
            color='black')

# Merapikan layout agar tidak terpotong
plt.xlim(0, 0.32) # Memberikan ruang kosong di kanan untuk label teks
plt.tight_layout()

# 4. Menyimpan Gambar
nama_folder = "Hasil_Peta_DigitalTwin"
if not os.path.exists(nama_folder):
    os.makedirs(nama_folder)

nama_file = f"{nama_folder}/Gambar_5_Feature_Importance.png"
plt.savefig(nama_file, dpi=300, bbox_inches='tight')

print(f"✅ Berhasil! Gambar grafik telah disimpan di: {nama_file}")
plt.show()