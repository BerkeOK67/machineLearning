# AWS Kurulum Kılavuzu

Bu kılavuz, ML Platform'un AWS (S3 + SageMaker) ile bulut eğitimi ve dağıtımını nasıl kullanacağınızı anlatır.

## Mimari

```
Frontend → Flask API → S3 (veri + model)
                    → SageMaker Training Job (eğitim)
                    → SageMaker Endpoint (tahmin)
```

## 1. AWS Hesabı Hazırlığı

### Gerekli servisler
- **Amazon S3** — veri setleri ve model dosyaları
- **Amazon SageMaker** — model eğitimi ve endpoint
- **IAM** — erişim rolleri

### S3 Bucket oluşturma
1. AWS Console → S3 → Create bucket
2. Bucket adı: `ml-platform-datasets-YOURNAME` (global benzersiz olmalı)
3. Region: `us-east-1` (veya tercih ettiğiniz bölge)

### IAM kullanıcısı (geliştirme için)
1. IAM → Users → Create user
2. Programmatic access seçin
3. Politikalar:
   - `AmazonS3FullAccess`
   - `AmazonSageMakerFullAccess`
4. Access Key ID ve Secret Access Key'i kaydedin

### SageMaker Execution Role
1. IAM → Roles → Create role
2. Trusted entity: SageMaker
3. Policy: `AmazonSageMakerFullAccess`, `AmazonS3FullAccess`
4. Role ARN'ini kopyalayın:
   ```
   arn:aws:iam::123456789012:role/SageMakerExecutionRole
   ```

## 2. .env Yapılandırması

`backend/python_api/.env` dosyasını düzenleyin:

```env
USE_AWS=true
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
S3_BUCKET=ml-platform-datasets-YOURNAME
AWS_SAGEMAKER_ROLE=arn:aws:iam::123456789012:role/SageMakerExecutionRole
SAGEMAKER_INSTANCE_TYPE=ml.m5.large
SAGEMAKER_ENDPOINT_INSTANCE_TYPE=ml.m5.large
SAGEMAKER_FRAMEWORK_VERSION=1.2-1
```

## 3. Bağımlılıkları Yükleyin

```powershell
cd backend/python_api
pip install boto3 sagemaker
```

## 4. API'yi Başlatın

```powershell
python app.py
```

AWS durumunu kontrol edin:
```powershell
curl http://localhost:5000/api/aws/status
```

Beklenen yanıt:
```json
{
  "aws_configured": true,
  "s3_connection": "ok",
  "sagemaker_role": true
}
```

## 5. Kullanım Akışı

### Adım 1: Veri Yükle
- Frontend'den CSV yükleyin
- Dosya otomatik olarak S3'e de yüklenir: `s3://bucket/datasets/{id}/filename.csv`

### Adım 2: Bulutta Eğit
- Modeller sekmesi → **Eğitim Ortamı: AWS SageMaker**
- Target column: `species`
- Algorithm: `RandomForest`
- Eğit → SageMaker training job başlar

### Adım 3: Job Durumunu Kontrol Et
- "Job Durumunu Kontrol Et" butonuna tıklayın
- Veya API:
  ```http
  GET /api/model/train/status/{job_name}
  ```

### Adım 4: Modeli Dağıt
- Job `Completed` olduktan sonra "SageMaker'a Dağıt"
- Veya API:
  ```http
  POST /api/model/{model_id}/deploy
  ```

### Adım 5: Tahmin Yap
- Tahmin sekmesinden endpoint'e bağlı modeli seçin
- Tahmin SageMaker endpoint üzerinden yapılır

## API Endpoint'leri

| Endpoint | Açıklama |
|----------|----------|
| `GET /api/aws/status` | AWS bağlantı durumu |
| `POST /api/dataset/upload` | Veri yükle (+ S3) |
| `POST /api/model/train` | `training_mode: "cloud"` ile SageMaker job |
| `GET /api/model/train/status/{job}` | Job durumu |
| `POST /api/model/{id}/deploy` | Endpoint oluştur |
| `POST /api/model/predict` | Lokal veya endpoint tahmin |

## Maliyet Uyarısı

| Servis | Tahmini maliyet |
|--------|-----------------|
| S3 | Düşük (~$0.023/GB/ay) |
| SageMaker Training (ml.m5.large) | ~$0.115/saat |
| SageMaker Endpoint (7/24) | ~$0.115/saat (pahalı!) |

**Öneri:** Endpoint'i sadece demo sırasında açın, iş bitince silin:
```python
deployer.delete_endpoint('endpoint-name')
```

## Sorun Giderme

### `AWS is not configured`
- `.env` dosyasında `USE_AWS=true` olduğundan emin olun
- Flask'ı yeniden başlatın

### `Access Denied` (S3)
- IAM kullanıcısının bucket erişimi var mı?
- Bucket adı `.env` ile aynı mı?

### SageMaker job failed
- AWS Console → SageMaker → Training jobs → Logs
- Role ARN doğru mu?
- Dataset S3'te var mı?

### Endpoint oluşturulamıyor
- Training job `Completed` mi?
- `s3_model_uri` dolu mu?

## Lokal vs Bulut

| Özellik | Lokal | AWS Bulut |
|---------|-------|-----------|
| Eğitim | Anında | 5-15 dakika |
| Maliyet | Ücretsiz | Ücretli |
| Ölçeklenebilirlik | Sınırlı | Yüksek |
| Teslim/demo | ✅ İdeal | ✅ Proje gereksinimi |

Her iki mod da aynı anda çalışır. AWS yapılandırılmamışsa sistem otomatik olarak lokal modda devam eder.
