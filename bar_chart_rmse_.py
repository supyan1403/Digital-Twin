import matplotlib.pyplot as plt
import numpy as np

# 1. Menyiapkan Data (Berdasarkan Tabel 3: Evaluasi Kesalahan Spasial)
parameter = ['Nitrogen (N)', 'Fosfor (P)', 'Kalium (K)', 'pH Tanah', 'Kelembapan', 'Suhu Udara']
rmse = [12.37, 5.16, 9.18, 0.61, 2.54, 0.96]
mae = [10.46, 4.33, 7.79, 0.48, 2.22, 0.80]

# Pengaturan posisi sumbu X
x = np.arange(len(parameter))
width = 0.35  # Lebar setiap batang

# 2. Pengaturan Gaya Grafik
plt.style.use('default') 
fig, ax = plt.subplots(figsize=(10, 5)) # Ukuran sedikit lebih lebar agar teks sumbu X tidak berdempetan

# 3. Membuat Batang (Bar) dengan Warna Netral Jurnal
# Warna Gelap (Dark Slate) untuk RMSE
rects1 = ax.bar(x - width/2, rmse, width, 
                label='RMSE (Root Mean Square Error)', 
                color='#334155', edgecolor='#1E293B', linewidth=1.2)

# Warna Terang (Light Slate) untuk MAE
rects2 = ax.bar(x + width/2, mae, width, 
                label='MAE (Mean Absolute Error)', 
                color='#94A3B8', edgecolor='#64748B', linewidth=1.2)

# 4. Kustomisasi Sumbu dan Label
ax.set_ylabel('Tingkat Kesalahan (Error Rate)', fontsize=12, fontweight='bold', color='#333333')
ax.set_xticks(x)
ax.set_xticklabels(parameter, fontsize=11, fontweight='bold', color='#333333')
ax.set_ylim(0, 15) # Memberikan ruang di atas batang tertinggi (12.37) untuk angka

# Mematikan garis pinggir atas dan kanan agar minimalis
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#9ca3af')
ax.spines['bottom'].set_color('#9ca3af')

# 5. Menambahkan Legenda (Di bagian atas tengah)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12),
          ncol=2, fontsize=11, frameon=False)

# 6. Fungsi Menambahkan Teks Angka di Atas Batang
def autolabel(rects, text_color):
    for rect in rects:
        height = rect.get_height()
        # Format angka 2 desimal agar seragam dengan tabel
        ax.annotate(f'{height:.2f}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4),  # Jarak 4 poin ke atas
                    textcoords="offset points",
                    ha='center', va='bottom', 
                    fontsize=10, fontweight='bold', color=text_color)

# Memanggil fungsi pelabelan dengan warna kontras
autolabel(rects1, '#1E293B') # Angka gelap untuk bar gelap
autolabel(rects2, '#475569') # Angka sedikit lebih abu-abu untuk bar terang

# 7. Menyimpan dan Menampilkan Grafik
plt.tight_layout()

# Menyimpan dengan resolusi 300 DPI untuk kualitas jurnal
nama_file = 'Gambar_Evaluasi_RMSE_MAE.png'
plt.savefig(nama_file, dpi=300, bbox_inches='tight', transparent=False, facecolor='white')

print(f"✅ Grafik berhasil dibuat dan disimpan sebagai: {nama_file}")
plt.show()