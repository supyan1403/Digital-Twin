import matplotlib.pyplot as plt
import numpy as np

# 1. Menyiapkan Data (Berdasarkan Tabel 5 Simulasi 37 Titik)
komoditas = ['Caisim', 'Jagung', 'Singkong']
lahan_optimal = [27, 7, 27]    # Lahan yang tidak butuh biaya (Rp 0)
lahan_defisit = [10, 30, 10]   # Lahan yang butuh biaya intervensi

# Pengaturan posisi sumbu X
x = np.arange(len(komoditas))
width = 0.35  # Lebar setiap batang

# 2. Pengaturan Gaya Grafik
# Menggunakan gaya dasar yang bersih (clean)
plt.style.use('default') 
fig, ax = plt.subplots(figsize=(8, 5))

# 3. Membuat Batang (Bar) dengan Warna Netral Gelap dan Cerah
# Menggunakan Warna Gelap (Dark Slate) untuk Optimal
rects1 = ax.bar(x - width/2, lahan_optimal, width, 
                label='Lahan Optimal (Rp 0)', 
                color='#334155', edgecolor='#1E293B', linewidth=1.2)

# Menggunakan Warna Cerah (Light Silver) untuk Defisit
rects2 = ax.bar(x + width/2, lahan_defisit, width, 
                label='Lahan Defisit (Intervensi)', 
                color='#E2E8F0', edgecolor='#94A3B8', linewidth=1.2)

# 4. Kustomisasi Sumbu dan Label (Tanpa Judul)
ax.set_ylabel('Jumlah Titik Koordinat', fontsize=12, fontweight='bold', color='#333333')
ax.set_xticks(x)
ax.set_xticklabels(komoditas, fontsize=12, fontweight='bold', color='#333333')
ax.set_ylim(0, 36) # Ruang ekstra di atas nilai 30 agar angka tidak terpotong

# Mematikan garis pinggir atas dan kanan agar lebih estetik/minimalis
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#9ca3af')
ax.spines['bottom'].set_color('#9ca3af')

# 5. Menambahkan Legenda
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=2, fontsize=11, frameon=False)

# 6. Fungsi Menambahkan Teks Angka di Atas Batang
def autolabel(rects, text_color):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 4),  # Jarak 4 poin ke atas
                    textcoords="offset points",
                    ha='center', va='bottom', 
                    fontsize=11, fontweight='bold', color=text_color)

# Menambahkan label angka dengan warna gelap agar seragam dan kontras
autolabel(rects1, '#1E293B')
autolabel(rects2, '#1E293B')

# 7. Menyimpan dan Menampilkan Grafik
plt.tight_layout()

# Menyimpan dengan resolusi 300 DPI untuk kualitas jurnal SINTA/Scopus
nama_file = 'Gambar_6_BarChart_Ekonomi_Netral.png'
plt.savefig(nama_file, dpi=300, bbox_inches='tight', transparent=False, facecolor='white')

print(f"Grafik berhasil dibuat dan disimpan sebagai: {nama_file}")
plt.show()