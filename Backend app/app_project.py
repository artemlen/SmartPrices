from flask import Flask, request, jsonify, render_template
import logging
import pickle
import numpy as np
import pandas as pd
import os

app = Flask(__name__)

# Настройка логирования с UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_latest_model(directory):
    """Находит последнюю обученную модель"""
    try:
        # Получаю самый последний pkl файл
        files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
        return os.path.join(directory, latest_file)
    except:
        return None

# Инициализация модели глобально
model = None

def load_model():
    """Загружает модель при старте приложения"""
    global model
    model_path = get_latest_model('./models')
    if model_path:
        try:
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
            logger.info("Model was founded")
        except Exception as e:
            model = None
    else:
        logger.error("No model found in directory")

# Загружаем модель при старте
load_model()

@app.route('/')
def index():
    return render_template('website.html')

@app.route('/api/numbers', methods=['POST'])
@app.route('/api/numbers', methods=['POST'])
def process_numbers():
    logger.info("Request received for /api/numbers")
    data = request.get_json()

    if not data:
        logger.error("Error: no data received")
        return {'status': 'error', 'message': 'Ошибка: данные не получены'}, 400
    
    try:

        num1 = float(data.get('number1', 0))
        num2 = int(data.get('number2', 1))
        num3 = int(data.get('number3', 1))
        num4 = int(data.get('number4', 1))
        
        logger.info("Input data: "+str(num1)+" "+str(num2)+" "+str(num3)+" "+str(num4))

        if model is None:
            raise RuntimeError("Модель не загружена")

        # Создаем DataFrame с правильными признаками
        input_data = {
            'total_meters': [num1],
            'rooms_count': [num2],
            'floors_count': [num3],
            'floor': [num4]
            
        }
        
        if hasattr(model, 'feature_names_in_') and 'relative_floor' in model.feature_names_in_:
            input_data['relative_floor'] = [num4 / max(1, num3)]
        
        input_df = pd.DataFrame(input_data)
        
        if hasattr(model, 'feature_names_in_'):
            input_df = input_df[list(model.feature_names_in_)]
        
        prediction = int(model.predict(input_df).round(0))

        logger.info("Prediction price: "+str(prediction))
        
        return {
            'status': 'success',
            'price': prediction,
            'formatted_price': prediction,
            'message': f'Предсказанная цена: {prediction}'
        }

    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}", exc_info=True)
        return {
            'status': 'error',
            'message': f'Ошибка: {str(e)}'
        }, 400



if __name__ == '__main__':
    logger.info("Starting server...")
    app.run(host='0.0.0.0', port=8000, debug=True)