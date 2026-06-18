"""
SageMaker training script for scikit-learn models.
Runs inside SageMaker training container.
"""
import argparse
import json
import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np


CLASSIFIERS = {
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'DecisionTree': DecisionTreeClassifier(random_state=42),
    'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
}

REGRESSORS = {
    'LinearRegression': LinearRegression(),
    'Ridge': Ridge(),
    'RandomForestRegressor': RandomForestRegressor(n_estimators=100, random_state=42),
}


def load_data(train_path):
    return pd.read_csv(train_path)


def prepare_data(df, target_column, model_type):
    df = df.copy()
    label_encoders = {}

    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le.classes_.tolist()

    X = df.drop(columns=[target_column])
    y = df[target_column]

    return train_test_split(X, y, test_size=0.2, random_state=42), label_encoders


def evaluate(model, X_test, y_test, model_type):
    y_pred = model.predict(X_test)

    if model_type == 'classification':
        return {
            'accuracy': float(accuracy_score(y_test, y_pred)),
            'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0)),
        }

    return {
        'mae': float(mean_absolute_error(y_test, y_pred)),
        'mse': float(mean_squared_error(y_test, y_pred)),
        'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
        'r2': float(r2_score(y_test, y_pred)),
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--target-column', type=str, required=True)
    parser.add_argument('--model-type', type=str, default='classification')
    parser.add_argument('--algorithm', type=str, default='RandomForest')
    args = parser.parse_args()

    train_dir = os.environ.get('SM_CHANNEL_TRAIN', '/opt/ml/input/data/train')
    model_dir = os.environ.get('SM_MODEL_DIR', '/opt/ml/model')

    train_files = [f for f in os.listdir(train_dir) if f.endswith('.csv')]
    if not train_files:
        raise FileNotFoundError('No CSV file found in training channel')

    df = load_data(os.path.join(train_dir, train_files[0]))
    (X_train, X_test, y_train, y_test), label_encoders = prepare_data(
        df, args.target_column, args.model_type
    )

    if args.model_type == 'classification':
        model = CLASSIFIERS.get(args.algorithm, CLASSIFIERS['RandomForest'])
    else:
        model = REGRESSORS.get(args.algorithm, REGRESSORS['LinearRegression'])

    model.fit(X_train, y_train)
    metrics = evaluate(model, X_test, y_test, args.model_type)

    joblib.dump(model, os.path.join(model_dir, 'model.pkl'))

    metadata = {
        'metrics': metrics,
        'algorithm': args.algorithm,
        'model_type': args.model_type,
        'target_column': args.target_column,
        'feature_columns': list(X_train.columns),
        'label_encoders': label_encoders,
    }

    with open(os.path.join(model_dir, 'metadata.json'), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print('Training completed:', json.dumps(metrics))
