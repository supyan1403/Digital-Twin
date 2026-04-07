import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# load data buat ngelatih AI
df = pd.read_excel('Dataset_Kriging_Terklasifikasi.xlsx')

# tentuin input (fitur) dan output (target)
X = df[['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen']]
y = df['Jenis_Komoditas']

# inisialisasi model RF
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y) # AI belajar dari semua data di excel

print("-" * 30)
print(" SISTEM PREDIKSI KOMODITAS ")
print("-" * 30)

# minta input dari user via terminal``
try:
    n = float(input("Input Nitrogen (N) : "))
    p = float(input("Input Fosfor (P)   : "))
    k = float(input("Input Kalium (K)   : "))
    ph = float(input("Input pH Tanah     : "))
    h = float(input("Input Kelembapan   : "))

    # bungkus inputan ke dataframe biar bisa dibaca model
    data_baru = pd.DataFrame([[n, p, k, ph, h]], 
                             columns=['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen'])

    # eksekusi prediksi
    hasil = model.predict(data_baru)

    print("\n>>> HASIL REKOMENDASI AI: " + hasil[0].upper() + " <<<")
    print("-" * 30)

except ValueError:
    print("Masukin angka aja bro, jangan huruf!")