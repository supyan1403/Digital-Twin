import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

print("Mulai proses Machine Learning...")

# 1. Load data yang udah diklasifikasi
df = pd.read_excel('Dataset_Kriging_Terklasifikasi.xlsx')

# 2. Pisahin Fitur (X) dan Target (y)
# X itu data tanahnya (parameter input)
X = df[['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen']]
# y itu jawaban yang mau ditebak (output)
y = df['Jenis_Komoditas']

# 3. Split data (Bagi jadi data belajar & data ujian)
# 80% buat training (belajar), 20% buat testing (ujian)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Panggil algoritma Random Forest
# n_estimators = 100 artinya kita bikin 100 "pohon keputusan" biar tebakannya akurat
model = RandomForestClassifier(n_estimators=100, random_state=42)

# 5. Training modelnya (ngajarin komputer)
print("Sedang melatih model Random Forest...")
model.fit(X_train, y_train)

# 6. Testing (komputer disuruh nebak data ujian)
y_pred = model.predict(X_test)

# 7. Evaluasi hasil tebakan
akurasi = accuracy_score(y_test, y_pred)
print("=======================================")
print(f"✅ Akurasi Model: {akurasi * 100:.2f}%")
print("=======================================")

# Bonus: tampilin perbandingan hasil tebakan vs jawaban asli
hasil_tes = pd.DataFrame({
    'Jawaban Asli': y_test.values,
    'Tebakan Komputer': y_pred
})
print("\nDetail Tebakan di Data Testing:")
print(hasil_tes)