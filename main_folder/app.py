import streamlit as st
import pandas as pd
import io


from kalkulasi import train_model, konversi_koordinat, hitung_luas_dan_grid
import ui_halaman


st.set_page_config(page_title="Digital Twin Pertanian", layout="wide", page_icon="🌱")

@st.cache_resource
def load_ai_model_v4(): 
    return train_model()


paket_ai = load_ai_model_v4() 
model_ai = paket_ai["model"]
skor_akurasi = paket_ai["akurasi"]

if model_ai is None:
    st.error("Gagal memuat dataset AI. Pastikan 'Dataset_Augmented.xlsx' ada di folder aplikasi.")
    st.stop()






st.sidebar.title("🌱 Digital Twin Engine")


template_data = {
    'Nama_Titik': ['T1', 'T2', 'T3', 'T4', 'T5'],
    'Latitude': ["7°20'31.30\"", "7°20'31.49\"", "", "", ""],
    'Longitude': ["108°2'34.38\"", "108°2'34.29\"", "", "", ""],
    'N_mg_kg': [86.98, 82.33, None, None, None],

    'Status_N': [
        '=IF(D2="","",IF(D2<40,"Rendah",IF(D2<=60,"Sedang","Tinggi")))',
        '=IF(D3="","",IF(D3<40,"Rendah",IF(D3<=60,"Sedang","Tinggi")))',
        '=IF(D4="","",IF(D4<40,"Rendah",IF(D4<=60,"Sedang","Tinggi")))',
        '=IF(D5="","",IF(D5<40,"Rendah",IF(D5<=60,"Sedang","Tinggi")))',
        '=IF(D6="","",IF(D6<40,"Rendah",IF(D6<=60,"Sedang","Tinggi")))'
    ],
    'P_mg_kg': [54.43, 47.03, None, None, None],

    'Status_P': [
        '=IF(F2="","",IF(F2<20,"Rendah",IF(F2<=40,"Sedang","Tinggi")))',
        '=IF(F3="","",IF(F3<20,"Rendah",IF(F3<=40,"Sedang","Tinggi")))',
        '=IF(F4="","",IF(F4<20,"Rendah",IF(F4<=40,"Sedang","Tinggi")))',
        '=IF(F5="","",IF(F5<20,"Rendah",IF(F5<=40,"Sedang","Tinggi")))',
        '=IF(F6="","",IF(F6<20,"Rendah",IF(F6<=40,"Sedang","Tinggi")))'
    ],
    'K_mg_kg': [79.39, 87.02, None, None, None],

    'Status_K': [
        '=IF(H2="","",IF(H2<30,"Rendah",IF(H2<=60,"Sedang","Tinggi")))',
        '=IF(H3="","",IF(H3<30,"Rendah",IF(H3<=60,"Sedang","Tinggi")))',
        '=IF(H4="","",IF(H4<30,"Rendah",IF(H4<=60,"Sedang","Tinggi")))',
        '=IF(H5="","",IF(H5<30,"Rendah",IF(H5<=60,"Sedang","Tinggi")))',
        '=IF(H6="","",IF(H6<30,"Rendah",IF(H6<=60,"Sedang","Tinggi")))'
    ],
    'pH': [6.9, 6.7, None, None, None],
    'Kelembapan_Persen': [74, 71, None, None, None],
    'Suhu_Udara': [23.1, 22.9, None, None, None]
}

df_template = pd.DataFrame(template_data)


excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    df_template.to_excel(writer, index=False, sheet_name='Data_Lahan')
excel_data = excel_buffer.getvalue()


with st.sidebar.expander("📥 Download Template Data", expanded=False):
    st.write("Gunakan file Excel ini. Kolom status akan otomatis terisi saat kamu mengetik angka N, P, dan K.")
    st.download_button(
        label="Download Template .xlsx",
        data=excel_data,
        file_name='Template_Digital_Twin.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )

st.sidebar.divider()


uploaded_file = st.sidebar.file_uploader("Upload Data Lahan (Excel/CSV)", type=['xlsx', 'csv'])


if uploaded_file:

    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:

        df = pd.read_csv(uploaded_file, sep=None, engine='python')
        
    df = df.sort_values(by=['Longitude', 'Latitude'], ascending=[True, False]).reset_index(drop=True)
    df = df.sort_values(by=['Longitude', 'Latitude'], ascending=[True, False]).reset_index(drop=True)
    

    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['Latitude'] = df['Latitude'].apply(lambda x: konversi_koordinat(x, is_lat=True))
        df['Longitude'] = df['Longitude'].apply(lambda x: konversi_koordinat(x, is_lat=False))
        
    luas, p, l = hitung_luas_dan_grid(df)
    

    st.title(f"📊 Dashboard Digital Twin: {uploaded_file.name}")
    
    m3, m4 = st.columns(2)
    m3.metric("Jumlah Titik Sampel", f"{len(df)} Titik")
    m4.metric("Sistem Pakar", "AI & Standar Aktif")
    st.divider()


    tab_data, tab_spasial = st.tabs(["📊 Data Kesuburan", "🗺️ Pemodelan 3D (Kriging)"])


    with tab_data:
        ui_halaman.tampilkan_tab_dashboard(df, model_ai, skor_akurasi)

    with tab_spasial:
        ui_halaman.tampilkan_tab_3d(df)