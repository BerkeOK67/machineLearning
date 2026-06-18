# Sample Data

Bu klasör örnek veri setleri içerir.

## Iris Dataset

`iris_sample.csv` - Iris çiçek türlerini sınıflandırmak için kullanılan klasik bir veri seti.

### Özellikler:
- **sepal_length**: Çanak yaprak uzunluğu (cm)
- **sepal_width**: Çanak yaprak genişliği (cm)
- **petal_length**: Taç yaprak uzunluğu (cm)
- **petal_width**: Taç yaprak genişliği (cm)
- **species**: Çiçek türü (setosa, versicolor, virginica)

### Kullanım:
1. Frontend'de "Veri Yükle" sekmesine gidin
2. `iris_sample.csv` dosyasını seçin
3. Dataset adı: "Iris Flowers"
4. Yükle butonuna tıklayın
5. Model eğit:
   - Target column: species
   - Model type: classification
   - Algorithm: RandomForest

### Örnek Tahmin Verisi:
```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

Beklenen sonuç: setosa (class 0)

---

## Kendi Verinizi Eklemek İçin:

1. CSV formatında bir dosya oluşturun
2. İlk satırda sütun adları olmalı
3. Desteklenen formatlar: CSV, XLSX, XLS
4. Maksimum dosya boyutu: 16MB
