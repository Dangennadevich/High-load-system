from fastapi.responses import FileResponse
from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
from typing import List
from io import BytesIO
from func import * # func.py with python def and list for this project
import pandas as pd

app = FastAPI()

class Item(BaseModel):
    name: str
    year: int
    selling_price: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float

class Items(BaseModel):
    objects: List[Item]


@app.post("/predict_item")
def predict_item(item: Item) -> float:
    ''' Функция для предсказания стоимости одного автомобиля


    В функцию на вход передается json методом post, который форматируем в DataFrame
    Этот датафрем обрабатываем с помощтю функции feature_engineering из func.py
    Далее def pred из func.py делаем предсказания стоимости автомобиля
    '''
    df = pd.DataFrame([dict(item)])
    X, y = feature_engineering(df)

    predict_price = pred(X)
    return predict_price


@app.post("/predict_items")
def predict_items(file: UploadFile) -> FileResponse:
    ''' Функция для предсказания стоимости множества автомобилей из csv файла

    В функцию методом post поступает csv файол, который причесывается и переводится в DataFrame формат
    Далее этап feature engineering с помощтю функции feature_engineering из func.py
    Затем предсказания для нескольких машин pred_multi_values из func.py
    '''
    content = file.file.read() #считываем байтовое содержимое
    buffer = BytesIO(content) #создаем буфер типа BytesIO
    df_csv = pd.read_csv(buffer, sep=';')

    buffer.close()
    file.close()  # закрывается именно сам файл

    X, y = feature_engineering(df_csv) # Обрабатываем данные, выведим отдельно Y - для доработки проекта
    predict_price = pred_multi_values(X) # Предсказанмя

    df_csv['pred_price'] = predict_price
    df_csv.to_csv('data_with_pred_price.csv')

    response = FileResponse(path='data_with_pred_price.csv', media_type='text/csv', filename='data_with_pred_price.csv')

    return response
