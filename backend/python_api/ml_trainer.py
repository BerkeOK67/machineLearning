import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBClassifier, XGBRegressor
import os
from datetime import datetime

class MLModelTrainer:
    def __init__(self, model_folder='models'):
        self.model_folder = model_folder
        os.makedirs(model_folder, exist_ok=True)
        self.model = None
        self.model_type = None
        
        # Available algorithms
        self.classification_models = {
            'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
            'DecisionTree': DecisionTreeClassifier(random_state=42),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
            'XGBoost': XGBClassifier(random_state=42)
        }
        
        self.regression_models = {
            'LinearRegression': LinearRegression(),
            'Ridge': Ridge(),
            'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42),
            'XGBoostRegressor': XGBRegressor(random_state=42)
        }
    
    def train_classification(self, X_train, y_train, algorithm='RandomForest', params=None):
        """Train a classification model"""
        if algorithm not in self.classification_models:
            raise ValueError(f"Algorithm {algorithm} not supported for classification")
        
        self.model = self.classification_models[algorithm]
        self.model_type = 'classification'
        
        # Set custom parameters if provided
        if params:
            self.model.set_params(**params)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        return self.model
    
    def train_regression(self, X_train, y_train, algorithm='LinearRegression', params=None):
        """Train a regression model"""
        if algorithm not in self.regression_models:
            raise ValueError(f"Algorithm {algorithm} not supported for regression")
        
        self.model = self.regression_models[algorithm]
        self.model_type = 'regression'
        
        # Set custom parameters if provided
        if params:
            self.model.set_params(**params)
        
        # Train the model
        self.model.fit(X_train, y_train)
        
        return self.model
    
    def evaluate_classification(self, X_test, y_test):
        """Evaluate classification model"""
        if self.model is None:
            raise ValueError("No model trained yet")
        
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
        }
        
        return metrics
    
    def evaluate_regression(self, X_test, y_test):
        """Evaluate regression model"""
        if self.model is None:
            raise ValueError("No model trained yet")
        
        y_pred = self.model.predict(X_test)
        
        metrics = {
            'mae': float(mean_absolute_error(y_test, y_pred)),
            'mse': float(mean_squared_error(y_test, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
            'r2': float(r2_score(y_test, y_pred))
        }
        
        return metrics
    
    def predict(self, X):
        """Make predictions"""
        if self.model is None:
            raise ValueError("No model trained yet")
        
        predictions = self.model.predict(X)
        
        # Get prediction probabilities for classification
        if self.model_type == 'classification' and hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X)
            return predictions, probabilities
        
        return predictions, None
    
    def save_model(self, model_name):
        """Save trained model to disk"""
        if self.model is None:
            raise ValueError("No model to save")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name}_{timestamp}.pkl"
        filepath = os.path.join(self.model_folder, filename)
        
        joblib.dump(self.model, filepath)
        
        return filepath
    
    def load_model(self, filepath):
        """Load a trained model from disk"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.model = joblib.load(filepath)
        
        return self.model
    
    def get_feature_importance(self):
        """Get feature importance for tree-based models"""
        if self.model is None:
            raise ValueError("No model trained yet")
        
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_.tolist()
        else:
            return None
