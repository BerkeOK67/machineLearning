# Proje 3: Akıllı Veri Analitiği ve Makine Öğrenmesi Uygulaması

## 1. Proje Tanımı

Bu proje, farklı programlama dilleri ve bulut teknolojileri kullanılarak büyük veri analizi, makine öğrenmesi modeli geliştirme, model eğitimi ve bulut ortamında dağıtım süreçlerini kapsayan uçtan uca bir veri analitiği platformunun geliştirilmesini amaçlamaktadır.

Sistem, kullanıcıların veri yükleyebilmesini, verileri analiz edebilmesini, makine öğrenmesi modelleri oluşturabilmesini ve tahmin sonuçlarını görüntüleyebilmesini sağlayacaktır.

---

# 2. Proje Amaçları

* Veri toplama ve işleme süreçlerini otomatikleştirmek
* Büyük veri kümelerinden anlamlı bilgiler elde etmek
* Makine öğrenmesi modelleri geliştirmek
* Bulut üzerinde model eğitmek
* Model performanslarını değerlendirmek
* Gerçek zamanlı tahminler sunmak
* REST API üzerinden tahmin servisleri sağlamak

---

# 3. Kullanılacak Teknolojiler

## Backend Teknolojileri

| Teknoloji | Kullanım Amacı                        |
| --------- | ------------------------------------- |
| Python    | Veri analizi ve model geliştirme      |
| .NET      | API geliştirme ve ML.NET              |
| Java      | Veri madenciliği ve Weka entegrasyonu |
| Node.js   | Gerçek zamanlı servisler              |
| PHP       | Yönetim paneli                        |

---

## Makine Öğrenmesi

* Scikit-learn
* TensorFlow
* PyTorch
* ML.NET
* Weka

---

## Veritabanları

### PostgreSQL

* Kullanıcı bilgileri
* Model kayıtları
* Tahmin geçmişleri

### MongoDB

* Ham veri setleri
* Analiz sonuçları

### BigQuery

* Büyük veri analizi
* Veri ambarı

---

## Bulut Platformları

### AWS

* SageMaker
* Lambda
* S3
* API Gateway

### Azure

* Azure Machine Learning
* Cognitive Services

### Google Cloud

* BigQuery
* Vertex AI

---

# 4. Sistem Mimarisi

```text
                +----------------+
                |    Kullanıcı   |
                +--------+-------+
                         |
                         v
                +----------------+
                |  Web Arayüzü   |
                +--------+-------+
                         |
      +------------------+------------------+
      |                  |                  |
      v                  v                  v

+------------+   +-------------+   +-------------+
| Python API |   | .NET API    |   | Node.js API |
+------+-----+   +------+------|   +------+------+
       |                |                |
       +----------------+----------------+
                        |
                        v
               +----------------+
               | Veri Katmanı   |
               +----------------+
                 |          |
                 v          v
            PostgreSQL   MongoDB
                 |
                 v
              BigQuery
                 |
                 v
        Bulut ML Servisleri
```

---

# 5. Fonksiyonel Gereksinimler

## Veri Yönetimi

### Kullanıcı

* Veri yükleyebilmeli
* CSV dosyası seçebilmeli
* Excel dosyası yükleyebilmeli

### Sistem

* Veriyi doğrulamalı
* Eksik verileri tespit etmeli
* Veri temizleme yapmalı

---

## Veri Analizi

Sistem aşağıdaki analizleri gerçekleştirebilmelidir:

* Ortalama
* Medyan
* Standart sapma
* Korelasyon analizi
* Dağılım grafikleri
* Özellik seçimi

---

## Makine Öğrenmesi

### Sınıflandırma

* Random Forest
* Decision Tree
* Logistic Regression
* XGBoost

### Regresyon

* Linear Regression
* Ridge Regression
* Random Forest Regressor

### Derin Öğrenme

* Yapay Sinir Ağları
* CNN
* LSTM

---

# 6. Veri Akışı

