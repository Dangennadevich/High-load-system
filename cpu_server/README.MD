<h1 align="center">Проект по распознованию сгенерированного AI моделью текста</h1>

Проект по распознованию AI-сгенерированного текста, основные компоненты:

    * CPU сервер с FastAPI сервером, на котором будет происходить взаимодействие с пользователем.
    
    * GPU сервер с AI моделью, которая проводит скоринг по запросу с CPU сервера.


<h1 align="center">СPU часть проекта</h1>

Запускается на первом сервере архитектуры. Сервис должен ожидать сообщение от пользователей и отправлять запрос на GPU через брокера сообщений rabbitmq. GPU отправляет ответ обратно.


<h1 align="center">Настройка сервисов на СPU</h1>

Выполняется после развертывания необходимого ПО на сервере (~/README.MD, пункт 1-3)


<h3 align="center">1. Поднимаем сервисы </h3>

<b>4.1 Создаем docker образ </b>

<code>docker-compose build </code> 

<b>4.2 Запускаем сервисы  </b>

<code>docker-compose up </code> 

<b>4.3 Создаем обменник в UI версии, у меня поднимается с типом direct  </b>

<code>direct_exchange </code> 


<h3 align="center">2. Проверяем работу сервисов </h3>

<b>2.1 Проверим запущены ли контейнеры</b>

<code>docker ps </code> 

<b>2.2 Сервис предсказания сгенерирован ли текст моделью крутится на 8000 порту. В примере временный публичный IP (временный)</b>

<code>http://92.255.111.116:8000</code> 

<b>2.3 # MlFlow крутится на 5050 порту</b>

<code>http://92.255.111.116:5050</code> 

<b>2.4 Проверим переменные окружения в контейнере MlFlow и подключение к postgres</b>

<code>docker exec -it mlflow-service bash
env | grep MLFLOW </code> 

<code>apt update && apt install postgresql-client -y</code> 

<code>psql -h postgres_db -U postgres -d mlflow_db -p 5432</code> 

<b>2.5 Проверить подключение к PostgeSQL с сервера</b>

<code>psql -h localhost -U postgres -d mlflow_db -p 5432 </code> 

<b>2.6 Проверить логи контейнеров</b>

<code>docker logs nginx_proxy --tail 50</code> 

<code>docker logs mlflow-service --tail 50</code> 

<code>docker logs postgres_db --tail 50</code> 

<code>docker logs fastapi_container --tail 50</code> 

<code>docker logs rabbitmq --tail 50</code> 


<h3 align="center">3. Запрос к сервису </h3>

Выполняется после настройки GPU сервиса (~/gpu_server/README.MD пункты 1-2)

<b>Отправляем запрос на сервис. Ожидается ответ.</b>

Ожидается ответ в виде числа, которое может быть оценкой вероятности того, что текст был сгенерирован моделью

<code>curl -X POST "http://92.255.111.116:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}' </code> 

Ответ: {"text":"Привет как дела?","result":"Processed text: Привет как дела?, **probability generated text = 0.013**"}% 


<h1 align="center">Файлы из директории CPU сервера</h1>

**main.py** - скрипт для запуска сервиса на CPU сервере. 

**Dockerfile** Инструкция для развертывания сервиса на FastAPI

**Docker-compose.yaml** Настраиваем инфраструктуру сервера

**pyproject.toml** Poetry инструкция для настройки виртуального окружения

**/.config** Директория с конфигами для сервисов