# Akıllı Veri Analitiği ve Makine Öğrenmesi Platformu

Bu proje, veri yükleme, analiz, makine öğrenmesi modeli eğitimi ve tahmin yapma özelliklerine sahip tam kapsamlı bir ML platformudur.

## 🚀 Özellikler

- **Veri Yönetimi**: CSV ve Excel dosyalarını yükleme ve saklama
- **Veri Analizi**: İstatistiksel analiz, korelasyon matrisi, eksik veri tespiti
- **Makine Öğrenmesi**: 
  - Sınıflandırma: Random Forest, Decision Tree, Logistic Regression, XGBoost
  - Regresyon: Linear Regression, Ridge, Random Forest Regressor
- **Model Değerlendirme**: Accuracy, Precision, Recall, F1-Score, R², RMSE
- **Gerçek Zamanlı Tahminler**: REST API üzerinden tahmin servisi
- **Kullanıcı Yönetimi**: JWT tabanlı kimlik doğrulama

## 🛠️ Teknolojiler

### Backend
- **Python Flask**: Ana API servisi
- **PostgreSQL**: İlişkisel veritabanı (kullanıcılar, modeller, tahminler)
- **MongoDB**: NoSQL veritabanı (ham veri setleri)
- **Scikit-learn**: Makine öğrenmesi algoritmaları
- **XGBoost**: Gradient boosting
- **Pandas & NumPy**: Veri işleme

### Frontend
- **HTML/CSS/JavaScript**: Modern web arayüzü
- **REST API**: Backend iletişimi

### Infrastructure
- **Docker & Docker Compose**: Konteynerizasyon
- **SQLAlchemy**: ORM

## 📋 Gereksinimler

- Docker ve Docker Compose
- Python 3.11+
- PostgreSQL 15+
- MongoDB 7+

## 🔧 Kurulum

### 1. Repository'i Klonlayın

```bash
git clone <repository-url>
cd makine-ogrenmesi
```

### 2. Docker ile Çalıştırın

```bash
docker-compose up -d
```

Bu komut şunları başlatacaktır:
- PostgreSQL (Port: 5432)
- MongoDB (Port: 27017)
- Python Flask API (Port: 5000)

### 3. Manuel Kurulum (Opsiyonel)

#### Backend Kurulumu

```bash
cd backend/python_api
pip install -r requirements.txt

# .env dosyasını oluşturun
cp .env.example .env

# Veritabanını başlatın
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Uygulamayı çalıştırın
python app.py
```

#### Frontend

```bash
# Frontend dizinine gidin
cd frontend

# index.html dosyasını bir web sunucusu ile açın
# Örnek: Live Server (VS Code extension) kullanabilirsiniz
```

## 📚 API Dokümantasyonu

### Kimlik Doğrulama

#### Kayıt Ol
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}
```

#### Giriş Yap
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

### Veri Yönetimi

#### Veri Yükle
```http
POST /api/dataset/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <csv/excel file>
name: "Dataset Adı"
```

#### Veriyi Analiz Et
```http
POST /api/dataset/<id>/analyze
Authorization: Bearer <token>
```

### Model Eğitimi

#### Model Eğit
```http
POST /api/model/train
Authorization: Bearer <token>
Content-Type: application/json

{
  "dataset_id": 1,
  "target_column": "target",
  "model_type": "classification",
  "algorithm": "RandomForest",
  "name": "My Model"
}
```

#### Modelleri Listele
```http
GET /api/models
Authorization: Bearer <token>
```

### Tahmin

#### Tahmin Yap
```http
POST /api/model/predict
Authorization: Bearer <token>
Content-Type: application/json

{
  "model_id": 1,
  "data": {
    "feature1": 5.1,
    "feature2": 3.5,
    "feature3": 1.4
  }
}
```

## 🎯 Kullanım Senaryoları

### 1. Iris Dataset ile Sınıflandırma

```python
# 1. Dataset yükle (iris.csv)
# 2. Veriyi analiz et
# 3. Model eğit:
{
  "dataset_id": 1,
  "target_column": "species",
  "model_type": "classification",
  "algorithm": "RandomForest"
}
# 4. Tahmin yap:
{
  "model_id": 1,
  "data": {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }
}
```

### 2. Ev Fiyat Tahmini (Regresyon)

```python
# 1. Dataset yükle (housing.csv)
# 2. Model eğit:
{
  "dataset_id": 2,
  "target_column": "price",
  "model_type": "regression",
  "algorithm": "RandomForestRegressor"
}
# 3. Tahmin yap
```

## 📊 Desteklenen Algoritmalar

### Sınıflandırma
- Random Forest Classifier
- Decision Tree Classifier
- Logistic Regression
- XGBoost Classifier

### Regresyon
- Linear Regression
- Ridge Regression
- Random Forest Regressor
- XGBoost Regressor

## 🔒 Güvenlik

- JWT tabanlı kimlik doğrulama
- Şifreler hash'lenerek saklanır (Werkzeug)
- CORS koruması
- Dosya tipi doğrulama
- Maksimum dosya boyutu limiti (16MB)

## 📈 Performans Metrikleri

### Sınıflandırma
- Accuracy (Doğruluk)
- Precision (Kesinlik)
- Recall (Duyarlılık)
- F1 Score

### Regresyon
- MAE (Mean Absolute Error)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)
- R² Score

## 🗂️ Proje Yapısı

```
makine-ogrenmesi/
├── backend/
│   ├── python_api/
│   │   ├── app.py              # Ana Flask uygulaması
│   │   ├── config.py           # Konfigürasyon
│   │   ├── models.py           # Database modelleri
│   │   ├── mongo_db.py         # MongoDB helper
│   │   ├── data_processor.py   # Veri işleme
│   │   ├── ml_trainer.py       # ML eğitim
│   │   ├── requirements.txt    # Python bağımlılıkları
│   │   └── Dockerfile
│   ├── dotnet_api/             # .NET API (gelecek)
│   └── node_api/               # Node.js API (gelecek)
├── frontend/
│   ├── index.html              # Ana sayfa
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── database/
│   └── schema.sql              # PostgreSQL şeması
├── docker-compose.yml          # Docker orchestration
└── README.md
```

## 🧪 Test

```bash
# API health check
curl http://localhost:5000/api/health

# Test kullanıcısı ile giriş
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@mlplatform.com", "password": "admin123"}'
```

## 🚧 Gelecek Geliştirmeler

- [ ] .NET API entegrasyonu (ML.NET)
- [ ] Node.js gerçek zamanlı servisler
- [ ] AWS SageMaker entegrasyonu
- [ ] Azure ML entegrasyonu
- [ ] Google Cloud Vertex AI
- [ ] Derin öğrenme modelleri (CNN, LSTM)
- [ ] Model versiyonlama
- [ ] A/B testing
- [ ] Otomatik hiperparametre optimizasyonu
- [ ] Dashboard grafikleri (Chart.js)
- [ ] Model performans karşılaştırması

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push edin (`git push origin feature/AmazingFeature`)
5. Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👥 İletişim

Proje Sahibi - [E-posta]

Proje Linki: [GitHub Repository]

## 🙏 Teşekkürler

- Scikit-learn
- Flask
- PostgreSQL
- MongoDB
- Docker
