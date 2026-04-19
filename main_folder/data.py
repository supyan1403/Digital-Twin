import pandas as pd
import numpy as np


try:
    df_asli = pd.read_excel('Dataset.xlsx')
    print(f"✅ Berhasil membaca {len(df_asli)} titik data asli.")
except Exception as e:
    print(f"❌ Error: File Dataset.xlsx tidak ditemukan. Detail: {e}")
    exit()



faktor_kali = 6
df_augmented = pd.concat([df_asli] * faktor_kali, ignore_index=True)




kolom_numerik = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']


noise_level = 0.10 

for col in kolom_numerik:
    if col in df_augmented.columns:

        noise = np.random.normal(0, noise_level, size=len(df_augmented))
        

        df_augmented.loc[24:, col] = df_augmented.loc[24:, col] * (1 + noise[24:])
        

        df_augmented[col] = df_augmented[col].round(2)


nama_file_baru = 'Dataset_Augmented.xlsx'
df_augmented.to_excel(nama_file_baru, index=False)

print(f"🚀 Sukses! File '{nama_file_baru}' telah dibuat dengan total {len(df_augmented)} baris.")
print("Gunakan file ini sebagai sumber data baru di 'kalkulasi.py'.")