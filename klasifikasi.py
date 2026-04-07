import pandas as pd
import numpy as np

# 1. Inisialisasi 32 Titik (T1 - T32)
n_samples = 32
titik = [f"T{i+1}" for i in range(n_samples)]

# 2. Generasi Koordinat GRID 4x8 (40m x 20m)
lats = np.linspace(-7.341900, -7.342080, 4) 
lons = np.linspace(108.042900, 108.043260, 8) 
lon_grid, lat_grid = np.meshgrid(lons, lats)
lat_flat = lat_grid.flatten()
lon_flat = lon_grid.flatten()

def klasifikasi_hara(n, p, k):
    st_n = "Sedang" if n >= 40 else "Rendah"
    st_p = "Tinggi" if p > 40 else "Sedang" if p >= 21 else "Rendah"
    st_k = "Tinggi" if k > 40 else "Sedang" if k >= 21 else "Rendah"
    return st_n, st_p, st_k

data = []
for i in range(n_samples):
    # Iklim mikro (Udara) Cigalontang (18-27°C) diambil tengahnya
    sh = np.random.uniform(22, 24) 
    lmb = np.random.uniform(70, 80)
    
    # PENYESUAIAN RANGE HARA (Dibuat beririsan/Overlap agar AI lebih fleksibel)
    if i < 11: 
        kom = "Caisim"
        n, p, k, ph = np.random.uniform(70, 95), np.random.uniform(35, 55), np.random.uniform(75, 100), np.random.uniform(6.0, 7.0)
    elif i < 22:
        kom = "Jagung"
        n, p, k, ph = np.random.uniform(45, 75), np.random.uniform(30, 50), np.random.uniform(55, 85), np.random.uniform(5.8, 7.5)
    else:
        kom = "Singkong"
        # Singkong sekarang bisa punya N sampai 55 (beririsan dengan Jagung)
        n, p, k, ph = np.random.uniform(30, 55), np.random.uniform(25, 45), np.random.uniform(40, 70), np.random.uniform(5.2, 7.0)

    st_n, st_p, st_k = klasifikasi_hara(n, p, k)
    
    data.append([
        titik[i], round(lat_flat[i], 6), round(lon_flat[i], 6),
        round(n, 2), st_n, round(p, 2), st_p, round(k, 2), st_k,
        round(ph, 1), round(lmb, 1), round(sh, 1), kom
    ])

columns = ['Nama_Titik', 'Latitude', 'Longitude', 'N_mg_kg', 'Status_N', 
           'P_mg_kg', 'Status_P', 'K_mg_kg', 'Status_K', 'pH', 
           'Kelembapan_Persen', 'Suhu_Udara', 'Jenis_Komoditas']

df = pd.DataFrame(data, columns=columns)
df.to_excel('Dataset_Kriging_Terklasifikasi.xlsx', index=False)
print("✅ Dataset Versi Dinamis (Irisan Hara) Berhasil Dibuat!")