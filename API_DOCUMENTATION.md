# ML Platform - API Dokümantasyonu

## Base URL
```
http://localhost:5000/api
```

## Authentication

Tüm kimlik doğrulama gerektiren endpoint'ler için JWT token kullanılır.

Header formatı:
```
Authorization: Bearer <your_jwt_token>
```

---

## Endpoints

### 1. Authentication

#### 1.1 Kullanıcı Kaydı

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Responses:**
- `400`: Email already registered
- `500`: Server error

---

#### 1.2 Kullanıcı Girişi

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-15T10:30:00"
  }
}
```

**Error Responses:**
- `401`: Invalid email or password
- `500`: Server error

---

### 2. Dataset Management

#### 2.1 Dataset Yükleme

**Endpoint:** `POST /dataset/upload`

**Authentication:** Required

**Request (multipart/form-data):**
- `file`: CSV veya Excel dosyası
- `name`: Dataset adı (optional)

**Response (201):**
```json
{
  "message": "Dataset uploaded successfully",
  "dataset": {
    "id": 1,
    "user_id": 1,
    "name": "Iris Dataset",
    "filename": "iris.csv",
    "rows": 150,
    "columns": 5,
    "created_at": "2024-01-15T11:00:00"
  },
  "info": {
    "shape": [150, 5],
    "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
    "dtypes": {
      "sepal_length": "float64",
      "sepal_width": "float64",
      "petal_length": "float64",
      "petal_width": "float64",
      "species": "object"
    },
    "missing_values": {
      "sepal_length": 0,
      "sepal_width": 0,
      "petal_length": 0,
      "petal_width": 0,
      "species": 0
    },
    "duplicates": 0
  }
}
```

**Error Responses:**
- `400`: No file provided / Invalid file type
- `500`: Server error

---

#### 2.2 Dataset Bilgisi

**Endpoint:** `GET /dataset/<dataset_id>`

**Authentication:** Required

**Response (200):**
```json
{
  "dataset": {
    "id": 1,
    "user_id": 1,
    "name": "Iris Dataset",
    "filename": "iris.csv",
    "rows": 150,
    "columns": 5,
    "created_at": "2024-01-15T11:00:00"
  },
  "data": [
    {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2,
      "species": "setosa"
    }
    // ... first 100 rows
  ]
}
```

**Error Responses:**
- `404`: Dataset not found
- `500`: Server error

---

#### 2.3 Dataset Analizi

**Endpoint:** `POST /dataset/<dataset_id>/analyze`

**Authentication:** Required

**Response (200):**
```json
{
  "message": "Analysis completed",
  "statistics": {
    "sepal_length": {
      "mean": 5.843,
      "median": 5.8,
      "std": 0.828,
      "min": 4.3,
      "max": 7.9,
      "q25": 5.1,
      "q75": 6.4
    }
    // ... other numeric columns
  },
  "correlation": {
    "sepal_length": {
      "sepal_length": 1.0,
      "sepal_width": -0.117,
      "petal_length": 0.871,
      "petal_width": 0.817
    }
    // ... correlation matrix
  },
  "info": {
    "shape": [150, 5],
    "columns": ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"],
    "dtypes": {...},
    "missing_values": {...},
    "duplicates": 0
  }
}
```

**Error Responses:**
- `404`: Dataset not found
- `500`: Server error

---

### 3. Model Training

#### 3.1 Model Eğitimi

**Endpoint:** `POST /model/train`

**Authentication:** Required

**Request Body:**
```json
{
  "dataset_id": 1,
  "target_column": "species",
  "model_type": "classification",
  "algorithm": "RandomForest",
  "name": "Iris Classifier",
  "params": {
    "n_estimators": 100,
    "max_depth": 10
  }
}
```

**Parameters:**
- `dataset_id` (required): Dataset ID
- `target_column` (required): Hedef sütun adı
- `model_type` (required): "classification" veya "regression"
- `algorithm` (required): Algoritma adı
- `name` (optional): Model adı
- `params` (optional): Hiperparametreler

**Supported Algorithms:**
- Classification: RandomForest, DecisionTree, LogisticRegression, XGBoost
- Regression: LinearRegression, Ridge, RandomForestRegressor, XGBoostRegressor

**Response (201):**
```json
{
  "message": "Model trained successfully",
  "model": {
    "id": 1,
    "name": "Iris Classifier",
    "algorithm": "RandomForest",
    "dataset_id": 1,
    "accuracy": 0.9666,
    "precision": 0.9677,
    "recall": 0.9666,
    "f1_score": 0.9668,
    "parameters": {
      "n_estimators": 100,
      "max_depth": 10
    },
    "created_at": "2024-01-15T11:30:00"
  },
  "metrics": {
    "accuracy": 0.9666,
    "precision": 0.9677,
    "recall": 0.9666,
    "f1_score": 0.9668
  }
}
```

**For Regression:**
```json
{
  "metrics": {
    "mae": 3.24,
    "mse": 21.89,
    "rmse": 4.67,
    "r2": 0.89
  }
}
```

**Error Responses:**
- `404`: Dataset not found
- `500`: Training error

---

#### 3.2 Model Bilgisi

**Endpoint:** `GET /model/<model_id>`

**Authentication:** Required

**Response (200):**
```json
{
  "model": {
    "id": 1,
    "name": "Iris Classifier",
    "algorithm": "RandomForest",
    "dataset_id": 1,
    "accuracy": 0.9666,
    "precision": 0.9677,
    "recall": 0.9666,
    "f1_score": 0.9668,
    "parameters": {...},
    "created_at": "2024-01-15T11:30:00"
  }
}
```

---

#### 3.3 Tüm Modeller

**Endpoint:** `GET /models`

**Authentication:** Required

**Response (200):**
```json
{
  "models": [
    {
      "id": 1,
      "name": "Iris Classifier",
      "algorithm": "RandomForest",
      "dataset_id": 1,
      "accuracy": 0.9666,
      "created_at": "2024-01-15T11:30:00"
    }
    // ... more models
  ]
}
```

---

### 4. Predictions

#### 4.1 Tahmin Yapma

**Endpoint:** `POST /model/predict`

**Authentication:** Required

**Request Body:**
```json
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

