import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer

class DataProcessor:
    def __init__(self):
        self.scaler = None
        self.label_encoders = {}
    
    def load_data(self, file_path, file_type='csv'):
        """Load data from file"""
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path)
            elif file_type in ['xlsx', 'xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            return df
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def get_basic_info(self, df):
        """Get basic information about the dataset"""
        info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': int(df.duplicated().sum())
        }
        return info
    
    def get_statistics(self, df):
        """Get statistical summary of the dataset"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'mean': float(df[col].mean()),
                'median': float(df[col].median()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75))
            }
        
        return stats
    
    def handle_missing_values(self, df, strategy='mean'):
        """Handle missing values"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        # Handle numeric columns
        if len(numeric_cols) > 0:
            if strategy == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif strategy == 'median':
                imputer = SimpleImputer(strategy='median')
            elif strategy == 'drop':
                df = df.dropna(subset=numeric_cols)
                return df
            else:
                imputer = SimpleImputer(strategy='constant', fill_value=0)
            
            df[numeric_cols] = imputer.fit_transform(df[numeric_cols])
        
        # Handle categorical columns
        if len(categorical_cols) > 0:
            imputer = SimpleImputer(strategy='most_frequent')
            df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
        
        return df
    
    def encode_categorical(self, df, columns=None):
        """Encode categorical variables"""
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns
        
        for col in columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def normalize_data(self, df, columns=None, method='standard'):
        """Normalize numerical data"""
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns
        
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        else:
            raise ValueError("Method must be 'standard' or 'minmax'")
        
        df[columns] = scaler.fit_transform(df[columns])
        self.scaler = scaler
        
        return df
    
    def get_correlation_matrix(self, df):
        """Calculate correlation matrix for numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return {}
        
        corr_matrix = numeric_df.corr()
        return corr_matrix.to_dict()
    
    def split_features_target(self, df, target_column):
        """Split dataframe into features and target"""
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataframe")
        
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        return X, y
    
    def prepare_for_training(self, df, target_column, test_size=0.2):
        """Prepare data for model training"""
        from sklearn.model_selection import train_test_split
        
        # Split features and target
        X, y = self.split_features_target(df, target_column)
        
        # Split into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        return X_train, X_test, y_train, y_test
