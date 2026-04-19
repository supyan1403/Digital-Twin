import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from scipy.interpolate import griddata
from scipy.spatial import KDTree
from kalkulasi import hitung_luas_m2, konversi_koordinat, analisis_presisi_npk, generate_pdf_report, evaluasi_standar_pertanian

def tampilkan_tab_dashboard(df, model_ai, skor_akurasi):



    st.subheader("📊 Ringkasan Kondisi Lahan")

    avg_ph = df['pH'].mean()
    avg_n = df['N_mg_kg'].mean()
    avg_p = df['P_mg_kg'].mean()
    avg_k = df['K_mg_kg'].mean()
    avg_hum = df['Kelembapan_Persen'].mean()
    avg_temp = df['Suhu_Udara'].mean()


    c_m1, c_m2, c_m3, c_m4 = st.columns(4)
    c_m1.metric("Rerata pH", f"{avg_ph:.2f}", delta="- Asam" if avg_ph < 6 else "Normal")
    c_m2.metric("Rerata Nitrogen (N)", f"{avg_n:.1f} mg/kg")
    c_m3.metric("Rerata Fosfor (P)", f"{avg_p:.1f} mg/kg")
    c_m4.metric("Rerata Kalium (K)", f"{avg_k:.1f} mg/kg")


    c_m5, c_m6, c_m7, c_m8 = st.columns(4)
    c_m5.metric("Rerata Kelembapan", f"{avg_hum:.1f}%")
    c_m6.metric("Rerata Suhu Udara", f"{avg_temp:.1f}°C")
    c_m7.metric("Akurasi AI", f"{skor_akurasi:.1f}%")
    c_m8.metric("Total Titik Sampel", len(df))

    st.divider()




    st.subheader("🌍 Lokasi Fisik (Google Satellite)")
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=19, max_zoom=22, tiles=None)
    folium.TileLayer(tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google', name='Google Satellite', max_zoom=22).add_to(m)

    for i, row in df.iterrows():
        label_titik = row['Nama_Titik'] if 'Nama_Titik' in df.columns else f"T{i+1}"
        folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=6, color='yellow', fill=True, fill_color='red', fill_opacity=0.9).add_to(m)
        folium.Marker(location=[row['Latitude'], row['Longitude']], icon=folium.DivIcon(icon_size=(150,36), icon_anchor=(7, 20), html=f'<div style="font-size: 10pt; color: white; font-weight: bold; text-shadow: 2px 2px 4px #000;">{label_titik}</div>')).add_to(m)
    st_folium(m, width=1200, height=450)
    st.divider()




    st.subheader("💡 Analisis & Keputusan SPK")
    

    titik_list = df['Nama_Titik'].unique().tolist()
    


    import re
    titik_list.sort(key=lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0)
    

    titik_terpilih = st.selectbox("📍 Pilih ID Titik untuk Dianalisis:", titik_list)

    if 'Nama_Titik' in df.columns:
        dt = df[df['Nama_Titik'] == titik_terpilih].iloc[0]
    else:
        idx = int(titik_terpilih.replace("T", "")) - 1
        dt = df.iloc[idx]
    

    st.markdown(f"#### 🔎 Data Aktual: {titik_terpilih}")
    d1, d2, d3, d4 = st.columns(4)
    

    d1.metric("Nitrogen (N)", f"{dt['N_mg_kg']:.1f} mg/kg")
    d2.metric("Fosfor (P)", f"{dt['P_mg_kg']:.1f} mg/kg")
    d3.metric("Kalium (K)", f"{dt['K_mg_kg']:.1f} mg/kg")
    d4.metric("Keasaman (pH)", f"{dt['pH']:.2f}")
    
    st.divider()

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







    luas_otomatis = hitung_luas_m2(df['Longitude'].values, df['Latitude'].values) if len(df) >= 3 else 600.0

    with st.expander("⚙️ Konfigurasi Target Unsur Hara & Harga Material", expanded=True):
        st.write("Pilih preset tanaman untuk memuat target hara otomatis.")
        

        preset_tanaman = {
            "Custom (Input Manual)": {"n": 40.0, "p": 20.0, "k": 30.0, "ph_min": 6.0, "ph_max": 7.0},
            "Caisim": {"n": 40.0, "p": 20.0, "k": 20.0, "ph_min": 6.0, "ph_max": 7.0},
            "Jagung": {"n": 60.0, "p": 40.0, "k": 30.0, "ph_min": 5.8, "ph_max": 7.8},
            "Singkong": {"n": 40.0, "p": 20.0, "k": 40.0, "ph_min": 5.2, "ph_max": 7.0}
        }
        
        pilihan_preset = st.selectbox("🌱 Pilih Preset Komoditas Tanaman:", list(preset_tanaman.keys()),index=1)
        data_preset = preset_tanaman[pilihan_preset]
        
        c1, c2, c3, c4 = st.columns(4)

        target_ph_min, target_ph_max = c1.slider("Target Rentang pH", min_value=4.0, max_value=9.0, value=(data_preset["ph_min"], data_preset["ph_max"]), step=0.1)
        target_n = c2.number_input("Target N (mg/kg)", value=data_preset["n"], step=1.0)
        target_p = c3.number_input("Target P (mg/kg)", value=data_preset["p"], step=1.0)
        target_k = c4.number_input("Target K (mg/kg)", value=data_preset["k"], step=1.0)

        st.divider()
        h1, h2, h3, h4 = st.columns(4)
        harga_kapur = h1.number_input("Harga Kapur", value=5000)
        harga_urea = h2.number_input("Harga Urea", value=10000)
        harga_sp36 = h3.number_input("Harga SP-36", value=8000)
        harga_kcl = h4.number_input("Harga KCl", value=12000)
        luas_input = st.number_input("Luas Lahan (m²)", value=int(luas_otomatis))


    total_titik = len(df)
    luas_per_titik = luas_input / total_titik if total_titik > 0 else 0
    df_res = df.copy()
    hasil = df_res.apply(lambda r: analisis_presisi_npk(r, luas_per_titik, harga_urea, harga_kapur, harga_sp36, harga_kcl, target_n, target_ph_min, target_ph_max, target_p, target_k), axis=1)
    df_res['Rekomendasi'], df_res['Biaya_Rp'] = zip(*hasil)

    df_res['sort_val'] = df_res['Nama_Titik'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0)
    df_res = df_res.sort_values('sort_val').drop(columns=['sort_val']).reset_index(drop=True)


    df_display = df_res.copy()
    

    kolom_nutrisi = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg']
    for col in kolom_nutrisi:
        if col in df_display.columns:
            df_display[col] = df_display[col].map('{:,.1f}'.format)
            

    if 'pH' in df_display.columns:
        df_display['pH'] = df_display['pH'].map('{:.2f}'.format)


    df_display['Biaya_Rp'] = df_display['Biaya_Rp'].apply(lambda x: f"Rp {int(x):,}".replace(',', '.'))
    

    df_display['sort_val'] = df_display['Nama_Titik'].apply(lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0)
    df_display = df_display.sort_values('sort_val').drop(columns=['sort_val']).reset_index(drop=True)
    

    st.subheader("📋 Laporan Detail Keseluruhan Lahan")
    

    with st.expander("Lihat Detail Tabel Rekomendasi Per Titik", expanded=False):
        st.table(df_display[['Nama_Titik', 'pH', 'N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'Rekomendasi', 'Biaya_Rp']].set_index('Nama_Titik'))
    

        total_biaya = df_res['Biaya_Rp'].sum()
        st.markdown(f"### 💰 Total Estimasi Biaya Perbaikan: **Rp {int(total_biaya):,}".replace(',', '.') + "**")

        total_biaya = df_res['Biaya_Rp'].sum()
    

    pdf_bytes = generate_pdf_report(df_res, total_biaya, pilihan_preset)
    
    st.download_button(
        label="📄 Download Laporan Rekomendasi (PDF)",
        data=pdf_bytes,
        file_name=f"Laporan_Pupuk_{pilihan_preset}.pdf",
        mime="application/pdf"
    )

    csv = df_res.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Download Laporan Rekomendasi (CSV)", data=csv, file_name='Laporan_Presisi_Lahan.csv', mime='text/csv')


    st.subheader("📊 Perbandingan Biaya Perbaikan per Titik")
    
    fig_biaya = go.Figure(data=[
        go.Bar(
            x=df_res['Nama_Titik'], 
            y=df_res['Biaya_Rp'],
            marker_color='rgb(55, 83, 109)',
            hovertemplate="<b>Titik %{x}</b><br>Biaya: Rp %{y:,.0f}<extra></extra>"
        )
    ])
    
    fig_biaya.update_layout(
        xaxis_title="ID Titik Sampel",
        yaxis_title="Estimasi Biaya (Rp)",
        template="plotly_white",
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    
    
    st.plotly_chart(fig_biaya, use_container_width=True)
    




    with st.expander("📚 Referensi Kriteria Kesuburan Tanah (LPT 1984)"):
        st.write("Penilaian ini didasarkan pada sifat umum tanah secara empiris.")
        data_lpt = {
            "Sifat Tanah": ["C (%)", "N (%)", "P2O5 HCl 25% (mg/100gr)", "K2O HCl 25% (mg/100gr)", "pH (H2O)"],
            "Sangat Rendah": ["< 1.00", "< 0.10", "< 15", "< 10", "< 4.5 (S. Masam)"],
            "Rendah": ["1.00 - 2.00", "0.10 - 0.20", "15 - 20", "10 - 20", "4.5 - 5.5 (Masam)"],
            "Sedang": ["2.01 - 3.00", "0.21 - 0.50", "21 - 40", "21 - 40", "5.6 - 6.5 (Agak Masam)"],
            "Tinggi": ["3.01 - 5.00", "0.51 - 0.75", "41 - 60", "41 - 60", "6.6 - 7.5 (Netral)"],
            "Sangat Tinggi": ["\> 5.00", "\> 0.75", "\> 60", "\> 60", "\> 8.5 (Alkalis)"]
        }
        st.table(pd.DataFrame(data_lpt))

    with st.expander("🎯 Referensi Kriteria Target Tanaman (Sistem Digital Twin)"):
        st.write("Status kesuburan pada sistem ini didasarkan pada Target Kebutuhan Nutrisi Tanaman yang dapat diatur.")
        

        data_kriteria_sistem = {
            "Unsur Hara (mg/kg)": ["Nitrogen (N)", "Fosfor (P)", "Kalium (K)"],
            "Rendah (Defisit)": ["< 40", "< 20", "< 30"],
            "Sedang (Mendekati Optimal)": ["40 - 60", "20 - 40", "30 - 60"],
            "Tinggi (Optimal)": ["\> 60", "\> 40", "\> 60"] 
        }
        
        df_kriteria = pd.DataFrame(data_kriteria_sistem)

        st.table(df_kriteria.set_index("Unsur Hara (mg/kg)"))
        
        st.info("""
        **💡 Penjelasan Logika Sistem:**
        Sistem menghitung nilai gap (selisih) antara data lapangan dengan target yang ditentukan. Jika nilai lapangan sudah melebihi target (contoh: N > 60 mg/kg), maka lahan diklasifikasikan sebagai **Tinggi/Optimal** sehingga rekomendasi dosis pupuk dapat ditekan menjadi 0 untuk efisiensi biaya.
        """)

def tampilkan_tab_3d(df):
    st.subheader("🗺️ Visualisasi Topografi Nutrisi 3D")
    

    params_3d = {
        'Nitrogen': {'col': 'N_mg_kg', 'color': 'Greens', 'status': 'Status_N'},
        'Fosfor': {'col': 'P_mg_kg', 'color': 'YlOrRd', 'status': 'Status_P'},
        'Kalium': {'col': 'K_mg_kg', 'color': 'Purples', 'status': 'Status_K'},
        'pH': {'col': 'pH', 'color': 'Viridis', 'status': None}
    }
    
    pilihan = st.selectbox("Pilih Parameter Visualisasi:", list(params_3d.keys()))
    info = params_3d[pilihan]

    try:

        df_clean = df.dropna(subset=['Latitude', 'Longitude', info['col'], 'Nama_Titik']).copy()
        
        x = df_clean['Longitude'].values
        y = df_clean['Latitude'].values
        z = df_clean[info['col']].values
        


        ux = np.linspace(x.min(), x.max(), 30)
        uy = np.linspace(y.min(), y.max(), 30)
        X_grid, Y_grid = np.meshgrid(ux, uy)
        
        from scipy.interpolate import griddata

        Z = griddata((x, y), z, (X_grid, Y_grid), method='linear')
        


        

        palet_warna = {'Rendah': 'red', 'Sedang': 'yellow', 'Tinggi': 'green'}
        
        if info['status'] and info['status'] in df_clean.columns:
            warna_titik = df_clean[info['status']].map(palet_warna).fillna('black').tolist()
        else:
            warna_titik = 'black'

        satuan = "" if pilihan == 'pH' else " mg/kg"


        import plotly.graph_objects as go
        trace_surface = go.Surface(
            z=Z, x=X_grid, y=Y_grid, 
            colorscale=info['color'],
            opacity=0.8,
            hovertemplate="<b>Kawasan Estimasi " + pilihan + "</b><br>Nilai: %{z:.2f}" + satuan + "<extra></extra>"
        )



        hover_data_lengkap = np.column_stack((
            df_clean['N_mg_kg'], df_clean['P_mg_kg'], df_clean['K_mg_kg'], df_clean['pH']
        ))
        

        z_offset = z + (z.max() * 0.02)

        trace_titik = go.Scatter3d(
            x=x, y=y, z=z_offset,
            mode='markers+text',
            text=df_clean['Nama_Titik'], 
            customdata=hover_data_lengkap,
            textposition="top center",
            marker=dict(
                size=8, 
                color=warna_titik, 
                line=dict(color='white', width=1)
            ),
            hovertemplate=(
                "<b>📍 Titik Asli: %{text}</b><br>"
                "---------------------<br>"
                "pH: %{customdata[3]:.2f}<br>"
                "N : %{customdata[0]:.1f} mg/kg<br>"
                "P : %{customdata[1]:.1f} mg/kg<br>"
                "K : %{customdata[2]:.1f} mg/kg"
                "<extra></extra>"
            )
        )

        fig = go.Figure(data=[trace_surface, trace_titik])
        

        kamera = dict(eye=dict(x=1.5, y=-1.5, z=1.2))

        fig.update_layout(
            scene=dict(aspectratio=dict(x=1, y=1, z=0.4), camera=kamera),
            height=700, margin=dict(l=0, r=0, b=0, t=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Gagal merender 3D: {e}")