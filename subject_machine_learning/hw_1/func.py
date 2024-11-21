import pandas as pd
import numpy as np
import re
import pickle

with open('ohe.pickle', 'rb') as f:
   ohe = pickle.load(f)

with open('StandardScaler.pickle', 'rb') as f:
   scaler = pickle.load(f)

with open('ml_model_car_price.pickle', 'rb') as f:
   ml = pickle.load(f)

df_fillna = pd.read_csv('df_fillna.csv', sep=';')

num_features = [
    'year', 'km_driven', 'mileage', 'engine', 'max_power', 'torque_upd',
    'max_torque_rpm', 'car_age', 'km_driven_per_year', 'mean_own_year', 'pover_per_V_engine'
]

categorical_cols = ['fuel', 'transmission', 'owner', 'seats', 'model']

drop_old_colum = ['name', 'seller_type']

def pred(X: pd.DataFrame) -> float:
    '''Функция выдающая предсказания модели для объектов из DataFrame

    :param X:
    DataFrame with cars
    :return:
    model predict price for car in DataFrame
    '''
    pred = ml.predict(X)
    pred = pred[0]
    return pred

def pred_multi_values(X: pd.DataFrame)-> np.array:
    '''Функция выдающая предсказания модели для 1 объекта из DataFrame

    :param X:
    DataFrame with 1 car
    :return:
    model predict price for car
    '''
    pred = ml.predict(X)
    return pred


def row_to_float(x: str) -> [float, None]:
    '''
    input -> row with words and int/float numbers // null
    out -> float // null for null
    '''
    # Оставим цифры и разделитель
    x = re.sub(r'[^0-9.]', '', str(x))

    # Что бы не падать на пропусках
    try:
        return float(x)
    except ValueError:
        return None


def mean_tear_own(elem: str) -> int:
    ''' Функция для реализации подсчета среднего срока владения

    Переведем строчное значение "Кол-во владельцев" в целое число и сократим кол-во значений переменной

    input <- cat features str: owner number
    output -> cat features int: owner number
    '''
    if elem == 'First Owner':
        return 1
    if elem == 'Second Owner':
        return 2
    if (elem == 'Third Owner') | (elem == 'Test Drive Car'):
        return 3
    else:
        return 4

def optim_owner(val: str) -> str:
    '''
    input <- Cat feature owner
    ouput -> optimizated feature owner
    '''
    if val in ['First Owner', 'Second Owner']:
        return val
    else:
        return 'Third & Above Owner'

def torque_split(col_df):
    '''
    input -> col with values like '260 Nm at 1800-2200 rpm'
    out -> col whith torque, col with max_torque_rpm max_torque_rpm
    '''
    torque = list()  # Тут первое значение = torque
    max_torque_rpm = list()  # Тут последнее значение = max_torque_rpm

    for row in col_df:
        # Для каждого значения - составим список из 2-3 цифр
        if row is not None:
            row = str(row).replace(',', '')  # 24@ 1,900-2,750(kgm@ rpm)	 -> 24@ 1900-2750(kgm@ rpm)
            row_whith_numbers = re.sub(r'[^0-9.]', ' ', str(row)).split()

            # Если у нас вернулась пустота - что бы не падать в ошибку
            try:
                torque.append(float(row_whith_numbers[0]))
            except:
                torque.append(None)

            # Если у нас вернулась пустота - что бы не падать в ошибку
            try:
                max_torque_rpm.append(float(row_whith_numbers[-1]))
            except:
                max_torque_rpm.append(None)

        else:
            torque.append(None)
            max_torque_rpm.append(None)

    return torque, max_torque_rpm

def nan_input(df_input: pd.DataFrame, df_fillna: pd.DataFrame = df_fillna) -> pd.DataFrame:
    '''Функция заполняет пропуски в входном датафрейме на основе второго входного датафрейма

    Для заполнения df_input используются значения из матрицы df_fillna,
    на выход отдаем экземпляр без пропусков df_input

    Заполнение происходит по следующим правилам:
    Для столбца Х находим пропуск - смотрим на год машины, в строчке где нашли пропуск.
    Далее из таблицы df_fillna вытягиваем значение по столбцу Х и этому же году.
    Это медианое значение - им заполним пропуск.
    '''
    df = df_input.copy()
    col_to_fillna = ['mileage', 'engine', 'seats', 'torque_upd', 'max_torque_rpm', 'max_power']
    for col in col_to_fillna: # для каждой колонки
        for i in range(len(df)): # для каждой строчки
            if pd.isna(df[col][i]): #math.isnan(df[col][i]) == True: # если в ячейке пропуск
                year = df['year'][i] # смотрим на год
                # заполняем соответсвующим значением медианы столбца по году из df_fillna
                if year < 1996: # до 1996 мало данных - заполним ближайшем соседом 1994
                    year = 1994
                    df[col][i] = df_fillna.loc[year][col]
                else:
                    df[col][i] = df_fillna.loc[year][col]
    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    # Обработаем mileage engine и max_power, torque
    df['mileage'] = df['mileage'].apply(lambda x: row_to_float(x))
    df['engine'] = df['engine'].apply(lambda x: row_to_float(x))
    df['max_power'] = df['max_power'].apply(lambda x: row_to_float(x))
    df['torque_upd'], df['max_torque_rpm'] = torque_split(df['torque'])

    # Пропуски
    df = nan_input(df)

    # Лет машине
    max_year = 2021
    df['year'].max() == df['year'].max()
    df['car_age'] = max_year - df['year']

    # Средний пробег за год ползования
    df['km_driven_per_year'] = round(df['km_driven'] / (max_year - df['year']))

    # Марка авто
    df['model'] = df['name'].apply(lambda x: x.split()[0])

    # Продавцы
    df['seller_individual_flg'] = df['seller_type'].apply(lambda x: 1 if x == 'Individual' else 0)

    # Средний срок владения
    df['mean_own_year'] = df['owner'].apply(lambda x: mean_tear_own(x))
    df['mean_own_year'] = df['car_age'] / df['mean_own_year']

    # Оптимиируем фичу с владельцем
    df['owner'] = df['owner'].apply(lambda x: optim_owner(x))

    # engine / max_power
    df['pover_per_V_engine'] = df['max_power'] / (df['engine'] * 0.001)

    # Возведем в квадрат
    for col in num_features:
        new_col = col + '_sqr'
        df[new_col] = round(df[col] ** 2, 2)
        df[new_col] = round(df[col] ** 2, 2)

    # Дропнем старые колонки
    df = df.drop(drop_old_colum, axis=1)
    df = df.drop('torque', axis=1)
    df = df.drop('year', axis=1)

    # split
    X = df.drop('selling_price', axis=1).copy()
    y = df['selling_price'].values

    # OHE
    X_ohe = ohe.transform(X[categorical_cols])

    X_ohe = pd.DataFrame(X_ohe)  # Преобразуем результат в DataFrame
    X_ohe.columns = list(ohe.get_feature_names_out(categorical_cols))

    X = pd.concat([X.drop(categorical_cols, axis=1), X_ohe], axis=1)  # Объедините DataFrame

    # Standart scaller
    X = scaler.transform(X=X)

    return X, y