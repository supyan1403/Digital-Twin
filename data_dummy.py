import pandas as pd
import numpy as np
import math

# ==========================================
# 1. PENGATURAN LOKASI AWAL (Lembang)
# ==========================================
lat_awal = -6.812345
lon_awal = 107.654321

# Konstanta Bumi di Lintang -6.8
DEG_PER_METER_LAT = 0.000008983
DEG_PER_METER_LON = 0.000009044

# ==========================================
# 2. PENGATURAN UKURAN & KEMIRINGAN
# ==========================================
panjang_m = 50.0  
lebar_m = 40.0    
rows = 5
cols = 5
step_panjang = panjang_m / (rows - 1)
step_lebar = lebar_m / (cols - 1)

# --- ATUR KEMIRINGAN DI SINI ---
# 0 = Lurus (Selatan-Timur). Semakin besar angkanya, semakin miring putarannya.
sudut_kemiringan = -45 
theta = math.radians(sudut_kemiringan)

# Hitung Vektor Arah menggunakan Trigonometri agar tetap Siku-siku (90 derajat)
# Arah Panjang (Bergerak ke Selatan dan sedikit serong Timur)
dy_panjang = -math.cos(theta) * step_panjang  
dx_panjang = math.sin(theta) * step_panjang   

# Arah Lebar (Bergerak ke Timur dan sedikit serong Utara)
dy_lebar = math.sin(theta) * step_lebar       
dx_lebar = math.cos(theta) * step_lebar       

# ==========================================
# 3. GENERATE DATA
# ==========================================
data = []
titik_id = 1
np.random.seed(99)

for r in range(rows):
    for c in range(cols):
        # Hitung posisi meter dengan memperhitungkan kemiringan
        m_lat = (r * dy_panjang) + (c * dy_lebar)
        m_lon = (r * dx_panjang) + (c * dx_lebar)
        
        # Konversi jarak meter ke derajat koordinat
        lat_baru = lat_awal + (m_lat * DEG_PER_METER_LAT)
        lon_baru = lon_awal + (m_lon * DEG_PER_METER_LON)
        
        data.append({
            'Nama_Titik': f'T{titik_id}',
            'Latitude': lat_baru,
            'Longitude': lon_baru,
            'N_mg_kg': round(np.random.uniform(20.0, 50.0), 2),
            'P_mg_kg': round(np.random.uniform(15.0, 40.0), 2),
            'K_mg_kg': round(np.random.uniform(150.0, 300.0), 2),
            'pH': round(np.random.uniform(5.5, 6.8), 1),
            'Kelembapan_Persen': round(np.random.uniform(60, 90), 1),
            'Suhu_Udara': round(np.random.uniform(20, 26), 1)
        })
        titik_id += 1

# ==========================================
# 4. SIMPAN FILE EXCEL
# ==========================================
df = pd.DataFrame(data)
nama_file = 'Dataset_Lembang_Miring.xlsx'
df.to_excel(nama_file, index=False)

print(f"✅ File '{nama_file}' berhasil dibuat!")
print(f"Ukuran Lahan: 50x40 meter | Sudut Kemiringan: {sudut_kemiringan} derajat")