from pymongo import MongoClient
from config import Config
from bson.objectid import ObjectId
import json
import sqlite3
import os

class MongoDB:
    def __init__(self):
        self.use_sqlite = os.getenv('USE_SQLITE', 'true').lower() == 'true'
        
        if self.use_sqlite:
            # Use SQLite for storing datasets
            self.db_path = 'datasets.db'
            self._init_sqlite()
        else:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.MONGO_DB]
    
    def _init_sqlite(self):
        """Initialize SQLite database for datasets"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                metadata TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id TEXT,
                analysis_type TEXT,
                result TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_dataset(self, data, metadata):
        """Save raw dataset"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO datasets (data, metadata) VALUES (?, ?)',
                (json.dumps(data), json.dumps(metadata))
            )
            conn.commit()
            dataset_id = cursor.lastrowid
            conn.close()
            return str(dataset_id)
        else:
            document = {
                'data': data,
                'metadata': metadata
            }
            result = self.db.datasets.insert_one(document)
            return str(result.inserted_id)
    
    def get_dataset(self, dataset_id):
        """Retrieve dataset"""
        try:
            if self.use_sqlite:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT data, metadata FROM datasets WHERE id = ?', (int(dataset_id),))
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    return {
                        '_id': dataset_id,
                        'data': json.loads(row[0]),
                        'metadata': json.loads(row[1])
                    }
                return None
            else:
                document = self.db.datasets.find_one({'_id': ObjectId(dataset_id)})
                if document:
                    document['_id'] = str(document['_id'])
                    return document
                return None
        except Exception as e:
            print(f"Error retrieving dataset: {e}")
            return None
    
    def save_analysis_result(self, dataset_id, analysis_type, result):
        """Save analysis results"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO analysis_results (dataset_id, analysis_type, result) VALUES (?, ?, ?)',
                (dataset_id, analysis_type, json.dumps(result))
            )
            conn.commit()
            result_id = cursor.lastrowid
            conn.close()
            return str(result_id)
        else:
            document = {
                'dataset_id': dataset_id,
                'analysis_type': analysis_type,
                'result': result
            }
            result = self.db.analysis_results.insert_one(document)
            return str(result.inserted_id)
    
    def get_analysis_results(self, dataset_id):
        """Get all analysis results for a dataset"""
        if self.use_sqlite:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, dataset_id, analysis_type, result FROM analysis_results WHERE dataset_id = ?',
                (dataset_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            results = []
            for row in rows:
                results.append({
                    '_id': str(row[0]),
                    'dataset_id': row[1],
                    'analysis_type': row[2],
                    'result': json.loads(row[3])
                })
            return results
        else:
            results = list(self.db.analysis_results.find({'dataset_id': dataset_id}))
            for result in results:
                result['_id'] = str(result['_id'])
            return results
    
    def close(self):
        if not self.use_sqlite and hasattr(self, 'client'):
            self.client.close()
