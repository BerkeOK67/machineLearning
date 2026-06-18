from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
import pandas as pd
from datetime import timedelta

from config import Config
from models import db, User, Dataset, Model, Prediction
from mongo_db import MongoDB
from data_processor import DataProcessor
from ml_trainer import MLModelTrainer
from cloud.aws_s3 import S3Service, is_aws_configured

# Frontend klasörünün yolu (backend/python_api'den iki üst klasör = proje kökü)
FRONTEND_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'frontend')

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path='')
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Create upload and model folders
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODEL_FOLDER'], exist_ok=True)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def ensure_db_columns():
    """Add new AWS columns to existing SQLite database."""
    if not Config.USE_SQLITE:
        return

    from sqlalchemy import inspect, text

    inspector = inspect(db.engine)
    dataset_cols = {col['name'] for col in inspector.get_columns('datasets')}
    model_cols = {col['name'] for col in inspector.get_columns('models')}

    statements = []
    if 's3_uri' not in dataset_cols:
        statements.append('ALTER TABLE datasets ADD COLUMN s3_uri VARCHAR(500)')
    if 's3_model_uri' not in model_cols:
        statements.append('ALTER TABLE models ADD COLUMN s3_model_uri VARCHAR(500)')
    if 'training_mode' not in model_cols:
        statements.append("ALTER TABLE models ADD COLUMN training_mode VARCHAR(20) DEFAULT 'local'")
    if 'sagemaker_job_name' not in model_cols:
        statements.append('ALTER TABLE models ADD COLUMN sagemaker_job_name VARCHAR(100)')
    if 'sagemaker_endpoint_name' not in model_cols:
        statements.append('ALTER TABLE models ADD COLUMN sagemaker_endpoint_name VARCHAR(100)')

    for stmt in statements:
        db.session.execute(text(stmt))
    if statements:
        db.session.commit()


def upload_dataset_to_s3(dataset_id, filepath, filename):
    s3 = S3Service()
    s3_key = f'datasets/{dataset_id}/{filename}'
    s3.upload_file(filepath, s3_key)
    return s3.get_uri(f'datasets/{dataset_id}/')


# ============= Frontend Serving =============

@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path='index.html'):
    """Serve frontend files"""
    # API isteklerini pass et
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    # Dosya varsa sun, yoksa index.html'e yönlendir
    target = os.path.join(FRONTEND_FOLDER, path)
    if os.path.exists(target) and os.path.isfile(target):
        return send_from_directory(FRONTEND_FOLDER, path)
    return send_from_directory(FRONTEND_FOLDER, 'index.html')


# ============= Authentication Routes =============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            name=data['name'],
            email=data['email']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=1)
        )
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= Dataset Routes =============

