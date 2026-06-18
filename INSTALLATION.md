# Makine Öğrenmesi Platform Kurulum ve Çalıştırma Kılavuzu

## Hızlı Başlangıç

### 1. Docker ile Çalıştırma (Önerilen)

```bash
# Projeyi klonlayın
cd makine-ogrenmesi

# Docker container'ları başlatın
docker-compose up -d

# Logları kontrol edin
docker-compose logs -f

# Container'ları durdurun
docker-compose down
```

Servisler:
- Python API: http://localhost:5000
- PostgreSQL: localhost:5432
- MongoDB: localhost:27017
- Frontend: frontend/index.html dosyasını tarayıcıda açın

---

### 2. Manuel Kurulum

#### Gereksinimler
- Python 3.11+
- PostgreSQL 15+
- MongoDB 7+
- pip

#### Adımlar

**PostgreSQL Kurulumu:**
```bash
# PostgreSQL'i başlatın
# Windows: PostgreSQL servisini başlatın
# Linux/Mac: sudo service postgresql start

# Veritabanını oluşturun
psql -U postgres
CREATE DATABASE ml_platform;
\q

# Şemayı yükleyin
psql -U postgres -d ml_platform -f database/schema.sql
```

**MongoDB Kurulumu:**
```bash
# MongoDB'yi başlatın
# Windows: MongoDB servisini başlatın
# Linux/Mac: sudo service mongod start
```

**Python Backend:**
```bash
cd backend/python_api

# Virtual environment oluşturun
python -m venv venv

# Virtual environment'ı aktifleştirin
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# .env dosyasını oluşturun
copy .env.example .env  # Windows
# VEYA
cp .env.example .env    # Linux/Mac

# .env dosyasını düzenleyin (veritabanı bilgilerini güncelleyin)

# Uygulamayı çalıştırın
python app.py
```

**Frontend:**
```bash
cd frontend

# index.html dosyasını bir web sunucusu ile açın
# VS Code kullanıyorsanız: Live Server extension ile açın
# Python ile basit sunucu:
python -m http.server 8080

# Tarayıcıda açın: http://localhost:8080
```

---

## Test Etme

### API Test Script

```bash
# Backend dizininde
cd backend/python_api

# Test scriptini çalıştırın (oluşturulacak)
python test_api.py
```

### Manuel Test (cURL)

```bash
# Health check
curl http://localhost:5000/api/health

# Kullanıcı kaydı
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@test.com", "password": "test123"}'

# Giriş
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123"}'
```

---

## Örnek Veri Seti ile Test

### 1. Iris Dataset

```bash
# Iris dataset'i indirin
# https://archive.ics.uci.edu/ml/machine-learning-databases/iris/iris.data

# Dataset'i yükleyin (Frontend üzerinden veya API ile)
curl -X POST http://localhost:5000/api/dataset/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@iris.csv" \
  -F "name=Iris Dataset"

# Model eğitin
curl -X POST http://localhost:5000/api/model/train \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "target_column": "species",
    "model_type": "classification",
    "algorithm": "RandomForest"
  }'

# Tahmin yapın
curl -X POST http://localhost:5000/api/model/predict \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": 1,
    "data": {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    }
  }'
```

---

## Sorun Giderme

### PostgreSQL Bağlantı Hatası

```bash
# Bağlantıyı test edin
psql -U postgres -d ml_platform

# Servisin çalıştığını kontrol edin
# Windows: services.msc
# Linux: sudo service postgresql status
```

### MongoDB Bağlantı Hatası

```bash
# MongoDB'yi test edin
mongosh

# Servisi kontrol edin
# Linux: sudo service mongod status
```

### Port Kullanımda Hatası

```bash
# Port'u kontrol edin
# Windows:
netstat -ano | findstr :5000
# Linux/Mac:
lsof -i :5000

# Kullanımda olan process'i sonlandırın
```

### Docker Container Hataları

```bash
# Container'ları yeniden başlatın
docker-compose down
docker-compose up -d --build

# Logları kontrol edin
docker-compose logs python_api
docker-compose logs postgres
docker-compose logs mongodb

# Container içine girin
docker exec -it ml_platform_python_api bash
```

### Pip Bağımlılık Hataları

```bash
# Cache'i temizleyin
pip cache purge

# Bağımlılıkları tekrar yükleyin
pip install -r requirements.txt --force-reinstall

# Spesifik paketler için:
pip install tensorflow==2.15.0 --force-reinstall
```

---

## Geliştirme Modu

### Hot Reload

Flask uygulaması development modunda otomatik olarak yeniden yüklenir:

```bash
# .env dosyasında
FLASK_ENV=development
```

### Debug Mode

```python
# app.py'de
app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## Production Deployment

### Güvenlik

1. `.env` dosyasındaki tüm şifreleri değiştirin
2. `SECRET_KEY` ve `JWT_SECRET_KEY` değerlerini güçlü yapın
3. HTTPS kullanın
4. Rate limiting ekleyin
5. CORS ayarlarını düzenleyin

### Performans

1. Gunicorn veya uWSGI kullanın:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. Nginx reverse proxy kurun
3. Redis caching ekleyin
4. Database connection pooling aktifleştirin

---

## Destek

Herhangi bir sorun yaşarsanız:
1. Logları kontrol edin
2. GitHub Issues'da arayın
3. Yeni issue açın

---

## Yararlı Komutlar

```bash
# Docker
docker-compose ps                    # Running containers
docker-compose logs -f python_api    # API logs
docker-compose restart python_api    # Restart API
docker-compose down -v               # Remove all including volumes

# Database
psql -U postgres -d ml_platform     # PostgreSQL shell
mongosh ml_platform                 # MongoDB shell

# Python
pip freeze > requirements.txt       # Update requirements
pip list --outdated                 # Check for updates
python -m pytest                    # Run tests

# Git
git status                          # Check status
git add .                           # Stage all changes
git commit -m "message"             # Commit
git push                            # Push to remote
```
