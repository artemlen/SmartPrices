# Импорт для Linear_model_train
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
import datetime
import os
import pickle
import logging

from prepare import Prepare_data

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/train.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def save_model(output_dir='models', koefs_dir = 'koefs', name="linear"):

    logger.info(f"Начало обучения модели. Выходная директория: {output_dir}, имя модели: {name}")
    
    try:

        df = Prepare_data()
        
        # Разделение на признаки и целевую переменную
        X_train, X_test, y_train, y_test = train_test_split(
            df.drop(columns=['Цена']), 
            df['Цена'], 
            test_size=0.2, 
            random_state=42
        )
        logger.info(f"Данные разделены. X_train: {X_train.shape}, X_test: {X_test.shape}")
        
        # Обучение модели
        logger.info("Обучение модели LinearRegression...")
        modelLR = LinearRegression()
        modelLR.fit(X_train, y_train)
        logger.info("Модель успешно обучена")

        # Получаем коэффициенты модели
        coefficients = modelLR.coef_
        abs_coefficients = np.abs(coefficients)
        importance_percentage = 100 * abs_coefficients / abs_coefficients.sum()
        feature_names = X_train.columns

        # Сохраняем коэффициенты в бинарный файл
        percentage_of_tags = []
        for feature, percentage in zip(feature_names, importance_percentage):
            percentage_of_tags.append({"tag": feature, "percent": round(float(percentage), 0)})
        with open(koefs_dir+'/'+'koefs.pkl', 'wb') as f:
            pickle.dump(percentage_of_tags, f)
        print(percentage_of_tags)
        

        
        # Предсказания и метрики
        predictions = modelLR.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        logger.info(f"Метрики модели - MSE: {mse:.2f}, R2: {r2:.2f}")
        
        # Сохранение модели
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, f'{name}_model.pkl')
        
        with open(model_path, 'wb') as file:
            pickle.dump(modelLR, file)
        logger.info(f"Модель сохранена по пути: {model_path}")
        
        logger.info("Процесс обучения и сохранения модели завершен успешно")
        
    except FileNotFoundError as e:
        logger.error(f"Ошибка: файл не найден - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при обучении модели: {str(e)}")
        raise

save_model()