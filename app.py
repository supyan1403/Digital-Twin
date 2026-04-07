import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from pykrige.ok import OrdinaryKriging
from geopy.distance import geodesic
from sklearn.ensemble import RandomForestClassifier
import re

# ==========================================
# 1. SETUP & MODEL AI (Otak Historis)
# ==========================================
st.set_page_config(page_title="Digital Twin Pertanian", layout="wide", page_icon="🌱")

@st.cache_resource
def train_model():
    """Menggunakan dataset awal sebagai basis otak AI"""
    try:
        df_base = pd.read_excel('Dataset_Kriging_Terklasifikasi.xlsx')
        X = df_base[['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']]
        y = df_base['Jenis_Komoditas']
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        return model
    except Exception as e:
        st.error(f"Gagal memuat dataset untuk AI: {e}")
        return None

model_ai = train_model()

if model_ai is None:
    st.stop()

# ==========================================
# 2. FUNGSI LOGIKA (AREA & STANDAR PAKAR)
# ==========================================
def konversi_koordinat(teks_kordinat, is_lat=False):
    """Mengubah format 7°20'31.40 menjadi desimal -7.342055"""
    # Jika data sudah berupa angka (float/int), langsung kembalikan
    if isinstance(teks_kordinat, (int, float)):
        hasil = float(teks_kordinat)
    else:
        # Ubah ke string dan bersihkan spasi
        teks = str(teks_kordinat).strip()
        
        # Ekstrak semua angka dari teks menggunakan Regex
        angka = re.findall(r"[\d\.]+", teks)
        
        if not angka:
            return 0.0
            
        derajat = float(angka[0]) if len(angka) > 0 else 0.0
        menit = float(angka[1]) if len(angka) > 1 else 0.0
        detik = float(angka[2]) if len(angka) > 2 else 0.0
        
        # Rumus konversi DMS ke Decimal Degrees
        hasil = derajat + (menit / 60) + (detik / 3600)
        
        # Jika teks aslinya punya tanda minus di depan
        if teks.startswith("-"):
            hasil = -abs(hasil)
            
    # Otomatis jadikan minus untuk Latitude (karena di Lintang Selatan / Indonesia)
    if is_lat and hasil > 0:
        hasil = -hasil
        
    return hasil

def hitung_luas_dan_grid(df):
    lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
    lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
    lebar = geodesic((lat_min, lon_min), (lat_min, lon_max)).meters
    panjang = geodesic((lat_min, lon_min), (lat_max, lon_min)).meters
    luas_m2 = panjang * lebar
    return luas_m2, panjang, lebar

def evaluasi_standar_pertanian(n, p, k, ph, suhu):
    """Otak Pakar: Evaluasi Kesesuaian Lahan Saintifik"""
    hasil = {}
    
    # --- Standar Caisim ---
    status_c, saran_c = "S3 (Tidak Sesuai)", []
    if (6.0 <= ph <= 7.0) and (15 <= suhu <= 22) and (n >= 40): status_c = "S1 (Sangat Sesuai)"
    elif (5.5 <= ph <= 7.5): status_c = "S2 (Cukup Sesuai)"
    if ph < 6.0: saran_c.append("Naikkan pH ke 6.0 dengan Kapur Dolomit.")
    elif ph > 7.0: saran_c.append("Turunkan pH ke 7.0 dengan organik.")
    if suhu > 22: saran_c.append("Suhu terlalu panas. Gunakan paranet (<22°C).")
    if n < 40: saran_c.append("Nitrogen rendah. Tambahkan Urea.")
    hasil['Caisim'] = {"status": status_c, "syarat": saran_c}

    # --- Standar Jagung ---
    status_j, saran_j = "S3 (Tidak Sesuai)", []
    if (5.8 <= ph <= 7.8) and (20 <= suhu <= 26) and (p >= 40): status_j = "S1 (Sangat Sesuai)"
    elif (5.5 <= ph <= 8.2): status_j = "S2 (Cukup Sesuai)"
    if ph < 5.8: saran_j.append("Naikkan pH ke 5.8 dengan Dolomit.")
    if p < 40: saran_j.append("Fosfor rendah. Tambahkan SP-36.")
    if suhu < 20 or suhu > 26: saran_j.append("Suhu kurang ideal (Butuh 20-26°C).")
    hasil['Jagung'] = {"status": status_j, "syarat": saran_j}

    # --- Standar Singkong ---
    status_s, saran_s = "S3 (Tidak Sesuai)", []
    if (5.2 <= ph <= 7.0) and (22 <= suhu <= 28) and (k >= 40): status_s = "S1 (Sangat Sesuai)"
    elif (4.8 <= ph <= 7.6): status_s = "S2 (Cukup Sesuai)"
    if ph < 5.2: saran_s.append("Naikkan pH ke 5.2 dengan Dolomit.")
    if k < 40: saran_s.append("Kalium rendah. Tambahkan KCL.")
    if suhu < 22: saran_s.append("Suhu terlalu dingin (>22°C).")
    hasil['Singkong'] = {"status": status_s, "syarat": saran_s}

    return hasil

