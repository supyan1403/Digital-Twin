import pandas as pd
import numpy as np
import math
import re
from scipy.spatial import ConvexHull
from sklearn.ensemble import RandomForestClassifier
from fpdf import FPDF
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model():
    """Menggunakan dataset 144 baris untuk melatih dan menguji AI"""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score


        df_base = pd.read_excel('Dataset_Augmented.xlsx') 
        X = df_base[['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']]
        y = df_base['Jenis_Komoditas']
        

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        

        model = RandomForestClassifier(
        n_estimators=50,
        max_depth=4,
        random_state=42
    )
        model.fit(X_train, y_train)
        

        y_pred = model.predict(X_test)
        akurasi = accuracy_score(y_test, y_pred) * 100
        

        return {"model": model, "akurasi": akurasi}
        
    except Exception as e:
        print("Error AI:", e)
        return {"model": None, "akurasi": 0.0}

def konversi_koordinat(teks_kordinat, is_lat=False):
    """Mengubah format derajat ke desimal"""
    if isinstance(teks_kordinat, (int, float)):
        hasil = float(teks_kordinat)
    else:
        teks = str(teks_kordinat).strip()
        angka = re.findall(r"[\d\.]+", teks)
        if not angka: return 0.0
        derajat = float(angka[0]) if len(angka) > 0 else 0.0
        menit = float(angka[1]) if len(angka) > 1 else 0.0
        detik = float(angka[2]) if len(angka) > 2 else 0.0
        hasil = derajat + (menit / 60) + (detik / 3600)
        if teks.startswith("-"): hasil = -abs(hasil)
        
    if is_lat and hasil > 0:
        hasil = -hasil
    return hasil

