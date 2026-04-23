import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pykrige.ok import OrdinaryKriging
import re
import warnings
import os

warnings.filterwarnings('ignore')

def parse_coordinate(val):
    if pd.isna(val): return np.nan
    if isinstance(val, (int, float)): return float(val)
    
    clean_str = str(val).replace(',', '.')
    parts = re.findall(r"[-+]?\d*\.\d+|\d+", clean_str)
    try:
        if len(parts) >= 3:
            d, m, s = float(parts[0]), float(parts[1]), float(parts[2])
            return abs(d) + (m/60) + (s/3600)
        elif len(parts) > 0:
            return float(clean_str)
    except: return np.nan
    return np.nan

print("⏳ Menyiapkan data untuk pembuatan peta vertikal (3x2)...")
df = pd.read_excel('Dataset_Augmented.xlsx')

# Membersihkan koordinat
df['lat_clean'] = df['Latitude'].apply(parse_coordinate)
df['lon_clean'] = df['Longitude'].apply(parse_coordinate)
df['lat_clean'] = -abs(df['lat_clean'])
df['lon_clean'] = abs(df['lon_clean'])
df = df.dropna(subset=['lat_clean', 'lon_clean', 'pH'])

kolom_target = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']

terjemahan_indonesia = {
    'N_mg_kg': 'Nitrogen (mg/kg)',
    'P_mg_kg': 'Fosfor (mg/kg)',
    'K_mg_kg': 'Kalium (mg/kg)',
    'pH': 'pH Tanah',
    'Kelembapan_Persen': 'Kelembapan Tanah (%)',
    'Suhu_Udara': 'Suhu Udara (°C)'
}

df_unik = df.groupby(['lon_clean', 'lat_clean'])[kolom_target].mean().reset_index()

x = df_unik['lon_clean'].values
y = df_unik['lat_clean'].values

nama_folder = "Hasil_Peta_DigitalTwin"
if not os.path.exists(nama_folder):
    os.makedirs(nama_folder)

grid_lon = np.linspace(min(x) - 0.0002, max(x) + 0.0002, 100)
grid_lat = np.linspace(min(y) - 0.0002, max(y) + 0.0002, 100)

print("🎨 Menggambar Peta Gabungan Vertikal...")

# PERUBAHAN DI SINI: Layout menjadi 3 baris x 2 kolom agar pas di 1 kolom jurnal Word
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12, 18))
axes = axes.flatten()

for i, variabel in enumerate(kolom_target):
    ax = axes[i] 
    z = df_unik[variabel].values
    nama_tampilan = terjemahan_indonesia[variabel]
    
    try:
        # Penyesuaian agar gradasi pH muncul cantik
        if variabel == 'pH':
            ok = OrdinaryKriging(x, y, z, variogram_model='linear', verbose=False)
        else:
            ok = OrdinaryKriging(x, y, z, variogram_model='spherical', verbose=False)
            
        z_map, ss_map = ok.execute('grid', grid_lon, grid_lat)
        
        # Penyesuaian Warna: Kelembapan tetap Biru, sisanya Merah-Kuning-Hijau
        if variabel == 'Kelembapan_Persen':
            warna = 'Blues'
        else:
            warna = 'RdYlGn'
            
        batas_bawah = np.min(z_map)
        batas_atas = np.max(z_map)
        
        if batas_atas == batas_bawah:
             tingkat_gradasi = np.linspace(batas_bawah - 0.5, batas_atas + 0.5, 20)
        else:
             tingkat_gradasi = np.linspace(batas_bawah, batas_atas, 50)
        
        peta = ax.contourf(grid_lon, grid_lat, z_map, levels=tingkat_gradasi, cmap=warna, extend='both')
        
        ax.scatter(x, y, c='black', marker='x', s=40, linewidths=1.5, label='Titik Sampel')
        fig.colorbar(peta, ax=ax, label=f'Nilai', format='%.2f', fraction=0.046, pad=0.04)
        
        ax.set_title(f'{nama_tampilan}', fontsize=14, fontweight='bold')
        ax.set_xlabel('Longitude', fontsize=10)
        ax.set_ylabel('Latitude', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
        
    except Exception as e:
        print(f"   ❌ Gagal menggambar {variabel}: {e}")
        ax.set_title(f'{nama_tampilan} (Gagal)', fontsize=14, color='red')

plt.tight_layout()

# Menyimpan gambar dengan resolusi tinggi (300 dpi)
nama_file_gabungan = f"{nama_folder}/Gambar_3_Peta_Kriging_Vertikal.png"
plt.savefig(nama_file_gabungan, dpi=300)

print(f"✅ Gambar 3 berhasil disimpan di: {nama_file_gabungan}")