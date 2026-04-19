import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pandas as pd


df_train = pd.read_excel('Dataset_Augmented.xlsx') 
kolom_fitur = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']

X_train = df_train[kolom_fitur]
y_train = df_train['Jenis_Komoditas']


rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)



df_baru = pd.read_excel('Data_Lahan_Latih.xlsx') 


df_baru = df_baru.rename(columns={
    'N (mg/kg)': 'N_mg_kg', 'P (mg/kg)': 'P_mg_kg', 'K (mg/kg)': 'K_mg_kg',
    'pH Tanah': 'pH', 'Kelembapan (%)': 'Kelembapan_Persen', 'Suhu (°C)': 'Suhu_Udara'
})


X_test_baru = df_baru[kolom_fitur]
df_baru['Rekomendasi_AI'] = rf_model.predict(X_test_baru)



df_tampil = df_baru[['Nama_Titik', 'N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH','Kelembapan_Persen', 'Suhu_Udara', 'Rekomendasi_AI']].set_index('Nama_Titik')

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\n" + "="*90)
print("                 🎯 HASIL REKOMENDASI KOMODITAS (SEMUA TITIK) 🎯")
print("="*90)

print(df_tampil.to_string()) 


df_baru.to_excel('Hasil_Rekomendasi.xlsx', index=False)
print(f"\n✅ File lengkap disimpan: 'Hasil_Rekomendasi.xlsx'")