@app.route('/api/dataset/upload', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def upload_dataset():
    """Upload a dataset"""
    try:
        user_id = 1  # Auth disabled during development

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process data
        processor = DataProcessor()
        file_type = filename.rsplit('.', 1)[1].lower()
        df = processor.load_data(filepath, file_type)
        
        # Get basic info
        info = processor.get_basic_info(df)
        
        # Save to MongoDB
        mongo = MongoDB()
        mongo_id = mongo.save_dataset(
            data=df.to_dict('records'),
            metadata={
                'filename': filename,
                'rows': df.shape[0],
                'columns': df.shape[1],
                'column_names': list(df.columns)
            }
        )
        
        # Save metadata to PostgreSQL
        dataset = Dataset(
            user_id=user_id,
            name=request.form.get('name', filename),
            filename=filename,
            mongo_id=mongo_id,
            rows=df.shape[0],
            columns=df.shape[1]
        )
        
        db.session.add(dataset)
        db.session.commit()

        s3_uri = None
        if is_aws_configured():
            try:
                s3_uri = upload_dataset_to_s3(dataset.id, filepath, filename)
                dataset.s3_uri = s3_uri
                db.session.commit()
            except Exception as s3_error:
                print(f'S3 upload warning: {s3_error}')
        
        return jsonify({
            'message': 'Dataset uploaded successfully',
            'dataset': dataset.to_dict(),
            'info': info,
            's3_uri': s3_uri
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/datasets', methods=['GET'])
def get_all_datasets():
    """Get all datasets"""
    try:
        datasets = Dataset.query.all()
        return jsonify({
            'datasets': [dataset.to_dict() for dataset in datasets]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dataset/<int:dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)

        # İlgili modelleri ve tahminleri sil
        for model in dataset.models:
            Prediction.query.filter_by(model_id=model.id).delete()
            if model.model_path and os.path.exists(model.model_path):
                os.remove(model.model_path)
            db.session.delete(model)

        # Yüklenen dosyayı sil
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], dataset.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        db.session.delete(dataset)
        db.session.commit()

        return jsonify({'message': 'Dataset deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dataset/<int:dataset_id>', methods=['GET'])
# @jwt_required()  # Disabled for testing
def get_dataset(dataset_id):
    """Get dataset information"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # Get data from MongoDB
        mongo = MongoDB()
        mongo_data = mongo.get_dataset(dataset.mongo_id)
        
        return jsonify({
            'dataset': dataset.to_dict(),
            'data': mongo_data['data'][:100] if mongo_data else []  # Return first 100 rows
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dataset/<int:dataset_id>/analyze', methods=['POST'])
# @jwt_required()  # Disabled for testing
def analyze_dataset(dataset_id):
    """Analyze a dataset"""
    try:
        dataset = Dataset.query.get_or_404(dataset_id)
        
        # Get data from MongoDB
        mongo = MongoDB()
        mongo_data = mongo.get_dataset(dataset.mongo_id)
        
        if not mongo_data:
            return jsonify({'error': 'Dataset not found in MongoDB'}), 404
        
        # Convert to DataFrame
        df = pd.DataFrame(mongo_data['data'])
        
        # Perform analysis
        processor = DataProcessor()
        stats = processor.get_statistics(df)
        correlation = processor.get_correlation_matrix(df)
        info = processor.get_basic_info(df)
        
        # Save analysis results to MongoDB
        mongo.save_analysis_result(
            dataset_id=str(dataset_id),
            analysis_type='statistical_analysis',
            result={
                'statistics': stats,
                'correlation': correlation,
                'info': info
            }
        )
        
        return jsonify({
            'message': 'Analysis completed',
            'statistics': stats,
            'correlation': correlation,
            'info': info
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= Model Training Routes =============

@app.route('/api/model/train', methods=['POST'])
# @jwt_required()  # Disabled for testing
def train_model():
    """Train a machine learning model (local or AWS SageMaker)"""
    try:
        data = request.get_json()
        
        dataset_id = data['dataset_id']
        algorithm = data['algorithm']
        target_column = data['target_column']
        model_type = data.get('model_type', 'classification')
        params = data.get('params', {})
        training_mode = data.get('training_mode', 'local')
        
        dataset = Dataset.query.get_or_404(dataset_id)

        if training_mode == 'cloud':
            return train_model_cloud(data, dataset, algorithm, target_column, model_type, params)

        mongo = MongoDB()
        mongo_data = mongo.get_dataset(dataset.mongo_id)
        df = pd.DataFrame(mongo_data['data'])
        
        processor = DataProcessor()
        df = processor.handle_missing_values(df)
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        categorical_cols = [col for col in categorical_cols if col != target_column]
        if len(categorical_cols) > 0:
            df = processor.encode_categorical(df, categorical_cols)
        
        if df[target_column].dtype == 'object':
            df = processor.encode_categorical(df, [target_column])
        
        X_train, X_test, y_train, y_test = processor.prepare_for_training(
            df, target_column, test_size=0.2
        )
        
        trainer = MLModelTrainer(app.config['MODEL_FOLDER'])
        
        if model_type == 'classification':
            trainer.train_classification(X_train, y_train, algorithm, params)
            metrics = trainer.evaluate_classification(X_test, y_test)
        else:
            trainer.train_regression(X_train, y_train, algorithm, params)
            metrics = trainer.evaluate_regression(X_test, y_test)
        
        model_name = f"{algorithm}_{dataset_id}"
        model_path = trainer.save_model(model_name)
        
        model = Model(
            name=data.get('name', f'{algorithm} Model'),
            algorithm=algorithm,
            dataset_id=dataset_id,
            accuracy=metrics.get('accuracy'),
            precision=metrics.get('precision'),
            recall=metrics.get('recall'),
            f1_score=metrics.get('f1_score'),
            model_path=model_path,
            training_mode='local',
            parameters=params
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'message': 'Model trained successfully',
            'model': model.to_dict(),
            'metrics': metrics,
            'training_mode': 'local'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def train_model_cloud(data, dataset, algorithm, target_column, model_type, params):
    """Start cloud training — AWS SageMaker veya simülasyon modu."""

    # Gerçek AWS varsa SageMaker kullan
    if is_aws_configured():
        return _train_sagemaker(data, dataset, algorithm, target_column, model_type, params)

    # AWS yoksa: lokalde eğit, cloud formatında response döndür
    return _train_simulated_cloud(data, dataset, algorithm, target_column, model_type, params)


def _train_sagemaker(data, dataset, algorithm, target_column, model_type, params):
    """Gerçek AWS SageMaker ile eğitim."""
    from cloud.sagemaker_train import SageMakerTrainer

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], dataset.filename)
    if not os.path.exists(filepath):
        mongo = MongoDB()
        mongo_data = mongo.get_dataset(dataset.mongo_id)
        df = pd.DataFrame(mongo_data['data'])
        df.to_csv(filepath, index=False)

    if not dataset.s3_uri:
        dataset.s3_uri = upload_dataset_to_s3(dataset.id, filepath, dataset.filename)
        db.session.commit()

    trainer = SageMakerTrainer()
    job_info = trainer.start_training_job(
        dataset_s3_uri=dataset.s3_uri,
        target_column=target_column,
        algorithm=algorithm,
        model_type=model_type,
    )

    model = Model(
        name=data.get('name', f'{algorithm} Cloud Model'),
        algorithm=algorithm,
        dataset_id=dataset.id,
        training_mode='cloud',
        sagemaker_job_name=job_info['job_name'],
        parameters={**params, 'target_column': target_column, 'model_type': model_type}
    )
    db.session.add(model)
    db.session.commit()

    return jsonify({
        'message': 'SageMaker training job started',
        'model': model.to_dict(),
        'job': job_info,
        'training_mode': 'cloud'
    }), 202


def _train_simulated_cloud(data, dataset, algorithm, target_column, model_type, params):
    """
    Simulated Cloud Training — AWS credentials olmadan çalışır.
    Eğitim lokalde yapılır, response formatı AWS SageMaker ile aynıdır.
    Bulut entegrasyon akışını göstermek için kullanılır.
    """
    from datetime import datetime

    mongo = MongoDB()
    mongo_data = mongo.get_dataset(dataset.mongo_id)
    df = pd.DataFrame(mongo_data['data'])

    processor = DataProcessor()
    df = processor.handle_missing_values(df)

    categorical_cols = [c for c in df.select_dtypes(include=['object']).columns if c != target_column]
    if categorical_cols:
        df = processor.encode_categorical(df, categorical_cols)
    if df[target_column].dtype == 'object':
        df = processor.encode_categorical(df, [target_column])

    X_train, X_test, y_train, y_test = processor.prepare_for_training(df, target_column, test_size=0.2)

    trainer = MLModelTrainer(app.config['MODEL_FOLDER'])
    if model_type == 'classification':
        trainer.train_classification(X_train, y_train, algorithm, params)
        metrics = trainer.evaluate_classification(X_test, y_test)
    else:
        trainer.train_regression(X_train, y_train, algorithm, params)
        metrics = trainer.evaluate_regression(X_test, y_test)

    model_name = f"cloud_{algorithm}_{dataset.id}"
    model_path = trainer.save_model(model_name)

    # Cloud job simülasyonu (SageMaker formatında)
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    simulated_job_name = f"ml-platform-sim-{algorithm.lower()}-{timestamp}"[:63]
    simulated_s3_uri = f"s3://ml-platform-simulated/models/{simulated_job_name}/output/model.tar.gz"

    model = Model(
        name=data.get('name', f'{algorithm} Cloud Model'),
        algorithm=algorithm,
        dataset_id=dataset.id,
        accuracy=metrics.get('accuracy'),
        precision=metrics.get('precision'),
        recall=metrics.get('recall'),
        f1_score=metrics.get('f1_score'),
        model_path=model_path,
        training_mode='cloud_simulated',
        sagemaker_job_name=simulated_job_name,
        s3_model_uri=simulated_s3_uri,
        parameters={**params, 'target_column': target_column, 'model_type': model_type}
    )
    db.session.add(model)
    db.session.commit()

    return jsonify({
        'message': 'Cloud training completed (simulated — AWS credentials not configured)',
        'model': model.to_dict(),
        'metrics': metrics,
        'job': {
            'job_name': simulated_job_name,
            'status': 'Completed',
            'model_artifacts': simulated_s3_uri,
            'note': 'Simulated cloud training — model trained locally, cloud artifacts are illustrative'
        },
        'training_mode': 'cloud_simulated'
    }), 201



@app.route('/api/model/train/status/<job_name>', methods=['GET'])
def get_training_job_status(job_name):
    """Get SageMaker training job status."""
    try:
        if not is_aws_configured():
            return jsonify({'error': 'AWS is not configured'}), 400

        from cloud.sagemaker_train import SageMakerTrainer
        trainer = SageMakerTrainer()
        status = trainer.get_job_status(job_name)

        model = Model.query.filter_by(sagemaker_job_name=job_name).first()
        if model and status['status'] == 'Completed' and status.get('model_artifacts'):
            model.s3_model_uri = status['model_artifacts']
            db.session.commit()
            status['model_id'] = model.id

        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model/<int:model_id>/deploy', methods=['POST'])
def deploy_model(model_id):
    """Deploy trained model to SageMaker endpoint."""
    try:
        if not is_aws_configured():
            return jsonify({'error': 'AWS is not configured'}), 400

        model = Model.query.get_or_404(model_id)

        if not model.s3_model_uri:
            if model.sagemaker_job_name:
                from cloud.sagemaker_train import SageMakerTrainer
                job_status = SageMakerTrainer().get_job_status(model.sagemaker_job_name)
                if job_status['status'] != 'Completed':
                    return jsonify({
                        'error': 'Training job not completed yet',
                        'status': job_status['status']
                    }), 400
                model.s3_model_uri = job_status.get('model_artifacts')
                db.session.commit()
            else:
                return jsonify({'error': 'No S3 model artifacts found'}), 400

        from cloud.sagemaker_deploy import SageMakerDeployer
        deployer = SageMakerDeployer()
        endpoint_name = None
        if request.is_json:
            payload = request.get_json(silent=True) or {}
            endpoint_name = payload.get('endpoint_name')
        deploy_info = deployer.deploy_model(model.s3_model_uri, endpoint_name)

        model.sagemaker_endpoint_name = deploy_info['endpoint_name']
        db.session.commit()

        return jsonify({
            'message': 'Model SageMaker endpoint\'e dağıtılıyor (arka planda oluşturuluyor)',
            'deployment': deploy_info,
            'model': model.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model/<int:model_id>/endpoint/status', methods=['GET'])
def get_endpoint_status(model_id):
    """Get SageMaker endpoint status."""
    try:
        model = Model.query.get_or_404(model_id)

        if not model.sagemaker_endpoint_name:
            return jsonify({'status': 'NoEndpoint', 'message': 'Bu model için endpoint yok'}), 200

        if not is_aws_configured():
            return jsonify({'status': 'Unknown', 'message': 'AWS yapılandırılmamış'}), 200

        from cloud.sagemaker_deploy import SageMakerDeployer
        deployer = SageMakerDeployer()
        status_info = deployer.get_endpoint_status(model.sagemaker_endpoint_name)
        return jsonify(status_info), 200
    except Exception as e:
        # Endpoint bulunamazsa
        return jsonify({'status': 'NotFound', 'message': str(e)}), 200


@app.route('/api/model/<int:model_id>', methods=['GET'])
# @jwt_required()  # Disabled for testing
def get_model(model_id):
    """Get model information"""
    try:
        model = Model.query.get_or_404(model_id)
        
        return jsonify({
            'model': model.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/models', methods=['GET'])
# @jwt_required()  # Disabled for testing
def get_all_models():
    """Get all models"""
    try:
        models = Model.query.all()
        
        return jsonify({
            'models': [model.to_dict() for model in models]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/model/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """Delete a model and optionally its SageMaker endpoint"""
    try:
        model = Model.query.get_or_404(model_id)

        # AWS endpoint'ini sil (varsa)
        if model.sagemaker_endpoint_name and is_aws_configured():
            try:
                from cloud.sagemaker_deploy import SageMakerDeployer
                deployer = SageMakerDeployer()
                deployer.delete_endpoint(model.sagemaker_endpoint_name)
                print(f"SageMaker endpoint silindi: {model.sagemaker_endpoint_name}")
            except Exception as ep_err:
                print(f"Endpoint silme hatası (devam ediliyor): {ep_err}")

        # Model dosyasını diskten sil
        if model.model_path and os.path.exists(model.model_path):
            os.remove(model.model_path)

        # Tahminleri de sil
        Prediction.query.filter_by(model_id=model_id).delete()

        db.session.delete(model)
        db.session.commit()

        return jsonify({'message': 'Model deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= Prediction Routes =============

@app.route('/api/model/predict', methods=['POST'])
# @jwt_required()  # Disabled for testing
def make_prediction():
    """Make a prediction using a trained model"""
    try:
        data = request.get_json()
        
        model_id = data['model_id']
        input_data = data['data']
        
        # Get model from database
        model = Model.query.get_or_404(model_id)

        if model.sagemaker_endpoint_name and is_aws_configured():
            from cloud.sagemaker_deploy import SageMakerDeployer
            deployer = SageMakerDeployer()
            cloud_result = deployer.predict(model.sagemaker_endpoint_name, input_data)
            result = {
                'prediction': cloud_result.get('predictions', [cloud_result])[0]
                if isinstance(cloud_result.get('predictions'), list)
                else cloud_result,
                'probabilities': None,
                'source': 'sagemaker_endpoint'
            }
        else:
            if not model.model_path:
                return jsonify({'error': 'Model file not found. Train locally or deploy cloud model.'}), 400

            trainer = MLModelTrainer(app.config['MODEL_FOLDER'])
            trainer.load_model(model.model_path)
            input_df = pd.DataFrame([input_data])
            predictions, probabilities = trainer.predict(input_df)

            result = {
                'prediction': predictions.tolist()[0],
                'probabilities': probabilities.tolist()[0] if probabilities is not None else None,
                'source': 'local'
            }
        
        # Save prediction to database
        prediction = Prediction(
            model_id=model_id,
            input_data=input_data,
            result=result
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        return jsonify({
            'message': 'Prediction successful',
            'prediction': prediction.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/<int:model_id>', methods=['GET'])
# @jwt_required()  # Disabled for testing
def get_predictions(model_id):
    """Get all predictions for a model"""
    try:
        predictions = Prediction.query.filter_by(model_id=model_id).all()
        
        return jsonify({
            'predictions': [pred.to_dict() for pred in predictions]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============= Health Check =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'ML Platform API',
        'aws_enabled': is_aws_configured(),
        'sagemaker_role_configured': bool(Config.AWS_SAGEMAKER_ROLE)
    }), 200


@app.route('/api/aws/status', methods=['GET'])
def aws_status():
    """Check AWS integration status."""
    status = {
        'aws_configured': is_aws_configured(),
        's3_bucket': Config.S3_BUCKET if is_aws_configured() else None,
        'region': Config.AWS_REGION,
        'sagemaker_role': bool(Config.AWS_SAGEMAKER_ROLE),
        'training_instance': Config.SAGEMAKER_INSTANCE_TYPE,
        'endpoint_instance': Config.SAGEMAKER_ENDPOINT_INSTANCE_TYPE,
    }

    if is_aws_configured():
        try:
            s3 = S3Service()
            s3.client.head_bucket(Bucket=Config.S3_BUCKET)
            status['s3_connection'] = 'ok'
        except Exception as e:
            status['s3_connection'] = f'error: {str(e)}'

    return jsonify(status), 200


# ============= Error Handlers =============

@app.errorhandler(422)
def handle_unprocessable_entity(e):
    """Handle 422 errors"""
    print(f"422 Error: {str(e)}")
    return jsonify({'error': 'Unprocessable entity', 'detail': str(e)}), 422

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    print(f"Unauthorized: {callback}")
    return jsonify({'error': 'Missing or invalid token'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(callback):
    print(f"Invalid token: {callback}")
    return jsonify({'error': 'Invalid token'}), 422

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_data):
    print(f"Token expired")
    return jsonify({'error': 'Token has expired'}), 401


# ============= Database Initialization =============

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_db_columns()
    app.run(host='0.0.0.0', port=5000, debug=True)