1. Kullanıcı veri yükler
2. Veri MongoDB'ye kaydedilir
3. Temizleme işlemleri yapılır
4. Özellik mühendisliği uygulanır
5. Model eğitilir
6. Sonuçlar değerlendirilir
7. Model kayıt altına alınır
8. Tahmin servisi aktif edilir

---

# 7. API Tasarımı

## Veri Yükleme

```http
POST /api/dataset/upload
```

### Request

```json
{
  "file": "dataset.csv"
}
```

---

## Model Eğitme

```http
POST /api/model/train
```

### Request

```json
{
  "algorithm": "RandomForest",
  "datasetId": 1
}
```

---

## Tahmin Alma

```http
POST /api/model/predict
```

### Request

```json
{
  "modelId": 10,
  "data": {
    "age": 25,
    "salary": 5000
  }
}
```

---

# 8. Veritabanı Tasarımı

## Users

```sql
CREATE TABLE Users(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(100),
    PasswordHash TEXT
);
```

## Models

```sql
CREATE TABLE Models(
    Id SERIAL PRIMARY KEY,
    Name VARCHAR(100),
    Algorithm VARCHAR(50),
    Accuracy FLOAT,
    CreatedAt TIMESTAMP
);
```

## Predictions

```sql
CREATE TABLE Predictions(
    Id SERIAL PRIMARY KEY,
    ModelId INT,
    InputData JSON,
    Result JSON,
    CreatedAt TIMESTAMP
);
```

---

# 9. Makine Öğrenmesi Süreci

## Veri Ön İşleme

* Eksik veri tamamlama
* Normalizasyon
* Standardizasyon
* Label Encoding
* One Hot Encoding

## Eğitim

Veriler:

* %80 Eğitim
* %20 Test

olarak ayrılacaktır.

## Değerlendirme

Sınıflandırma:

* Accuracy
* Precision
* Recall
* F1 Score

Regresyon:

* MAE
* MSE
* RMSE
* R²

---

# 10. Bulut Entegrasyonu

## AWS

### S3

* Veri depolama

### SageMaker

* Model eğitme

### Lambda

* Tahmin servisi

---

## Azure

### Azure ML

* Eğitim
* Deployment

### Cognitive Services

* Veri zenginleştirme

---

## Google Cloud

### BigQuery

* Büyük veri analizi

### Vertex AI

* Model dağıtımı

---

# 11. Güvenlik Gereksinimleri

* JWT Authentication
* Role Based Authorization
* HTTPS
* Veri şifreleme
* API Rate Limiting
* Audit Logging

---

# 12. Performans Gereksinimleri

* Veri yükleme süresi < 5 saniye
* Tahmin süresi < 2 saniye
* API yanıt süresi < 500 ms
* Aynı anda 100+ kullanıcı desteği

---

# 13. Test Senaryoları

## Birim Testler

* Veri yükleme
* Model eğitimi
* Tahmin alma

## Entegrasyon Testleri

* Veritabanı bağlantıları
* Bulut servisleri
* API servisleri

## Performans Testleri

* Yük testi
* Stres testi
* Ölçeklenebilirlik testi

---

# 14. Teslim Edilecek Çıktılar

* Kaynak kodları
* API dokümantasyonu
* Veritabanı şeması
* Makine öğrenmesi modelleri
* Docker dosyaları
* Deployment dokümantasyonu
* Kullanıcı kılavuzu

---

# 15. Geliştirme Takvimi

## Faz 1

* Gereksinim analizi
* Mimari tasarım

## Faz 2

* Veritabanı geliştirme
* API geliştirme

## Faz 3

* Veri analizi modülü
* Makine öğrenmesi modülü

## Faz 4

* Bulut entegrasyonu
* Model deployment

## Faz 5

* Testler
* Optimizasyon

## Faz 6

* Dokümantasyon
* Final teslimi

---

# Beklenen Sonuç

Sistem, kullanıcıların veri yükleyerek otomatik analiz yapabildiği, makine öğrenmesi modelleri oluşturabildiği, bulut üzerinde eğitip dağıtabildiği ve gerçek zamanlı tahminler alabileceği tam kapsamlı bir Akıllı Veri Analitiği ve Makine Öğrenmesi Platformu olacaktır.
