import json
import joblib
import os


def model_fn(model_dir):
    return joblib.load(os.path.join(model_dir, 'model.pkl'))


def input_fn(request_body, content_type='application/json'):
    if content_type != 'application/json':
        raise ValueError(f'Unsupported content type: {content_type}')
    data = json.loads(request_body)
    if 'instances' in data:
        return data['instances']
    return [data]


def predict_fn(input_data, model):
    import pandas as pd
    df = pd.DataFrame(input_data)
    predictions = model.predict(df)
    return predictions.tolist()


def output_fn(prediction, accept='application/json'):
    return json.dumps({'predictions': prediction}), accept
