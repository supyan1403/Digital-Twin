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
import math
from scipy.spatial import KDTree
from shapely.geometry import Polygon, Point


params = {
        "Nitrogen (N)": {"col": "N_mg_kg", "color": "Blues"}, 
        "Fosfor (P)": {"col": "P_mg_kg", "color": "YlOrBr"}, 
        "Kalium (K)": {"col": "K_mg_kg", "color": "Reds"}, 
        "pH Tanah": {"col": "pH", "color": "Viridis"}, 
        "Kelembapan (%)": {"col": "Kelembapan_Persen", "color": "Teal"}, 
        "Suhu Udara (°C)": {"col": "Suhu_Udara", "color": "Plasma"}
        
}

# ==========================================
# 1. SETUP & MODEL AI (Otak Historis)
# ==========================================
st.set_page_config(page_title="Digital Twin Pertanian", layout="wide", page_icon="🌱")

@st.cache_resource
def train_model():
    """Menggunakan dataset awal sebagai basis otak AI"""
    try:
        df_base = pd.read_excel('Dataset_Kriging_Terklasifikasi1.xlsx')
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

from scipy.spatial import ConvexHull

def hitung_luas_m2(lons, lats):
    # 1. Konversi derajat ke meter (pendekatan sederhana di ekuator)
    # 1 derajat lat kira-kira 111,320 meter
    # 1 derajat lon kira-kira 111,320 * cos(lat) meter
    lat_ref = np.mean(lats)
    x = lons * (111320 * np.cos(np.radians(lat_ref)))
    y = lats * 111320
    
    # 2. Ambil titik terluar (Convex Hull)
    points = np.column_stack((x, y))
    hull = ConvexHull(points)
    
    # 3. Luas area hull dalam meter persegi
    return hull.volume # Dalam ConvexHull 2D, 'volume' adalah Luas

def hitung_luas_dan_grid(df):
    try:
        # Cari data secara spesifik berdasarkan Nama_Titik
        t1 = df[df['Nama_Titik'] == 'T1'].iloc[0]
        t4 = df[df['Nama_Titik'] == 'T4'].iloc[0]     # Titik penentu Lebar
        t21 = df[df['Nama_Titik'] == 'T21'].iloc[0]   # Titik penentu Panjang

        # Ukur pakai Haversine
        lebar = hitung_jarak_meter(t1['Latitude'], t1['Longitude'], t4['Latitude'], t4['Longitude'])
        panjang = hitung_jarak_meter(t1['Latitude'], t1['Longitude'], t21['Latitude'], t21['Longitude'])
        
        # Bulatkan secara langsung
        lebar = round(lebar)
        panjang = round(panjang)
        luas_m2 = panjang * lebar
        
        return luas_m2, panjang, lebar

    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengukur: {e}")
        # Fallback (Metode cadangan)
        return 600, 30, 20  # Jika sistem gagal membaca, paksa keluarkan 30x20

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
def hitung_estimasi_biaya(syarat_list, luas_m2):
    """Menghitung biaya pupuk berdasarkan saran perbaikan dan luas lahan"""
    
    # Harga dari CSV (diasumsikan dalam ribuan rupiah)
    harga = {
        "dolomit": 1500, # Rp 1.500 / kg
        "urea": 3000,    # Rp 3.000 / kg
        "sp-36": 3500,   # Rp 3.500 / kg
        "kcl": 5000      # Rp 5.000 / kg
    }
    
    # Asumsi kebutuhan pupuk standar (kg per meter persegi)
    # 1 Ha = 10.000 m2. (Contoh: Urea 200 kg/Ha = 0.02 kg/m2)
    dosis_m2 = {
        "dolomit": 0.2,  
        "urea": 0.02,    
        "sp-36": 0.015,  
        "kcl": 0.01      
    }
    
    total_biaya = 0
    rincian = []
    
    # Gabungkan semua teks saran dan ubah ke huruf kecil untuk pengecekan
    syarat_teks = " ".join(syarat_list).lower()
    
    # Deteksi kebutuhan berdasarkan kata kunci di teks saran
    if "dolomit" in syarat_teks:
        kebutuhan = luas_m2 * dosis_m2["dolomit"]
        biaya = kebutuhan * harga["dolomit"]
        total_biaya += biaya
        rincian.append(f"• **Kapur Dolomit**: {kebutuhan:.1f} kg x Rp {harga['dolomit']:,} = **Rp {biaya:,.0f}**")
        
    if "urea" in syarat_teks:
        kebutuhan = luas_m2 * dosis_m2["urea"]
        biaya = kebutuhan * harga["urea"]
        total_biaya += biaya
        rincian.append(f"• **Pupuk Urea**: {kebutuhan:.1f} kg x Rp {harga['urea']:,} = **Rp {biaya:,.0f}**")
        
    if "sp-36" in syarat_teks:
        kebutuhan = luas_m2 * dosis_m2["sp-36"]
        biaya = kebutuhan * harga["sp-36"]
        total_biaya += biaya
        rincian.append(f"• **Pupuk SP-36**: {kebutuhan:.1f} kg x Rp {harga['sp-36']:,} = **Rp {biaya:,.0f}**")
        
    if "kcl" in syarat_teks:
        kebutuhan = luas_m2 * dosis_m2["kcl"]
        biaya = kebutuhan * harga["kcl"]
        total_biaya += biaya
        rincian.append(f"• **Pupuk KCl**: {kebutuhan:.1f} kg x Rp {harga['kcl']:,} = **Rp {biaya:,.0f}**")
        
    return total_biaya, rincian

