import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt


nama_file = 'Dataset_Augmented.xlsx'
df = pd.read_excel(nama_file)



kolom_fitur = ['N_mg_kg', 'P_mg_kg', 'K_mg_kg', 'pH', 'Kelembapan_Persen', 'Suhu_Udara']
kolom_target = 'Jenis_Komoditas'

X = df[kolom_fitur]
y = df[kolom_target]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)


y_pred = rf_model.predict(X_test)


akurasi = accuracy_score(y_test, y_pred)

print("\n" + "="*50)
print("🏆 HASIL EVALUASI AI: REKOMENDASI KOMODITAS 🏆")
print("="*50)
print(f"Akurasi Prediksi Tanaman : {akurasi * 100:.2f}%\n")
print("Laporan Detail (Caisim, Jagung, Singkong):\n")
print(classification_report(y_test, y_pred, zero_division=0))


cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', 
            xticklabels=rf_model.classes_, yticklabels=rf_model.classes_)
plt.title('Confusion Matrix - Prediksi Rekomendasi Komoditas')
plt.ylabel('Komoditas Asli (Target Ideal)')
plt.xlabel('Rekomendasi AI')
plt.savefig('Confusion_Matrix_Komoditas_Sinta.png', dpi=300, bbox_inches='tight')
print("✅ Grafik berhasil disimpan sebagai 'Confusion_Matrix_Komoditas_Sinta.png'")
plt.show()