def hitung_jarak_meter(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def hitung_luas_m2(lons, lats):
    lat_ref = np.mean(lats)
    x = lons * (111320 * np.cos(np.radians(lat_ref)))
    y = lats * 111320
    points = np.column_stack((x, y))
    hull = ConvexHull(points)
    return hull.volume 

def hitung_luas_dan_grid(df):
    try:
        t1 = df[df['Nama_Titik'] == 'T1'].iloc[0]
        t4 = df[df['Nama_Titik'] == 'T4'].iloc[0]
        t21 = df[df['Nama_Titik'] == 'T21'].iloc[0]

        lebar = hitung_jarak_meter(t1['Latitude'], t1['Longitude'], t4['Latitude'], t4['Longitude'])
        panjang = hitung_jarak_meter(t1['Latitude'], t1['Longitude'], t21['Latitude'], t21['Longitude'])
        
        lebar = round(lebar)
        panjang = round(panjang)
        return panjang * lebar, panjang, lebar
    except Exception:
        return 600, 30, 20

def evaluasi_standar_pertanian(n, p, k, ph, suhu):
    """Otak Pakar: Evaluasi Kesesuaian Lahan Saintifik"""
    hasil = {}
    

    status_c, saran_c = "S3 (Tidak Sesuai)", []
    if (6.0 <= ph <= 7.0) and (15 <= suhu <= 22) and (n >= 40): status_c = "S1 (Sangat Sesuai)"
    elif (5.5 <= ph <= 7.5): status_c = "S2 (Cukup Sesuai)"
    if ph < 6.0: saran_c.append("Naikkan pH ke 6.0 dengan Kapur Dolomit.")
    elif ph > 7.0: saran_c.append("Turunkan pH ke 7.0 dengan organik.")
    if suhu > 22: saran_c.append("Suhu terlalu panas. Gunakan paranet (<22°C).")
    if n < 40: saran_c.append("Nitrogen rendah. Tambahkan Urea.")
    hasil['Caisim'] = {"status": status_c, "syarat": saran_c}


    status_j, saran_j = "S3 (Tidak Sesuai)", []
    if (5.8 <= ph <= 7.8) and (20 <= suhu <= 26) and (p >= 40): status_j = "S1 (Sangat Sesuai)"
    elif (5.5 <= ph <= 8.2): status_j = "S2 (Cukup Sesuai)"
    if ph < 5.8: saran_j.append("Naikkan pH ke 5.8 dengan Dolomit.")
    if p < 40: saran_j.append("Fosfor rendah. Tambahkan SP-36.")
    if suhu < 20 or suhu > 26: saran_j.append("Suhu kurang ideal (Butuh 20-26°C).")
    hasil['Jagung'] = {"status": status_j, "syarat": saran_j}


    status_s, saran_s = "S3 (Tidak Sesuai)", []
    if (5.2 <= ph <= 7.0) and (22 <= suhu <= 28) and (k >= 40): status_s = "S1 (Sangat Sesuai)"
    elif (4.8 <= ph <= 7.6): status_s = "S2 (Cukup Sesuai)"
    if ph < 5.2: saran_s.append("Naikkan pH ke 5.2 dengan Dolomit.")
    if k < 40: saran_s.append("Kalium rendah. Tambahkan KCL.")
    if suhu < 22: saran_s.append("Suhu terlalu dingin (>22°C).")
    hasil['Singkong'] = {"status": status_s, "syarat": saran_s}

    return hasil

def analisis_presisi_npk(row, lpt_val, h_urea, h_kapur, h_sp36, h_kcl, t_n, t_ph_min, t_ph_max, t_p, t_k):
    pesan = []
    biaya_titik = 0
    

    if row['pH'] < t_ph_min:

        kg_kapur = (t_ph_min - row['pH']) * 0.5 * (lpt_val / 10)
        biaya_titik += kg_kapur * h_kapur
        pesan.append(f"Kapur Dolomit: {kg_kapur:.2f}kg")
        
    elif row['pH'] > t_ph_max:

        kg_sulfur = (row['pH'] - t_ph_max) * 0.2 * (lpt_val / 10) 
        harga_sulfur = 15000 
        biaya_titik += kg_sulfur * harga_sulfur
        pesan.append(f"Sulfur: {kg_sulfur:.2f}kg")


    if 'N_mg_kg' in row and row['N_mg_kg'] < t_n:
        kg_urea = ((t_n - row['N_mg_kg']) / 10) * 0.01 * lpt_val
        biaya_titik += kg_urea * h_urea
        pesan.append(f"Urea: {kg_urea:.2f}kg")
        
    if 'P_mg_kg' in row and row['P_mg_kg'] < t_p:
        kg_sp36 = ((t_p - row['P_mg_kg']) / 10) * 0.008 * lpt_val 
        biaya_titik += kg_sp36 * h_sp36
        pesan.append(f"SP-36: {kg_sp36:.2f}kg")
        
    if 'K_mg_kg' in row and row['K_mg_kg'] < t_k:
        kg_kcl = ((t_k - row['K_mg_kg']) / 10) * 0.005 * lpt_val
        biaya_titik += kg_kcl * h_kcl
        pesan.append(f"KCl: {kg_kcl:.2f}kg")
        
    rekomendasi = " | ".join(pesan) if pesan else "Optimal"
    return rekomendasi, round(biaya_titik)

from fpdf import FPDF

def generate_pdf_report(df, total_biaya, komoditas):
    pdf = FPDF()
    pdf.add_page()
    

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, "LAPORAN REKOMENDASI PEMUPUKAN PRESISI", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Komoditas Target: {komoditas}", ln=True, align='C')
    pdf.ln(10)
    

    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Titik", 1, 0, 'C', True)
    pdf.cell(120, 10, "Rekomendasi Material", 1, 0, 'C', True)
    pdf.cell(50, 10, "Estimasi Biaya", 1, 1, 'C', True)
    

    pdf.set_font("Arial", '', 9)
    for index, row in df.iterrows():

        rek = row['Rekomendasi'] if row['Rekomendasi'] != "Optimal" else "Kondisi Tanah Optimal"
        pdf.cell(20, 10, str(row['Nama_Titik']), 1, 0, 'C')
        pdf.cell(120, 10, rek, 1, 0, 'L')
        pdf.cell(50, 10, f"Rp {int(row['Biaya_Rp']):,}".replace(',', '.'), 1, 1, 'R')
        

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(140, 10, "TOTAL ESTIMASI BIAYA KESELURUHAN", 0, 0, 'R')
    pdf.cell(50, 10, f"Rp {int(total_biaya):,}".replace(',', '.'), 1, 1, 'R')
    
    return bytes(pdf.output())