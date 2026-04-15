import streamlit as st
import pandas as pd

# Import dari modul buatan kita sendiri
from kalkulasi import train_model, konversi_koordinat, hitung_luas_dan_grid
import ui_halaman

# Setup Halaman
st.set_page_config(page_title="Digital Twin Pertanian", layout="wide", page_icon="🌱")

@st.cache_resource
def load_ai_model_v4(): # <--- Ganti jadi v4
    return train_model()

# Panggil fungsi v4
paket_ai = load_ai_model_v4() 
model_ai = paket_ai["model"]
skor_akurasi = paket_ai["akurasi"]

if model_ai is None:
    st.error("Gagal memuat dataset AI. Pastikan 'Dataset_500_Valid.xlsx' ada di folder aplikasi.")
    st.stop()

# ==========================================
# SIDEBAR & PROSES DATA UTAMA
# ==========================================
st.sidebar.title("🌱 Digital Twin Engine")
uploaded_file = st.sidebar.file_uploader("Upload Data Lahan (Excel/CSV)", type=['xlsx', 'csv'])

if uploaded_file:
    # Baca Data
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
    df = df.sort_values(by=['Longitude', 'Latitude'], ascending=[True, False]).reset_index(drop=True)
    
    # Bersihkan Koordinat GPS
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        df['Latitude'] = df['Latitude'].apply(lambda x: konversi_koordinat(x, is_lat=True))
        df['Longitude'] = df['Longitude'].apply(lambda x: konversi_koordinat(x, is_lat=False))
        
    luas, p, l = hitung_luas_dan_grid(df)
    
    # Header Dashboard
    st.title(f"📊 Dashboard Digital Twin: {uploaded_file.name}")
    
    m3, m4 = st.columns(2)
    m3.metric("Jumlah Titik Sampel", f"{len(df)} Titik")
    m4.metric("Sistem Pakar", "AI & Standar Aktif")
    st.divider()

    # Navigasi Tab
    tab_data, tab_spasial = st.tabs(["📊 Data Kesuburan", "🗺️ Pemodelan 3D (Kriging)"])

    # Memanggil tampilan UI dari file sebelah
    with tab_data:
        ui_halaman.tampilkan_tab_dashboard(df, model_ai, skor_akurasi)

    with tab_spasial:
        ui_halaman.tampilkan_tab_3d(df)