import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# 1. Load Data
file_name = 'Dataset_Kriging_Terklasifikasi.xlsx'
if os.path.exists(file_name):
    df = pd.read_excel(file_name)
else:
    df = pd.read_csv('Dataset_Kriging_Terklasifikasi.xlsx - Sheet1.csv')

# Asumsi grid 8x4 petak (total 32)
panjang_x = 8
lebar_y = 4

# Buat koordinat X dan Y untuk jaring laba-laba (mesh)
x = np.linspace(0, panjang_x, 50)
y = np.linspace(0, lebar_y, 50)
X, Y = np.meshgrid(x, y)

# Buat Z (Ketinggian Lahan)
Z = np.sin(X * 0.5) * np.cos(Y * 0.5) * 0.2

# 2. Buat Peta 3D Dasar (Tanah)
fig = go.Figure(data=[go.Surface(
    z=Z, 
    x=X, 
    y=Y, 
    colorscale='Earth', 
    showscale=False
)])

# 3. Pengaturan Tampilan 3D (Kamera dan Grid)
fig.update_layout(
    title='Simulasi Blok Lahan 3D - Tenjonagara',
    autosize=True,
    scene=dict(
        xaxis=dict(title='Panjang Lahan (m)', showgrid=True),
        yaxis=dict(title='Lebar Lahan (m)', showgrid=True),
        zaxis=dict(title='Ketinggian', showgrid=False, range=[-1, 2]),
        camera=dict(
            eye=dict(x=1.8, y=-1.8, z=1.2)
        ),
        aspectratio=dict(x=2, y=1, z=0.2) 
    )
)

# 4. SIMPAN SEBAGAI FILE HTML (Ini perubahannya)
nama_file_html = 'Peta_Lahan_3D_Iyan.html'
fig.write_html(nama_file_html)

print(f"✅ Selesai! File '{nama_file_html}' berhasil dibuat.")
print("Silakan buka folder skripsi kamu, lalu klik dua kali file tersebut.")