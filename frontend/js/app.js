// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken');
let currentUser = JSON.parse(localStorage.getItem('user') || 'null');
let currentDatasetId = null;
let currentCloudJobName = null;
let currentCloudModelId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Sidebar başlangıçta gizli (auth page görünüyor)
    document.getElementById('sidebar').style.display = 'none';

    if (authToken) {
        showMainApp();
        loadDashboard();
    } else {
        showLogin();
    }

    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    document.getElementById('uploadForm')?.addEventListener('submit', handleUpload);
    document.getElementById('trainModelForm')?.addEventListener('submit', handleTrainModel);
    document.getElementById('predictForm')?.addEventListener('submit', handlePredict);
    document.getElementById('modelType')?.addEventListener('change', updateAlgorithmList);
}

// Algoritma listesini model tipine göre güncelle
function updateAlgorithmList() {
    const modelType = document.getElementById('modelType').value;
    const algorithmSelect = document.getElementById('algorithmSelect');
    
    if (modelType === 'classification') {
        algorithmSelect.innerHTML = `
            <option value="RandomForest">Random Forest</option>
            <option value="DecisionTree">Decision Tree</option>
            <option value="LogisticRegression">Logistic Regression</option>
            <option value="XGBoost">XGBoost</option>
        `;
    } else {
        algorithmSelect.innerHTML = `
            <option value="LinearRegression">Linear Regression</option>
            <option value="Ridge">Ridge Regression</option>
            <option value="RandomForestRegressor">Random Forest Regressor</option>
            <option value="XGBoostRegressor">XGBoost Regressor</option>
        `;
    }
}

// Authentication
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.user;
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('user', JSON.stringify(currentUser));
            
            showAlert('Giriş başarılı!', 'success');
            showMainApp();
            loadDashboard();
        } else {
            showAlert(data.error || 'Giriş başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Kayıt başarılı! Şimdi giriş yapabilirsiniz.', 'success');
            showLogin();
        } else {
            showAlert(data.error || 'Kayıt başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    showLogin();
}

// Navigation
function showSection(sectionId) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    // Sidebar aktif nav item
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    const navBtn = document.getElementById('nav-' + sectionId);
    if (navBtn) navBtn.classList.add('active');

    // Load section-specific data
    if (sectionId === 'dashboard') {
        loadDashboard();
    } else if (sectionId === 'datasets') {
        loadDatasetsList();
    } else if (sectionId === 'models') {
        loadDatasets();
        loadModels();
    } else if (sectionId === 'predict') {
        loadModelsForPrediction();
    }
}

function updateFileName(input) {
    const drop = document.getElementById('fileDrop');
    if (input.files && input.files[0]) {
        drop.querySelector('.file-drop-text').textContent = input.files[0].name;
        drop.style.borderColor = 'var(--purple)';
        drop.style.background = 'rgba(139,92,246,0.08)';
    }
}

function showLogin() {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.auth-page').forEach(s => s.classList.remove('active'));
    document.getElementById('loginSection').classList.add('active');
    document.getElementById('sidebar').style.display = 'none';
}

function showRegister() {
    document.querySelectorAll('.auth-page').forEach(s => s.classList.remove('active'));
    document.getElementById('registerSection').classList.add('active');
}

function showMainApp() {
    document.querySelectorAll('.auth-page').forEach(s => s.classList.remove('active'));
    document.getElementById('sidebar').style.display = 'flex';
    // Sidebar'da kullanıcı adını göster
    if (currentUser) {
        const el = document.getElementById('sidebarUserName');
        if (el) el.textContent = currentUser.name || currentUser.email || 'Kullanıcı';
    }
    showSection('dashboard');
}