def hitung_jarak_meter(lat1, lon1, lat2, lon2):
    # Rumus Haversine sederhana untuk menghitung jarak meter
    R = 6371000  # Jari-jari bumi dalam meter
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c




# ==========================================
# 3. SIDEBAR & UPLOAD FILE
# ==========================================
st.sidebar.title("🌱 Digital Twin Engine")
uploaded_file = st.sidebar.file_uploader("Upload Data Lahan (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)

    df = df.sort_values(by=['Longitude', 'Latitude'], ascending=[True, False]).reset_index(drop=True)
    
    # --- PROSES PEMBERSIHAN KOORDINAT OTOMATIS ---
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['Latitude'] = df['Latitude'].apply(lambda x: konversi_koordinat(x, is_lat=True))
        df['Longitude'] = df['Longitude'].apply(lambda x: konversi_koordinat(x, is_lat=False))
    # ---------------------------------------------
    
    luas, p, l = hitung_luas_dan_grid(df)
    
    st.title(f"📊 Dashboard Digital Twin: {uploaded_file.name}")
    
    m3, m4 = st.columns(2)
    # m1.metric("Total Luas Lahan", f"{luas:.0f} m²", f"{luas/10000:.2f} Ha")
    # m2.metric("Estimasi Dimensi", f"{p:.1f}m x {l:.1f}m")
    m3.metric("Jumlah Titik Sampel", f"{len(df)} Titik")
    m4.metric("Sistem Pakar", "AI & Standar Aktif")

    st.divider()

    tab_data, tab_spasial = st.tabs(["📊 Data Kesuburan", "🗺️ Pemodelan 3D (Kriging)"])

  # ==========================================
    # TAB 1: PETA SATELIT & PANEL ANALISIS
    # ==========================================
    with tab_data:
        # --- BAGIAN ATAS: PETA SATELIT ---
        st.subheader("Lokasi Fisik (Google Satellite)")
        
        m = folium.Map(
            location=[df['Latitude'].mean(), df['Longitude'].mean()], 
            zoom_start=19, 
            max_zoom=22, 
            tiles=None
        )
        
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
            attr='Google', 
            name='Google Satellite',
            max_zoom=22
        ).add_to(m)

        for i, row in df.iterrows():
            label_titik = row['Nama_Titik'] if 'Nama_Titik' in df.columns else f"T{i+1}"
            
            # Marker Bulat
            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=6, color='yellow', fill=True, fill_color='red', fill_opacity=0.9
            ).add_to(m)

            # Label T1-T28 Permanen
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                icon=folium.DivIcon(
                    icon_size=(150,36),
                    icon_anchor=(7, 20),
                    html=f'<div style="font-size: 10pt; color: white; font-weight: bold; text-shadow: 2px 2px 4px #000;">{label_titik}</div>'
                )
            ).add_to(m)
        
        st_folium(m, width=1200, height=450)
        st.divider()

        # --- BAGIAN BAWAH: PANEL ANALISIS ---
        st.subheader("💡 Analisis & Keputusan SPK (Per Titik)")
        
        # 1. TENTUKAN DATA TERLEBIH DAHULU (Sebelum bagi kolom)
        titik_list = df['Nama_Titik'].unique() if 'Nama_Titik' in df.columns else [f"T{i+1}" for i in range(len(df))]
        titik_terpilih = st.selectbox("📍 Pilih ID Titik untuk Dianalisis:", titik_list)
        
        # Ambil Data Titik
        if 'Nama_Titik' in df.columns:
            dt = df[df['Nama_Titik'] == titik_terpilih].iloc[0]
        else:
            idx = int(titik_terpilih.replace("T", "")) - 1
            dt = df.iloc[idx]
            
        # HITUNG EVALUASI (Ini kuncinya agar tidak NameError)
        eval_standar = evaluasi_standar_pertanian(
            dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Suhu_Udara']
        )

        # 2. BARU BAGI KOLOM UNTUK MENAMPILKAN HASIL
        col_input, col_ai, col_pakar = st.columns([1, 1.5, 1.5])
        
        with col_input:
            with st.expander("📝 Parameter Riil", expanded=True):
                st.write(f"**N:** {dt['N_mg_kg']:.2f} | **P:** {dt['P_mg_kg']:.2f}")
                st.write(f"**K:** {dt['K_mg_kg']:.2f} | **pH:** {dt['pH']:.1f}")
                st.write(f"**Suhu:** {dt['Suhu_Udara']:.1f}°C")

        # Kolom Tengah: AI
        with col_ai:
            st.markdown("#### ⚖️ Rekomendasi AI")
            input_val = [[dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Kelembapan_Persen'], dt['Suhu_Udara']]]
        
            # Ambil Prediksi & Probabilitas
            pred_ai = model_ai.predict(input_val)[0]
            probs = model_ai.predict_proba(input_val)[0] 
        
            st.success(f"Tanaman Disarankan: **{pred_ai}**")
        
        # Tampilkan Persentase
        for i, cls in enumerate(model_ai.classes_):
            p_persen = probs[i] * 100
            st.caption(f"{cls}: {p_persen:.1f}%")
            st.progress(float(probs[i]))
        with col_pakar:
            st.markdown("#### 🎯 Hasil Sistem Pakar")
            tanaman_uji = st.selectbox("Cek Tanaman Lain:", ["Caisim", "Jagung", "Singkong"])
            
            res = eval_standar[tanaman_uji]
            st.write(f"**Status: {res['status']}**")
            if res['syarat']:
                for s in res['syarat']:
                    st.write(f"⚠️ {s}")
            else:
                st.write("✅ Lahan sudah optimal.")

           # --- Di dalam Tab 1 ---
        
    # --- DI DALAM TAB 1 ---

    # 1. PERHITUNGAN LUAS AWAL (Tetap di belakang layar)
        luas_otomatis = 0.0
        try:
            if len(df) >= 3:
                luas_otomatis = hitung_luas_m2(df['Longitude'].values, df['Latitude'].values)
        except:
            luas_otomatis = 500.0

        # 2. AREA INPUT TERPISAH
        with st.expander("⚙️ Konfigurasi Sistem Digital Twin", expanded=True):
            
            # SEKSI A: TARGET UNSUR HARA (Kondisi Ideal Tanah)
            st.markdown("### 🎯 1. Target Unsur Hara Tanah")
            st.caption("Tentukan ambang batas ideal sesuai jenis komoditas yang akan ditanam.")
            c1, c2, c3, c4 = st.columns(4)
            target_ph = c1.number_input("Target pH", value=6.5, step=0.1, help="Standar keasaman tanah")
            target_n = c2.number_input("Target N (mg/kg)", value=40.0)
            target_p = c3.number_input("Target P (mg/kg)", value=20.0)
            target_k = c4.number_input("Target K (mg/kg)", value=30.0)

            st.divider() # Garis pemisah visual

            # SEKSI B: HARGA PASAR (Kondisi Ekonomi)
            st.markdown("### 💰 2. Parameter Ekonomi (Harga Pupuk)")
            st.caption("Masukkan harga pasar terbaru per kilogram material.")
            c5, c6, c7, c8 = st.columns(4)
            harga_kapur = c5.number_input("Harga Kapur", value=5000)
            harga_urea = c6.number_input("Harga Urea", value=10000)
            harga_sp36 = c7.number_input("Harga SP-36", value=8000)
            harga_kcl = c8.number_input("Harga KCl", value=12000)

            st.divider()

            # SEKSI C: DIMENSI FISIK (Terpisah Sendiri)
            st.markdown("### 📏 3. Dimensi Lahan")
            st.caption("Luas lahan total yang akan diproses oleh sistem.")
            # Kita letakkan luas lahan di kolom yang lebih lebar agar menonjol
            luas_input = st.number_input("Luas Lahan Total (m²)", 
                                         value=int(luas_otomatis) if luas_otomatis > 0 else 600,
                                         help="Angka ini akan dibagi rata ke seluruh titik sampel.")

        # --- LOGIKA PERHITUNGAN TETAP SAMA ---
        total_titik = len(df)
        luas_per_titik = luas_input / total_titik if total_titik > 0 else 0
    

        # 4. FUNGSI ANALISIS PRESISI FULL NPK
        def analisis_presisi_npk(row, lpt_val, h_urea, h_kapur, h_sp36, h_kcl, t_n, t_ph, t_p, t_k):
            pesan = []
            biaya_titik = 0
            
            # --- HITUNG KAPUR (Untuk pH) ---
            if row['pH'] < t_ph:
                selisih_ph = t_ph - row['pH']
                kg_kapur = selisih_ph * 0.5 * (lpt_val / 10)
                biaya_titik += kg_kapur * h_kapur
                pesan.append(f"🧪 Kapur: {kg_kapur:.2f}kg")
            
            # --- HITUNG UREA (Untuk N) ---
            if 'N_mg_kg' in row and row['N_mg_kg'] < t_n:
                selisih_n = t_n - row['N_mg_kg']
                kg_urea = (selisih_n / 10) * 0.01 * lpt_val
                biaya_titik += kg_urea * h_urea
                pesan.append(f"🍃 Urea: {kg_urea:.2f}kg")

            # --- HITUNG SP-36 (Untuk P) ---
            if 'P_mg_kg' in row and row['P_mg_kg'] < t_p:
                selisih_p = t_p - row['P_mg_kg']
                # Asumsi dosis: 0.008 kg per m2 untuk 10 poin defisit P
                kg_sp36 = (selisih_p / 10) * 0.008 * lpt_val 
                biaya_titik += kg_sp36 * h_sp36
                pesan.append(f"🌾 SP-36: {kg_sp36:.2f}kg")

            # --- HITUNG KCl (Untuk K) ---
            if 'K_mg_kg' in row and row['K_mg_kg'] < t_k:
                selisih_k = t_k - row['K_mg_kg']
                # Asumsi dosis: 0.005 kg per m2 untuk 10 poin defisit K
                kg_kcl = (selisih_k / 10) * 0.005 * lpt_val
                biaya_titik += kg_kcl * h_kcl
                pesan.append(f"🥔 KCl: {kg_kcl:.2f}kg")
            
            rekomendasi = " | ".join(pesan) if pesan else "✨ Optimal"
            return rekomendasi, round(biaya_titik)

        # 5. EKSEKUSI DATA
        df_res = df.copy()
        hasil_analisis = df_res.apply(
            lambda r: analisis_presisi_npk(
                r, luas_per_titik, harga_urea, harga_kapur, harga_sp36, harga_kcl, 
                target_n, target_ph, target_p, target_k
            ), axis=1
        )
        df_res['Kebutuhan Material (Kg)'], df_res['Estimasi Biaya (Rp)'] = zip(*hasil_analisis)

        # 6. PERCANTIK TAMPILAN TABEL
        df_display = df_res.copy()
        df_display['Estimasi Biaya (Rp)'] = df_display['Estimasi Biaya (Rp)'].apply(lambda x: f"Rp {int(x):,}".replace(',', '.'))
        df_display['Urutan'] = df_display['Nama_Titik'].str.extract('(\d+)').astype(int)
        df_display = df_display.sort_values('Urutan').drop(columns=['Urutan']).reset_index(drop=True)

        # 7. TAMPILKAN TABEL DAN TOTAL BIAYA
        st.write("### 📊 Tabel Rekomendasi per Titik (Full NPK)")
        st.table(df_display[['Nama_Titik', 'pH', 'Kebutuhan Material (Kg)', 'Estimasi Biaya (Rp)']])
        
        total_biaya_lahan = df_res['Estimasi Biaya (Rp)'].sum()
        st.info(f"**Total Anggaran Pengadaan Pupuk & Kapur:** Rp {int(total_biaya_lahan):,}".replace(',', '.'))
# ==========================================
# TAB 2: PEMODELAN 3D (SINKRON DENGAN TAB 1)
# ==========================================

    with tab_spasial:
        st.subheader("Visualisasi Digital Twin (Info Hover Lengkap)")

        # 1. Definisi Parameter & Warna
        params = {
            'pH': {'col': 'pH', 'color': 'Viridis'},
            'Nitrogen': {'col': 'N_mg_kg', 'color': 'Greens'},
            'Fosfor': {'col': 'P_mg_kg', 'color': 'YlOrRd'},
            'Kalium': {'col': 'K_mg_kg', 'color': 'Purples'},
            'Kelembapan': {'col': 'Kelembapan_Persen', 'color': 'Blues'},
            'Suhu': {'col': 'Suhu_Udara', 'color': 'Reds'}
        }

        pilihan_label = st.selectbox("Pilih Parameter:", list(params.keys()))
        info = params[pilihan_label]

        try:
            from scipy.interpolate import griddata
            from scipy.spatial import KDTree # Untuk mencari nama titik terdekat
            
            # Bersihkan data
            df_p = df.dropna(subset=[info['col']])
            lons = df_p['Longitude'].values
            lats = df_p['Latitude'].values
            z_val = df_p[info['col']].values
            nama_titik_asli = df_p['Nama_Titik'].values

            # 2. Buat Grid (Sumbu Y dibalik: Max ke Min agar T1 di Kiri Atas)
            ux = np.linspace(lons.min(), lons.max(), 50)
            uy = np.linspace(lats.max(), lats.min(), 50) 
            X_grid, Y_grid = np.meshgrid(ux, uy)

            # 3. Logika Hover: Mencari Nama Titik Terdekat untuk setiap titik di Grid
            tree = KDTree(np.column_stack((lons, lats)))
            _, indices = tree.query(np.column_stack((X_grid.ravel(), Y_grid.ravel())))
            closest_names = nama_titik_asli[indices].reshape(X_grid.shape)

            # 4. Interpolasi Grid (Method Cubic agar Mulus)
            Z = griddata((lons, lats), z_val, (X_grid, Y_grid), method='cubic')

            # 5. Visualisasi Plotly
            fig = go.Figure()

            # A. Permukaan 3D dengan Custom Data (Nama Titik)
            fig.add_trace(go.Surface(
                x=X_grid, 
                y=Y_grid, 
                z=Z,
                customdata=closest_names, # Memasukkan nama titik ke hover
                colorscale=info['color'],
                colorbar_title=pilihan_label,
                hovertemplate=(
                    "<b>📍 Lokasi: Sekitar %{customdata}</b><br>" +
                    "----------------------------<br>" +
                    "<b>Latitude</b>: %{y:.6f}<br>" +
                    "<b>Longitude</b>: %{x:.6f}<br>" +
                    f"<b>Kadar {pilihan_label}</b>: " + "%{z:.2f}<extra></extra>"
                )
            ))

            # B. Titik Sampel (Titik Merah agar Sinkron dengan Tab 1)
            fig.add_trace(go.Scatter3d(
                x=lons, 
                y=lats, 
                z=z_val,
                mode='markers+text',
                text=nama_titik_asli,
                name="Titik Riil",
                marker=dict(size=4, color='red', line=dict(color='white', width=1)),
                textfont=dict(size=9, color='black'),
                hovertemplate="<b>Titik: %{text}</b><extra></extra>"
            ))

            # 6. Atur Tampilan Sumbu
            fig.update_layout(
                scene=dict(
                    aspectmode='manual',
                    aspectratio=dict(x=1, y=1, z=0.4),
                    xaxis_title="Longitude",
                    yaxis_title="Latitude",
                    zaxis_title=pilihan_label,
                    xaxis=dict(tickformat=".5f"),
                    yaxis=dict(tickformat=".5f")
                ),
                margin=dict(l=0, r=0, b=0, t=40),
                height=700
            )
            
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Gagal memproses visualisasi: {e}")