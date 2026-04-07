import pandas as pd
import numpy as np

# Simulasi 15 Titik Lahan di Garut (Koordinat beda dari Tasikmalaya)
# Garut sekitar Latitude: -7.2278, Longitude: 107.8891
np.random.seed(42)

data_garut = {
    'Nama_Titik': [f'G-{i+1}' for i in range(15)],
    'Latitude': np.linspace(-7.2270, -7.2280, 15) + np.random.normal(0, 0.0001, 15),
    'Longitude': np.linspace(107.8890, 107.8900, 15) + np.random.normal(0, 0.0001, 15),
    'N_mg_kg': np.random.uniform(20, 80, 15), # Variasi N
    'P_mg_kg': np.random.uniform(10, 60, 15), # Variasi P
    'K_mg_kg': np.random.uniform(15, 70, 15), # Variasi K
    'pH': np.random.uniform(4.5, 7.5, 15),    # pH bervariasi (asam ke netral)
    'Kelembapan_Persen': np.random.uniform(50, 80, 15),
    'Suhu_Udara': np.random.uniform(20, 28, 15)
}

df_garut = pd.DataFrame(data_garut)
df_garut.to_excel('Lahan_Garut_15Titik.xlsx', index=False)
print("✅ File 'Lahan_Garut_15Titik.xlsx' berhasil dibuat!")