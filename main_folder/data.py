import pandas as pd
import numpy as np

# 1. Load Data Primer (24 Titik Asli)
try:
    df_asli = pd.read_excel('Dataset2.xlsx')
    print(f"✅ Berhasil membaca {len(df_asli)} titik data asli.")
except Exception as e:
    print(f"❌ Error: File Dataset2.xlsx tidak ditemukan. Detail: {e}")
    exit()

# 2. Tentukan Faktor Augmentasi
# 24 titik x 6 kali = 144 baris (Sangat ideal untuk target minimal 150)
faktor_kali = 6
df_augmented = pd.concat([df_asli] * faktor_kali, ignore_index=True)

# 3. Proses Stochastic Jittering (Penambahan Noise Terkontrol)
# Kita hanya memberikan variasi pada kolom angka (nutrisi & sensor)
# Koordinat (Lon/Lat) dan Nama Titik TIDAK diubah agar lokasi tetap akurat
kolom_numerik = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']

# Gunakan Standar Deviasi 0.08 (Artinya variasi maksimal sekitar 8%)
noise_level = 0.08 

for col in kolom_numerik:
    if col in df_augmented.columns:
        # Menghasilkan noise acak berdasarkan distribusi normal
        noise = np.random.normal(0, noise_level, size=len(df_augmented))
        
        # Terapkan noise hanya pada baris duplikat (biarkan 24 baris pertama tetap asli)
        df_augmented.loc[24:, col] = df_augmented.loc[24:, col] * (1 + noise[24:])
        
        # Pembulatan agar terlihat seperti hasil pembacaan alat (2 desimal)
        df_augmented[col] = df_augmented[col].round(2)

# 4. Simpan ke File Excel Baru
nama_file_baru = 'Dataset_150_Augmented.xlsx'
df_augmented.to_excel(nama_file_baru, index=False)

print(f"🚀 Sukses! File '{nama_file_baru}' telah dibuat dengan total {len(df_augmented)} baris.")
print("Gunakan file ini sebagai sumber data baru di 'kalkulasi.py'.")