// Dashboard
async function loadDashboard() {
    try {
        const [datasetsRes, modelsRes] = await Promise.all([
            fetch(`${API_BASE_URL}/datasets`),
            fetch(`${API_BASE_URL}/models`)
        ]);

        if (datasetsRes.ok) {
            const datasetsData = await datasetsRes.json();
            document.getElementById('totalDatasets').textContent = datasetsData.datasets.length;
        }

        if (modelsRes.ok) {
            const modelsData = await modelsRes.json();
            document.getElementById('totalModels').textContent = modelsData.models.length;

            // Tahmin sayısını hesapla (tüm modellerin prediction sayısı)
            let totalPredictions = 0;
            for (const model of modelsData.models) {
                try {
                    const predRes = await fetch(`${API_BASE_URL}/predictions/${model.id}`);
                    if (predRes.ok) {
                        const predData = await predRes.json();
                        totalPredictions += predData.predictions.length;
                    }
                } catch (e) { /* sessizce geç */ }
            }
            document.getElementById('totalPredictions').textContent = totalPredictions;
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ============= Dataset List (Datasets page) =============

async function loadDatasetsList() {
    const grid = document.getElementById('datasetsGrid');
    if (!grid) return;
    grid.innerHTML = '<p style="color:var(--text-muted)">Yükleniyor...</p>';

    try {
        const res = await fetch(`${API_BASE_URL}/datasets`);
        const data = await res.json();

        if (!res.ok || !data.datasets) {
            grid.innerHTML = '<p style="color:var(--red-2)">Datasetler yüklenemedi.</p>';
            return;
        }

        if (data.datasets.length === 0) {
            grid.innerHTML = `
                <div style="grid-column:1/-1; text-align:center; padding:48px; color:var(--text-muted);">
                    <div style="font-size:40px; margin-bottom:12px;">📂</div>
                    <p>Henüz dataset yüklenmedi.</p>
                    <button class="btn btn-primary" style="width:auto;margin-top:16px" onclick="showSection('upload')">+ Veri Yükle</button>
                </div>`;
            return;
        }

        grid.innerHTML = data.datasets.map(ds => `
            <div class="dataset-card">
                <div class="dataset-card-header">
                    <div>
                        <div class="dataset-card-title">📄 ${ds.name}</div>
                        <div class="dataset-card-date">${new Date(ds.created_at).toLocaleString('tr-TR')}</div>
                    </div>
                </div>
                <div class="dataset-card-meta">
                    <span class="meta-badge blue">📊 ${ds.rows} satır</span>
                    <span class="meta-badge green">🔠 ${ds.columns} sütun</span>
                    ${ds.s3_uri ? '<span class="meta-badge">☁️ S3</span>' : ''}
                </div>
                <div class="dataset-card-actions">
                    <button class="btn btn-secondary btn-sm" onclick="viewDataset(${ds.id}, '${ds.name}')">
                        🔍 Görüntüle
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="deleteDataset(${ds.id}, '${ds.name}')">
                        🗑️ Sil
                    </button>
                </div>
            </div>
        `).join('');

    } catch (err) {
        grid.innerHTML = `<p style="color:var(--red-2)">Hata: ${err.message}</p>`;
    }
}

async function viewDataset(datasetId, name) {
    const detailCard = document.getElementById('datasetDetailCard');
    const detailTitle = document.getElementById('detailTitle');
    const detailMeta = document.getElementById('detailMeta');
    const detailPreview = document.getElementById('detailPreview');

    detailTitle.textContent = `📄 ${name}`;
    detailMeta.innerHTML = '<p style="color:var(--text-muted)">Yükleniyor...</p>';
    detailPreview.innerHTML = '';
    detailCard.style.display = 'block';
    detailCard.scrollIntoView({ behavior: 'smooth', block: 'start' });

    try {
        const res = await fetch(`${API_BASE_URL}/dataset/${datasetId}`);
        const data = await res.json();

        if (!res.ok) {
            detailMeta.innerHTML = `<p style="color:var(--red-2)">${data.error || 'Yüklenemedi'}</p>`;
            return;
        }

        const ds = data.dataset;
        detailMeta.innerHTML = `
            <div class="dataset-card-meta" style="margin-bottom:12px;">
                <span class="meta-badge blue">📊 ${ds.rows} satır</span>
                <span class="meta-badge green">🔠 ${ds.columns} sütun</span>
                ${ds.s3_uri ? `<span class="meta-badge" title="${ds.s3_uri}">☁️ S3'te</span>` : ''}
                <span class="meta-badge">${new Date(ds.created_at).toLocaleString('tr-TR')}</span>
            </div>
        `;

        // Tablo preview
        const rows = data.data || [];
        if (rows.length === 0) {
            detailPreview.innerHTML = '<p style="color:var(--text-muted)">Veri bulunamadı.</p>';
            return;
        }

        const cols = Object.keys(rows[0]);
        const headerHTML = cols.map(c => `<th>${c}</th>`).join('');
        const rowsHTML = rows.slice(0, 50).map(row =>
            `<tr>${cols.map(c => `<td>${row[c] ?? ''}</td>`).join('')}</tr>`
        ).join('');

        detailPreview.innerHTML = `
            <p style="font-size:12px;color:var(--text-muted);margin-bottom:8px;">İlk ${Math.min(50, rows.length)} satır görüntüleniyor (toplam ${ds.rows})</p>
            <div class="preview-table-wrap">
                <table class="preview-table">
                    <thead><tr>${headerHTML}</tr></thead>
                    <tbody>${rowsHTML}</tbody>
                </table>
            </div>
        `;

    } catch (err) {
        detailMeta.innerHTML = `<p style="color:var(--red-2)">Hata: ${err.message}</p>`;
    }
}

async function deleteDataset(datasetId, name) {
    if (!confirm(`"${name}" datasetini silmek istediğinizden emin misiniz?\nBu dataset ile eğitilen modeller de silinecek!`)) return;

    try {
        const res = await fetch(`${API_BASE_URL}/dataset/${datasetId}`, { method: 'DELETE' });
        const data = await res.json();

        if (res.ok) {
            showAlert(`"${name}" başarıyla silindi.`, 'success');
            document.getElementById('datasetDetailCard').style.display = 'none';
            loadDatasetsList();
            loadDashboard();
        } else {
            showAlert(data.error || 'Silme başarısız', 'error');
        }
    } catch (err) {
        showAlert('Bağlantı hatası: ' + err.message, 'error');
    }
}

// Dataset Upload
async function handleUpload(e) {
    e.preventDefault();
    
    const name = document.getElementById('datasetName').value;
    const file = document.getElementById('datasetFile').files[0];
    
    if (!file) {
        showAlert('Lütfen bir dosya seçin', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('name', name);

    const submitBtn = e.target.querySelector('button[type="submit"]');
    setLoading(submitBtn, true, 'Yükleniyor...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/dataset/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Dataset başarıyla yüklendi!', 'success');
            currentDatasetId = data.dataset.id;

            // Sütun tiplerini göster
            const dtypes = data.info.dtypes || {};
            const dtypeRows = Object.entries(dtypes).map(([col, t]) =>
                `<tr><td>${col}</td><td>${t}</td></tr>`
            ).join('');

            // Eksik değerleri göster
            const missing = data.info.missing_values || {};
            const missingText = Object.values(missing).some(v => v > 0)
                ? Object.entries(missing).filter(([,v]) => v > 0).map(([col, v]) => `${col}: ${v}`).join(', ')
                : 'Yok';
            
            const infoDiv = document.getElementById('datasetInfo');
            infoDiv.innerHTML = `
                <p><strong>Ad:</strong> ${data.dataset.name}</p>
                <p><strong>Satır Sayısı:</strong> ${data.dataset.rows}</p>
                <p><strong>Sütun Sayısı:</strong> ${data.dataset.columns}</p>
                <p><strong>Eksik Değerler:</strong> ${missingText}</p>
                <h4 style="margin-top:15px;margin-bottom:8px;">Sütun Tipleri:</h4>
                <table class="info-table">
                    <thead><tr><th>Sütun</th><th>Tip</th></tr></thead>
                    <tbody>${dtypeRows}</tbody>
                </table>
            `;
            
            document.getElementById('uploadResult').style.display = 'block';
            document.getElementById('uploadForm').reset();
            // Dosya seçici alanını sıfırla
            const drop = document.getElementById('fileDrop');
            if (drop) {
                drop.querySelector('.file-drop-text').textContent = 'CSV veya Excel dosyası seçin';
                drop.style.borderColor = '';
                drop.style.background = '';
            }
            loadDashboard(); // Dashboard sayaçlarını güncelle
        } else {
            showAlert(data.error || 'Yükleme başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    } finally {
        setLoading(submitBtn, false, 'Yükle');
    }
}

async function analyzeDataset() {
    if (!currentDatasetId) {
        showAlert('Önce bir dataset yükleyin', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/dataset/${currentDatasetId}/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Analiz tamamlandı!', 'success');
            
            // Display analysis results
            const analysisDiv = document.getElementById('analysisInfo');
            analysisDiv.innerHTML = `
                <h4>İstatistiksel Bilgiler:</h4>
                <pre>${JSON.stringify(data.statistics, null, 2)}</pre>
                <h4>Korelasyon Matrisi:</h4>
                <pre>${JSON.stringify(data.correlation, null, 2)}</pre>
            `;
            
            document.getElementById('analysisResult').style.display = 'block';
        } else {
            showAlert(data.error || 'Analiz başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

// Load Datasets
async function loadDatasets() {
    try {
        const response = await fetch(`${API_BASE_URL}/datasets`);
        const data = await response.json();
        const select = document.getElementById('datasetSelect');
        select.innerHTML = '<option value="">Seçiniz...</option>';

        if (response.ok && data.datasets) {
            data.datasets.forEach(dataset => {
                select.innerHTML += `<option value="${dataset.id}">${dataset.name} (${dataset.rows} satır)</option>`;
            });
            if (currentDatasetId) {
                select.value = currentDatasetId;
            }
        }
    } catch (error) {
        console.error('Error loading datasets:', error);
    }
}

// Model Training
async function handleTrainModel(e) {
    e.preventDefault();
    
    const datasetId = document.getElementById('datasetSelect').value;
    const targetColumn = document.getElementById('targetColumn').value;
    const modelType = document.getElementById('modelType').value;
    const algorithm = document.getElementById('algorithmSelect').value;
    const trainingMode = document.getElementById('trainingMode').value;
    
    if (!datasetId) {
        showAlert('Lütfen bir dataset seçin', 'error');
        return;
    }

    const submitBtn = e.target.querySelector('button[type="submit"]');
    setLoading(submitBtn, true, 'Eğitiliyor...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/model/train`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                dataset_id: parseInt(datasetId),
                target_column: targetColumn,
                model_type: modelType,
                algorithm: algorithm,
                training_mode: trainingMode,
                name: `${algorithm} Model`
            })
        });
        
        const data = await response.json();
        
        if (response.ok || response.status === 202) {
            const isCloud = trainingMode === 'cloud';
            showAlert(isCloud ? 'SageMaker eğitim job başlatıldı!' : 'Model başarıyla eğitildi!', 'success');
            
            const metricsDiv = document.getElementById('modelMetrics');
            const title = document.getElementById('trainingResultTitle');
            const checkBtn = document.getElementById('checkJobStatusBtn');
            const deployBtn = document.getElementById('deployModelBtn');

            if (isCloud) {
                title.textContent = 'AWS SageMaker Eğitimi Başlatıldı';
                currentCloudJobName = data.job?.job_name;
                currentCloudModelId = data.model?.id;
                metricsDiv.innerHTML = `
                    <p><strong>Job:</strong> ${currentCloudJobName}</p>
                    <p><strong>Durum:</strong> ${data.job?.status || 'InProgress'}</p>
                    <p>Eğitim tamamlandığında "Job Durumunu Kontrol Et" butonuna tıklayın.</p>
                `;
                checkBtn.style.display = 'inline-block';
                deployBtn.style.display = 'none';
            } else {
                title.textContent = 'Eğitim Tamamlandı!';
                const m = data.metrics || {};
                metricsDiv.innerHTML = `
                    <h4>Model Performansı:</h4>
                    <table class="info-table">
                        <tbody>
                        ${m.accuracy !== undefined ? `<tr><td>Accuracy</td><td>${(m.accuracy * 100).toFixed(2)}%</td></tr>` : ''}
                        ${m.precision !== undefined ? `<tr><td>Precision</td><td>${(m.precision * 100).toFixed(2)}%</td></tr>` : ''}
                        ${m.recall !== undefined ? `<tr><td>Recall</td><td>${(m.recall * 100).toFixed(2)}%</td></tr>` : ''}
                        ${m.f1_score !== undefined ? `<tr><td>F1 Score</td><td>${(m.f1_score * 100).toFixed(2)}%</td></tr>` : ''}
                        ${m.r2 !== undefined ? `<tr><td>R² Score</td><td>${m.r2.toFixed(4)}</td></tr>` : ''}
                        ${m.rmse !== undefined ? `<tr><td>RMSE</td><td>${m.rmse.toFixed(4)}</td></tr>` : ''}
                        ${m.mae !== undefined ? `<tr><td>MAE</td><td>${m.mae.toFixed(4)}</td></tr>` : ''}
                        </tbody>
                    </table>
                `;
                checkBtn.style.display = 'none';
                deployBtn.style.display = 'none';
            }
            
            document.getElementById('trainingResult').style.display = 'block';
            document.getElementById('trainModelForm').reset();
            updateAlgorithmList(); // reset algoritma listesini sıfırla
            
            // Reload models list
            loadModels();
        } else {
            showAlert(data.error || 'Eğitim başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    } finally {
        setLoading(submitBtn, false, 'Modeli Eğit');
    }
}

// Load Models
async function loadModels() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const modelsList = document.getElementById('modelsList');
            
            if (data.models.length === 0) {
                modelsList.innerHTML = '<p>Henüz eğitilmiş model yok.</p>';
                return;
            }
            
            modelsList.innerHTML = data.models.map(model => {
                const modeLabel = {
                    'local': '🖥️ Lokal',
                    'cloud': '☁️ AWS SageMaker',
                    'cloud_simulated': '☁️ Bulut (Simüle)'
                }[model.training_mode] || model.training_mode || 'Lokal';

                const endpointBadge = model.sagemaker_endpoint_name
                    ? `<span style="background:#28a745;color:white;padding:2px 8px;border-radius:4px;font-size:12px;">✅ Endpoint Aktif</span>`
                    : '';

                const isCloudModel = model.training_mode === 'cloud' || model.training_mode === 'cloud_simulated';
                const canDeploy = isCloudModel && !model.sagemaker_endpoint_name && model.training_mode === 'cloud';

                return `
                <div class="model-card">
                    <h4>${model.name} ${endpointBadge}</h4>
                    <p><strong>Algoritma:</strong> ${model.algorithm}</p>
                    <p><strong>Eğitim:</strong> ${modeLabel}</p>
                    <p><strong>Accuracy:</strong> ${model.accuracy ? (model.accuracy * 100).toFixed(2) + '%' : 'N/A'}</p>
                    ${model.sagemaker_job_name ? `<p><strong>Job:</strong> <code style="font-size:11px">${model.sagemaker_job_name}</code></p>` : ''}
                    ${model.sagemaker_endpoint_name ? `<p><strong>Endpoint:</strong> <code style="font-size:11px">${model.sagemaker_endpoint_name}</code></p>` : ''}
                    <p><strong>Tarih:</strong> ${new Date(model.created_at).toLocaleDateString('tr-TR')}</p>
                    <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap;">
                        ${canDeploy ? `<button class="btn btn-secondary" onclick="deployModelById(${model.id})">🚀 Dağıt</button>` : ''}
                        ${model.sagemaker_endpoint_name ? `<button class="btn btn-secondary" onclick="checkEndpointStatusById(${model.id})">📡 Endpoint Durumu</button>` : ''}
                        <button class="btn btn-danger" onclick="deleteModel(${model.id})">🗑️ Sil</button>
                    </div>
                </div>
            `}).join('');

        }
    } catch (error) {
        console.error('Error loading models:', error);
    }
}

