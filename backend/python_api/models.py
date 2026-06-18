from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Dataset(db.Model):
    __tablename__ = 'datasets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    mongo_id = db.Column(db.String(100))
    s3_uri = db.Column(db.String(500))
    rows = db.Column(db.Integer)
    columns = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='datasets')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'filename': self.filename,
            's3_uri': self.s3_uri,
            'rows': self.rows,
            'columns': self.columns,
            'created_at': self.created_at.isoformat()
        }


class Model(db.Model):
    __tablename__ = 'models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    algorithm = db.Column(db.String(50), nullable=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('datasets.id'), nullable=False)
    accuracy = db.Column(db.Float)
    precision = db.Column(db.Float)
    recall = db.Column(db.Float)
    f1_score = db.Column(db.Float)
    model_path = db.Column(db.String(255))
    s3_model_uri = db.Column(db.String(500))
    training_mode = db.Column(db.String(20), default='local')
    sagemaker_job_name = db.Column(db.String(100))
    sagemaker_endpoint_name = db.Column(db.String(100))
    parameters = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    dataset = db.relationship('Dataset', backref='models')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'algorithm': self.algorithm,
            'dataset_id': self.dataset_id,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'model_path': self.model_path,
            's3_model_uri': self.s3_model_uri,
            'training_mode': self.training_mode,
            'sagemaker_job_name': self.sagemaker_job_name,
            'sagemaker_endpoint_name': self.sagemaker_endpoint_name,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat()
        }


class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('models.id'), nullable=False)
    input_data = db.Column(db.JSON, nullable=False)
    result = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    model = db.relationship('Model', backref='predictions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_id': self.model_id,
            'input_data': self.input_data,
            'result': self.result,
            'created_at': self.created_at.isoformat()
        }
