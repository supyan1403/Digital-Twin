import pandas as pd
import numpy as np

print("Memulai pembuatan data lahan baru...")

# Set seed agar pola acaknya tetap konsisten
np.random.seed(99)

# Bikin 32 titik koordinat (Area sekitar Tasikmalaya)
longitudes = np.random.uniform(108.15, 108.25, 32)
latitudes = np.random.uniform(-7.35, -7.25, 32)

# POLA DATA EKSTREM (Agar beda drastis dengan file pertamamu)
# N: Lumayan, P: Sangat Rendah, K: Defisit Parah, pH: Sangat Asam
n_kadar = np.random.uniform(40, 70, 32)    
p_kadar = np.random.uniform(5, 15, 32)     # Fosfor merah/pudar
k_kadar = np.random.uniform(20, 50, 32)    # Kalium sangat merah/pudar
ph_tanah = np.random.uniform(4.5, 5.5, 32) # pH Asam (didominasi warna merah di peta)
kelembapan = np.random.uniform(40, 55, 32)

# Karena tanahnya asam dan kurang hara, kita set komoditas dominan Singkong
komoditas = np.random.choice(['SINGKONG', 'JAGUNG'], 32, p=[0.85, 0.15])

# Rangkai menjadi DataFrame persis seperti struktur aslimu
df_baru = pd.DataFrame({
    'Longitude': longitudes,
    'Latitude': latitudes,
    'N_mg_kg': n_kadar,
    'P_mg_kg': p_kadar,
    'K_mg_kg': k_kadar,
    'pH': ph_tanah,
    'Kelembapan_Persen': kelembapan,
    'Jenis_Komoditas': komoditas
})

# Export ke Excel
nama_file = 'Data_Lahan_Kritis_Tasik.xlsx'
df_baru.to_excel(nama_file, index=False)

print(f"✅ Sukses! File '{nama_file}' berhasil dibuat di folder ini.")