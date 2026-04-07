import pandas as pd
import numpy as np

# set koordinat awal (sesuai dari gmaps)
lat_awal = -7.342036909858733
lon_awal = 108.04289249956308
step = 0.000045 # jarak grid ~5m

np.random.seed(42)
data_asli = []
sample_id = 1

for baris in range(4):     
    for kolom in range(8): 
        # hitung titik lat lon
        lat_titik = lat_awal + (baris * step)
        lon_titik = lon_awal + (kolom * step)
        
        # bikin tren spasial biar petanya ada gradasi pas di-kriging
        # K tinggi di awal, makin ke timur makin turun
        k_val = 145 - (kolom * 8) - (baris * 5) + np.random.normal(0, 3)
        n_val = 20 + (kolom * 6) + (baris * 2) + np.random.normal(0, 2)
        p_val = 12 + (kolom * 2) + np.random.normal(0, 2)
        ph_val = 5.5 + (kolom * 0.15) + np.random.normal(0, 0.1)
        moisture = 60 + (baris * 2) + np.random.normal(0, 2)
        
        # cegah nilai minus
        k_val = max(10, round(k_val))
        n_val = max(10, round(n_val))
        p_val = max(10, round(p_val))
        ph_val = round(ph_val, 1)
        moisture = max(20, round(moisture))
        
        # append ke list
        data_asli.append([
            f"T_{sample_id:02d}", lat_titik, lon_titik, 
            n_val, p_val, k_val, ph_val, moisture
        ])
        sample_id += 1

# masukin ke df terus export excel
kolom_asli = ['ID_Sampel', 'Latitude', 'Longitude', 'N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen']
df_asli = pd.DataFrame(data_asli, columns=kolom_asli)
df_asli.to_excel('Dataset_Kriging_LokasiAsli.xlsx', index=False)

print("Berhasil bikin Dataset_Kriging_LokasiAsli.xlsx")