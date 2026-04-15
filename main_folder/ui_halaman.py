import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from scipy.interpolate import griddata
from scipy.spatial import KDTree
from kalkulasi import evaluasi_standar_pertanian, analisis_presisi_npk, hitung_luas_m2

def tampilkan_tab_dashboard(df, model_ai, skor_akurasi):
    # ---------------------------------------------------------
    # 1. HEADER METRICS (RINGKASAN LAHAN)
    # ---------------------------------------------------------
    st.subheader("📊 Ringkasan Kondisi Lahan")
    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    
    avg_ph = df['pH'].mean()
    avg_n = df['N_mg_kg'].mean()
    
    c_m1.metric("Rerata pH", f"{avg_ph:.2f}", delta="- Asam" if avg_ph < 6 else "Normal")
    c_m2.metric("Rerata Nitrogen", f"{avg_n:.1f} mg/kg")
    c_m3.metric("Akurasi AI", f"{skor_akurasi:.1f}%")
    c_m4.metric("Total Titik", len(df))
    st.divider()

    # ---------------------------------------------------------
    # 2. PETA SATELIT
    # ---------------------------------------------------------
    st.subheader("🌍 Lokasi Fisik (Google Satellite)")
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=19, max_zoom=22, tiles=None)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite', max_zoom=22).add_to(m)

    for i, row in df.iterrows():
        label_titik = row['Nama_Titik'] if 'Nama_Titik' in df.columns else f"T{i+1}"
        folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=6, color='yellow', fill=True, fill_color='red', fill_opacity=0.9).add_to(m)
        folium.Marker(location=[row['Latitude'], row['Longitude']], icon=folium.DivIcon(icon_size=(150,36), icon_anchor=(7, 20), html=f'<div style="font-size: 10pt; color: white; font-weight: bold; text-shadow: 2px 2px 4px #000;">{label_titik}</div>')).add_to(m)
    st_folium(m, width=1200, height=450)
    st.divider()

    # ---------------------------------------------------------
    # 3. PANEL ANALISIS SPK & AI (DIPERBAIKI)
    # ---------------------------------------------------------
    st.subheader("💡 Analisis & Keputusan SPK")
    
    # 1. Ambil nama titik unik (agar tidak dobel T1, T1...)
    titik_list = df['Nama_Titik'].unique().tolist()
    
    # 2. Urutkan secara cerdas (Natural Sort)
    # Menggunakan regex untuk mengambil angka di dalam nama titik (T1, T2, dst)
    import re
    titik_list.sort(key=lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0)
    
    # 3. Masukkan ke Selectbox
    titik_terpilih = st.selectbox("📍 Pilih ID Titik untuk Dianalisis:", titik_list)

    if 'Nama_Titik' in df.columns:
        dt = df[df['Nama_Titik'] == titik_terpilih].iloc[0]
    else:
        idx = int(titik_terpilih.replace("T", "")) - 1
        dt = df.iloc[idx]

    eval_standar = evaluasi_standar_pertanian(dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Suhu_Udara'])

    col_ai, col_pakar = st.columns(2)
    with col_ai:
        st.markdown("#### ⚖️ Rekomendasi AI")
        st.caption(f"🎯 Akurasi Model: {skor_akurasi:.1f}%")
        input_val = [[dt['N_mg_kg'], dt['P_mg_kg'], dt['K_mg_kg'], dt['pH'], dt['Kelembapan_Persen'], dt['Suhu_Udara']]]
        pred_ai = model_ai.predict(input_val)[0]
        probs = model_ai.predict_proba(input_val)[0]
        st.success(f"Tanaman Disarankan: **{pred_ai}**")
        for i, cls in enumerate(model_ai.classes_):
            st.caption(f"{cls}: {probs[i]*100:.1f}%")
            st.progress(float(probs[i]))

    with col_pakar:
        st.markdown("#### 🎯 Hasil Sistem Pakar")
        tanaman_uji = st.selectbox("Cek Tanaman Lain:", ["Caisim", "Jagung", "Singkong"])
        res = eval_standar[tanaman_uji]
        st.write(f"**Status: {res['status']}**")
        if res['syarat']:
            for s in res['syarat']: st.write(f"⚠️ {s}")
        else: st.write("✅ Lahan sudah optimal.")
    st.divider()

    # ---------------------------------------------------------
    # 4. KALKULATOR BIAYA & DOWNLOAD REPORT (DIPERBAIKI)
    # ---------------------------------------------------------
    st.subheader("💰 Perhitungan Biaya Perbaikan Lahan")
    
    # Hitung luas otomatis dari koordinat jika tersedia
    luas_otomatis = hitung_luas_m2(df['Longitude'].values, df['Latitude'].values) if len(df) >= 3 else 600.0

    with st.expander("⚙️ Konfigurasi Target Unsur Hara & Harga Material", expanded=True):
        st.caption("Masukkan target ideal tanah (mg/kg) dan harga pasar material saat ini.")
        
        # Baris 1: Target pH & NPK
        c1, c2, c3, c4 = st.columns(4)
        target_ph = c1.number_input("Target pH Tanah", value=6.5, step=0.1, help="Skala keasaman ideal")
        target_n = c2.number_input("Target N (mg/kg)", value=40.0, step=1.0)
        target_p = c3.number_input("Target P (mg/kg)", value=20.0, step=1.0)
        target_k = c4.number_input("Target K (mg/kg)", value=30.0, step=1.0)

        st.divider()

        # Baris 2: Harga Material
        h1, h2, h3, h4 = st.columns(4)
        harga_kapur = h1.number_input("Harga Kapur (Rp/kg)", value=5000, step=500)
        harga_urea = h2.number_input("Harga Urea (Rp/kg)", value=10000, step=500)
        harga_sp36 = h3.number_input("Harga SP-36 (Rp/kg)", value=8000, step=500)
        harga_kcl = h4.number_input("Harga KCl (Rp/kg)", value=12000, step=500)

        # Baris 3: Luas Lahan
        luas_input = st.number_input("Luas Lahan Total (m²)", value=int(luas_otomatis))

    # --- EKSEKUSI PERHITUNGAN ---
    total_titik = len(df)
    luas_per_titik = luas_input / total_titik if total_titik > 0 else 0
    
    df_res = df.copy()
    # Memanggil fungsi analisis_presisi_npk dengan parameter lengkap
    hasil = df_res.apply(
        lambda r: analisis_presisi_npk(
            r, luas_per_titik, harga_urea, harga_kapur, harga_sp36, harga_kcl, 
            target_n, target_ph, target_p, target_k
        ), axis=1
    )
    df_res['Rekomendasi'], df_res['Biaya_Rp'] = zip(*hasil)

    # --- MERAPIKAN DESIMAL SEBELUM TAMPIL DI TABEL ---
    df_display = df_res.copy()
    
    # Membulatkan kolom nutrisi (NPK) menjadi 1 angka di belakang koma
    kolom_nutrisi = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg']
    for col in kolom_nutrisi:
        if col in df_display.columns:
            df_display[col] = df_display[col].map('{:,.1f}'.format)
            
    # Membulatkan pH menjadi 2 angka di belakang koma (standar lab)
    if 'pH' in df_display.columns:
        df_display['pH'] = df_display['pH'].map('{:.2f}'.format)

    # Format Biaya tetap dengan separator ribuan (Rp)
    df_display['Biaya_Rp'] = df_display['Biaya_Rp'].apply(lambda x: f"Rp {int(x):,}".replace(',', '.'))
    
    # Mengurutkan Nama_Titik secara alami (T1, T2, dst)
    df_display['sort_val'] = df_display['Nama_Titik'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0)
    df_display = df_display.sort_values('sort_val').drop(columns=['sort_val']).reset_index(drop=True)
    
    # Tampilkan Tabel yang sudah rapi
    st.table(df_display[['Nama_Titik', 'pH', 'N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'Rekomendasi', 'Biaya_Rp']])
    
    # Tombol Download CSV
    csv = df_res.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download Laporan Rekomendasi (CSV)", data=csv, file_name='Laporan_Presisi_Lahan.csv', mime='text/csv')

    # ---------------------------------------------------------
    # 5. REFERENSI STANDAR (Tabel LPT 1984)
    # ---------------------------------------------------------
    with st.expander("📚 Referensi Kriteria Kesuburan Tanah (LPT 1984)"):
        st.write("Penilaian ini didasarkan pada sifat umum tanah secara empiris.")
        data_lpt = {
            "Sifat Tanah": ["C (%)", "N (%)", "P2O5 HCl 25% (mg/100gr)", "K2O HCl 25% (mg/100gr)", "pH (H2O)"],
            "Sangat Rendah": ["< 1.00", "< 0.10", "< 15", "< 10", "< 4.5 (S. Masam)"],
            "Rendah": ["1.00 - 2.00", "0.10 - 0.20", "15 - 20", "10 - 20", "4.5 - 5.5 (Masam)"],
            "Sedang": ["2.01 - 3.00", "0.21 - 0.50", "21 - 40", "21 - 40", "5.6 - 6.5 (Agak Masam)"],
            "Tinggi": ["3.01 - 5.00", "0.51 - 0.75", "41 - 60", "41 - 60", "6.6 - 7.5 (Netral)"],
            "Sangat Tinggi": ["> 5.00", "> 0.75", "> 60", "> 60", "> 8.5 (Alkalis)"]
        }
        st.table(pd.DataFrame(data_lpt))

def tampilkan_tab_3d(df):
    st.subheader("🗺️ Visualisasi Topografi Nutrisi 3D")
    params_3d = {
        'pH': {'col': 'pH', 'color': 'Viridis'},
        'Nitrogen': {'col': 'N_mg_kg', 'color': 'Greens'},
        'Fosfor': {'col': 'P_mg_kg', 'color': 'YlOrRd'},
        'Kalium': {'col': 'K_mg_kg', 'color': 'Purples'}
    }
    pilihan = st.selectbox("Pilih Parameter Visualisasi:", list(params_3d.keys()))
    info = params_3d[pilihan]

    try:
        x, y, z = df['Longitude'].values, df['Latitude'].values, df[info['col']].values
        ux = np.linspace(x.min(), x.max(), 50)
        uy = np.linspace(y.min(), y.max(), 50)
        X_grid, Y_grid = np.meshgrid(ux, uy)
        Z = griddata((x, y), z, (X_grid, Y_grid), method='cubic')
        
        # Logika Hover Titik Terdekat
        tree = KDTree(np.column_stack((x, y)))
        _, indices = tree.query(np.column_stack((X_grid.ravel(), Y_grid.ravel())))
        closest_names = df['Nama_Titik'].values[indices].reshape(X_grid.shape)

        fig = go.Figure(data=[go.Surface(z=Z, x=X_grid, y=Y_grid, customdata=closest_names, colorscale=info['color'],
                                         hovertemplate="<b>Titik: %{customdata}</b><br>Kadar: %{z:.2f}<extra></extra>")])
        fig.update_layout(scene=dict(aspectratio=dict(x=1, y=1, z=0.4)), height=700, margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Gagal merender 3D: {e}")