async function deleteModel(modelId) {
    if (!confirm('Bu modeli silmek istediğinizden emin misiniz?')) return;

    try {
        const response = await fetch(`${API_BASE_URL}/model/${modelId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        if (response.ok) {
            showAlert('Model silindi.', 'success');
            loadModels();
            loadDashboard();
        } else {
            const data = await response.json();
            showAlert(data.error || 'Silme başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}


// Load Models for Prediction
async function loadModelsForPrediction() {
    try {
        const response = await fetch(`${API_BASE_URL}/models`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('modelSelect');
            select.innerHTML = '<option value="">Seçiniz...</option>';
            
            data.models.forEach(model => {
                select.innerHTML += `<option value="${model.id}">${model.name} (${model.algorithm})</option>`;
            });
        }
    } catch (error) {
        console.error('Error loading models:', error);
    }
}

// Make Prediction
async function handlePredict(e) {
    e.preventDefault();
    
    const modelId = document.getElementById('modelSelect').value;
    const inputDataStr = document.getElementById('inputData').value;
    
    if (!modelId) {
        showAlert('Lütfen bir model seçin', 'error');
        return;
    }
    
    let inputData;
    try {
        inputData = JSON.parse(inputDataStr);
    } catch (error) {
        showAlert('Geçersiz JSON formatı', 'error');
        return;
    }

    const submitBtn = e.target.querySelector('button[type="submit"]');
    setLoading(submitBtn, true, 'Tahmin yapılıyor...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/model/predict`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_id: parseInt(modelId),
                data: inputData
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Tahmin başarılı!', 'success');

            // API'den gelen result yapısını güvenli şekilde oku
            const result = data.prediction?.result || {};
            const prediction = result.prediction;
            const probabilities = result.probabilities;
            const source = result.source || 'local';
            
            const predictionDiv = document.getElementById('predictionInfo');
            predictionDiv.innerHTML = `
                <table class="info-table">
                    <tbody>
                        <tr><td><strong>Tahmin Sonucu</strong></td><td>${prediction}</td></tr>
                        <tr><td><strong>Kaynak</strong></td><td>${source === 'sagemaker_endpoint' ? 'AWS SageMaker' : 'Lokal'}</td></tr>
                        ${probabilities ? `<tr><td><strong>Olasılıklar</strong></td><td>${JSON.stringify(probabilities)}</td></tr>` : ''}
                    </tbody>
                </table>
            `;
            
            document.getElementById('predictionResult').style.display = 'block';
        } else {
            showAlert(data.error || 'Tahmin başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    } finally {
        setLoading(submitBtn, false, 'Tahmin Yap');
    }
}

// Utility Functions
async function checkJobStatus() {
    if (!currentCloudJobName) return;

    try {
        const response = await fetch(`${API_BASE_URL}/model/train/status/${currentCloudJobName}`);
        const data = await response.json();

        if (response.ok) {
            const metricsDiv = document.getElementById('modelMetrics');
            metricsDiv.innerHTML = `
                <p><strong>Job:</strong> ${data.job_name}</p>
                <p><strong>Durum:</strong> ${data.status}</p>
                ${data.model_artifacts ? `<p><strong>Model:</strong> ${data.model_artifacts}</p>` : ''}
                ${data.failure_reason ? `<p><strong>Hata:</strong> ${data.failure_reason}</p>` : ''}
            `;

            if (data.status === 'Completed') {
                currentCloudModelId = data.model_id || currentCloudModelId;
                document.getElementById('deployModelBtn').style.display = 'inline-block';
                showAlert('Bulut eğitimi tamamlandı! Şimdi dağıtabilirsiniz.', 'success');
            }
        } else {
            showAlert(data.error || 'Job durumu alınamadı', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

async function deployModel() {
    if (currentCloudModelId) {
        await deployModelById(currentCloudModelId);
    }
}

async function deployModelById(modelId) {
    try {
        showAlert('⏳ SageMaker endpoint oluşturuluyor (arka planda, birkaç dakika sürer)...', 'success');
        const response = await fetch(`${API_BASE_URL}/model/${modelId}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        const data = await response.json();

        if (response.ok) {
            showAlert(`☁️ Endpoint oluşturuluyor: ${data.deployment?.endpoint_name} — Hazır olmak birkaç dakika alabilir.`, 'success');
            currentCloudModelId = modelId;
            // Endpoint status check butonunu göster
            document.getElementById('checkEndpointBtn').style.display = 'inline-block';
            document.getElementById('deployModelBtn').style.display = 'none';
            loadModels();
        } else {
            showAlert(data.error || 'Dağıtım başarısız', 'error');
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

async function checkEndpointStatus() {
    if (!currentCloudModelId) return;
    await checkEndpointStatusById(currentCloudModelId);
}

async function checkEndpointStatusById(modelId) {
    try {
        const response = await fetch(`${API_BASE_URL}/model/${modelId}/endpoint/status`);
        const data = await response.json();

        const statusEmoji = {
            'InService': '✅',
            'Creating': '⏳',
            'Updating': '🔄',
            'Failed': '❌',
            'NotFound': '❓',
            'NoEndpoint': 'ℹ️'
        }[data.status] || '❓';

        showAlert(`${statusEmoji} Endpoint durumu: ${data.status}${data.message ? ' — ' + data.message : ''}`, 
            data.status === 'InService' ? 'success' : 'error');

        if (data.status === 'InService') {
            showAlert('✅ Endpoint hazır! Artık tahmin ekranından bu modeli kullanabilirsiniz.', 'success');
            loadModels();
        }
    } catch (error) {
        showAlert('Bağlantı hatası: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    // Toast notification — sağ alt köşede
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;';
        document.body.appendChild(toastContainer);
    }

    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.cssText = 'min-width:280px;max-width:400px;box-shadow:0 8px 32px rgba(0,0,0,0.5);';
    toast.textContent = message;

    toastContainer.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// Loading state helper
function setLoading(button, isLoading, loadingText) {
    if (!button) return;
    if (isLoading) {
        button.disabled = true;
        button._originalText = button.innerHTML;
        button.innerHTML = `<span class="spinner"></span> ${loadingText || 'Yükleniyor...'}`;
        button.style.opacity = '0.75';
    } else {
        button.disabled = false;
        button.innerHTML = button._originalText || loadingText || 'Gönder';
        button.style.opacity = '1';
    }
}