# ==========================================
# 3. SIDEBAR & UPLOAD FILE
# ==========================================
st.sidebar.title("🌱 Digital Twin Engine")
uploaded_file = st.sidebar.file_uploader("Upload Data Lahan (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    
    # --- PROSES PEMBERSIHAN KOORDINAT OTOMATIS ---
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['Latitude'] = df['Latitude'].apply(lambda x: konversi_koordinat(x, is_lat=True))
        df['Longitude'] = df['Longitude'].apply(lambda x: konversi_koordinat(x, is_lat=False))
    # ---------------------------------------------
    
    luas, p, l = hitung_luas_dan_grid(df)
    
    st.title(f"📊 Dashboard Digital Twin: {uploaded_file.name}")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Luas Lahan", f"{luas:.0f} m²", f"{luas/10000:.2f} Ha")
    m2.metric("Estimasi Dimensi", f"{p:.1f}m x {l:.1f}m")
    m3.metric("Jumlah Titik Sampel", f"{len(df)} Titik")
    m4.metric("Sistem Pakar", "AI & Standar Aktif")

    st.divider()

    tab_satelit, tab_spasial = st.tabs(["🛰️ Lokasi & Analisis Keputusan", "⛰️ Peta 3D Kriging (Iklim & Hara)"])

    # ==========================================
    # TAB 1: PETA SATELIT FULL WIDTH & PANEL BAWAH
    # ==========================================
    with tab_satelit:
        # --- BAGIAN ATAS: PETA FULL WIDTH ---
        st.subheader("Lokasi Fisik (Google Satellite)")
        m = folium.Map(
            location=[df['Latitude'].mean(), df['Longitude'].mean()], 
            zoom_start=19, 
            max_zoom=22,  # <--- BATAS ZOOM DIBUKA
            tiles=None
        )
        
        # 2. Tambahkan max_zoom=22 di sini juga
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google', 
            name='Google Satellite',
            max_zoom=22   # <--- BATAS ZOOM TILE DIBUKA
        ).add_to(m)
        for _, row in df.iterrows():
            info_popup = f"<b>Titik: {row['Nama_Titik']}</b><br>pH: {row['pH']}<br>Suhu: {row['Suhu_Udara']}°C<br>N: {row['N_mg_kg']:.1f} | P: {row['P_mg_kg']:.1f} | K: {row['K_mg_kg']:.1f}"
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=6, color='yellow', fill=True, fill_color='red', popup=folium.Popup(info_popup, max_width=250)).add_to(m)
        
        # Peta diubah menjadi lebih lebar
        st_folium(m, width=1200, height=450)
        
        st.divider()

        # --- BAGIAN BAWAH: PANEL ANALISIS ---
        st.subheader("💡 Analisis & Keputusan SPK (Per Titik)")
        
        # Membagi panel bawah menjadi 3 kolom agar rapi
        col_input, col_ai, col_pakar = st.columns([1, 1.5, 1.5])
        
        # Kolom Kiri: Pemilihan Titik & Data Mentah
        with col_input:
            titik = st.selectbox("📍 Pilih ID Titik:", df['Nama_Titik'].unique())
            dt = df[df['Nama_Titik'] == titik].iloc[0]
            
            with st.expander("Parameter Lingkungan", expanded=True):
                st.write(f"**N:** {dt['N_mg_kg']:.2f} | **P:** {dt['P_mg_kg']:.2f} | **K:** {dt['K_mg_kg']:.2f}")
                st.write(f"**pH:** {dt['pH']:.1f} | **Lembap:** {dt['Kelembapan_Persen']:.1f}% | **Suhu:** {dt['Suhu_Udara']:.1f}°C")

        # Proses Data
        input_val = [[dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Kelembapan_Persen'], dt['Suhu_Udara']]]
        pred_ai = model_ai.predict(input_val)[0]
        probs = model_ai.predict_proba(input_val)[0]
        eval_standar = evaluasi_standar_pertanian(dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Suhu_Udara'])
        
        s1_crops = [c for c, d in eval_standar.items() if 'S1' in d['status']]
        s2_crops = [c for c, d in eval_standar.items() if 'S2' in d['status']]
        if s1_crops:
            pred_pakar, alasan = s1_crops[0], "Karena berstatus S1 (Sangat Sesuai)"
        elif s2_crops:
            pred_pakar, alasan = s2_crops[0], "Karena berstatus S2 (Cukup Sesuai)"
        else:
            pred_pakar, alasan = "Tidak ada yang ideal", "Semua tanaman berstatus S3"

        # Kolom Tengah: Head-to-Head AI vs Pakar
        with col_ai:
            st.markdown("#### ⚖️ Kesimpulan Sistem")
            if pred_ai == pred_pakar:
                st.markdown(f"<div style='background-color:#2ecc71;padding:10px;border-radius:5px;color:white;'><b>SEPAKAT!</b><br>AI dan Standar Pertanian setuju merekomendasikan <b>{pred_ai}</b>.</div>", unsafe_allow_html=True)
                
                syarat_sepakat = eval_standar[pred_ai]['syarat']
                if syarat_sepakat:
                    st.warning("**Saran Optimalisasi:**\n" + "\n".join([f"- {s}" for s in syarat_sepakat]))
                else:
                    st.success("**Saran Optimalisasi:**\n- Kondisi sudah optimal, tidak ada penanganan khusus yang diperlukan.")
                    
            else:
                st.markdown(f"<div style='background-color:#e67e22;padding:10px;border-radius:5px;color:white;'><b>BERBEDA PENDAPAT!</b><br>AI condong ke <b>{pred_ai}</b> (Riwayat), tetapi kondisi riil ideal untuk <b>{pred_pakar}</b> (Pakar).</div>", unsafe_allow_html=True)
                
                syarat_beda = eval_standar[pred_ai]['syarat']
                if syarat_beda:
                    st.warning(f"**Saran jika ingin tanam {pred_ai}:**\n" + "\n".join([f"- {s}" for s in syarat_beda]))
                else:
                    st.info(f"**Saran jika ingin tanam {pred_ai}:**\n- Parameter utama (pH, Suhu, Hara) secara umum sudah memenuhi ambang batas minimum untuk {pred_ai}. Anda bisa tetap menanamnya.")
            
            with st.expander("Lihat Detail Probabilitas AI"):
                for i, cls in enumerate(model_ai.classes_):
                    st.caption(f"{cls}: {probs[i]*100:.1f}%")
                    st.progress(float(probs[i]))

        # Kolom Kanan: Simulasi Kustom
        with col_pakar:
            st.markdown("#### 🎯 Simulasi Kesesuaian Manual")
            tanaman_uji = st.selectbox("Pilih Tanaman Uji:", ["Caisim", "Jagung", "Singkong"], key="uji_simulasi")
            
            status_uji = eval_standar[tanaman_uji]['status']
            syarat_uji = eval_standar[tanaman_uji]['syarat']
            
            if "S1" in status_uji:
                warna_uji = "#2ecc71"
                pesan_status = "✅ SANGAT COCOK"
            elif "S2" in status_uji:
                warna_uji = "#f1c40f"
                pesan_status = "⚠️ CUKUP COCOK"
            else:
                warna_uji = "#e74c3c"
                pesan_status = "❌ TIDAK COCOK"
                
            st.markdown(f"<div style='background-color:{warna_uji};padding:10px;border-radius:5px;color:white;text-align:center;'><b>{pesan_status}</b><br>{status_uji}</div>", unsafe_allow_html=True)
            
            if syarat_uji:
                st.write("**Perbaikan yang dibutuhkan:**")
                for s in syarat_uji:
                    st.write(f"- {s}")
            else:
                st.write("Kandungan tanah sudah optimal.")

    # ==========================================
    # TAB 2: KRIGING 3D 
    # ==========================================
    with tab_spasial:
        st.subheader("Pemodelan Spasial 3D (Kriging)")
        gx = np.linspace(df['Longitude'].min(), df['Longitude'].max(), 50)
        gy = np.linspace(df['Latitude'].min(), df['Latitude'].max(), 50)
        
        params = {"Nitrogen (N)": {"col": "N_mg_kg", "color": "Blues"}, "Fosfor (P)": {"col": "P_mg_kg", "color": "YlOrBr"}, "Kalium (K)": {"col": "K_mg_kg", "color": "Reds"}, "pH Tanah": {"col": "pH", "color": "Viridis"}, "Kelembapan (%)": {"col": "Kelembapan_Persen", "color": "Teal"}, "Suhu Udara (°C)": {"col": "Suhu_Udara", "color": "Plasma"}}
        
        col_k1, col_k2 = st.columns(2)
        for i, (label, info) in enumerate(params.items()):
            with (col_k1 if i % 2 == 0 else col_k2):
                st.markdown(f"**{label}**")
                try:
                    ok = OrdinaryKriging(df['Longitude'], df['Latitude'], df[info['col']], variogram_model='linear')
                    z, _ = ok.execute('grid', gx, gy)
                    fig = go.Figure(data=[go.Surface(z=z, x=gx, y=gy, colorscale=info['color'], showscale=False)])
                    fig.update_layout(height=400, margin=dict(l=0, r=0, b=0, t=0), scene=dict(zaxis_title=label, xaxis=dict(showticklabels=False, title=""), yaxis=dict(showticklabels=False, title="")))
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass

else:
    st.info("👈 Silakan upload file dataset lahan Anda (Excel/CSV) di menu samping untuk memulai simulasi.")