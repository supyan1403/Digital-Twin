import pandas as pd
import numpy as np
from pykrige.ok import OrdinaryKriging
from sklearn.metrics import mean_squared_error, mean_absolute_error
import re
import warnings

warnings.filterwarnings('ignore')


def dms_to_dd(dms_str):
    if not isinstance(dms_str, str): return dms_str
    try:
        parts = re.findall(r"[-+]?\d*\.\d+|\d+", dms_str)
        d, m, s = map(float, parts[:3])
        dd = d + m/60 + s/3600
        return -dd if "S" in dms_str or d > 0 else dd
    except: return 0


df = pd.read_excel('Dataset_Augmented.xlsx')
df['lat_clean'] = df['Latitude'].apply(dms_to_dd)
df['lon_clean'] = df['Longitude'].apply(lambda x: abs(dms_to_dd(x)))


variabel_uji = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']
hasil_evaluasi = []

df = df.groupby(['lat_clean', 'lon_clean'])[variabel_uji].mean().reset_index()

print("⏳ Sedang menghitung validasi Kriging (LOOCV)...")

for var_name in variabel_uji:
    x, y, z = df['lon_clean'].values, df['lat_clean'].values, df[var_name].values
    z_asli, z_prediksi = [], []

    for i in range(len(z)):
        x_train, y_train, z_train = np.delete(x, i), np.delete(y, i), np.delete(z, i)
        x_test, y_test, z_true = x[i], y[i], z[i]
        
        try:
            ok = OrdinaryKriging(x_train, y_train, z_train, variogram_model='linear', verbose=False)
            z_hat, _ = ok.execute('points', [x_test], [y_test])
            z_asli.append(float(z_true))
            z_prediksi.append(float(z_hat[0]))
        except: continue
    
    if z_asli:
        rmse = np.sqrt(mean_squared_error(z_asli, z_prediksi))
        mae = mean_absolute_error(z_asli, z_prediksi)
        

        hasil_evaluasi.append({
            'Variabel Lingkungan': var_name, 
            'RMSE': rmse, 
            'MAE': mae
        })


df_hasil = pd.DataFrame(hasil_evaluasi)

print("\n" + "="*50)
print("🎯  HASIL EVALUASI MODEL KRIGING (LOOCV)  🎯")
print("="*50)

if not df_hasil.empty:

    df_hasil['RMSE'] = df_hasil['RMSE'].round(2)
    df_hasil['MAE'] = df_hasil['MAE'].round(2)
    

    print(df_hasil.to_string(index=False))
else:
    print("Data tidak ditemukan.")
print("="*50)