**Response (200):**
```json
{
  "message": "Prediction successful",
  "prediction": {
    "id": 1,
    "model_id": 1,
    "input_data": {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    },
    "result": {
      "prediction": 0,
      "probabilities": [0.95, 0.03, 0.02]
    },
    "created_at": "2024-01-15T12:00:00"
  }
}
```

**For Regression:**
```json
{
  "result": {
    "prediction": 245000.50,
    "probabilities": null
  }
}
```

**Error Responses:**
- `404`: Model not found
- `500`: Prediction error

---

#### 4.2 Model Tahmin Geçmişi

**Endpoint:** `GET /predictions/<model_id>`

**Authentication:** Required

**Response (200):**
```json
{
  "predictions": [
    {
      "id": 1,
      "model_id": 1,
      "input_data": {...},
      "result": {...},
      "created_at": "2024-01-15T12:00:00"
    }
    // ... more predictions
  ]
}
```

---

### 5. Health Check

#### 5.1 Sistem Durumu

**Endpoint:** `GET /health`

**Authentication:** Not required

**Response (200):**
```json
{
  "status": "healthy",
  "service": "ML Platform API"
}
```

---

## Error Responses

Tüm error response'lar şu formatta döner:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes:**
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `500`: Internal Server Error

---

## Rate Limiting

Şu anda rate limiting uygulanmamıştır. Gelecek versiyonlarda eklenecektir.

---

## Example Usage (cURL)

### Kullanıcı Kaydı ve Giriş
```bash
# Kayıt
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "password": "pass123"}'

# Giriş
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com", "password": "pass123"}'
```

### Dataset Yükleme
```bash
curl -X POST http://localhost:5000/api/dataset/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@iris.csv" \
  -F "name=Iris Dataset"
```

### Model Eğitimi
```bash
curl -X POST http://localhost:5000/api/model/train \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": 1,
    "target_column": "species",
    "model_type": "classification",
    "algorithm": "RandomForest"
  }'
```

### Tahmin
```bash
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

## WebSocket Support (Gelecek)

Gerçek zamanlı eğitim güncellemeleri için WebSocket desteği gelecek versiyonlarda eklenecektir.

---

## Changelog

### v1.0.0 (2024-01-15)
- İlk stabil sürüm
- Temel CRUD operasyonları
- ML model eğitimi ve tahmin
- JWT authentication
- PostgreSQL ve MongoDB desteği
