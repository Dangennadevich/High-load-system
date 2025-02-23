<h1 align="center">Проект по распознованию сгенерированного AI моделью текста</h1>

Проект по распознованию AI-сгенерированного текста, основные компоненты:

    * CPU сервер с FastAPI сервером, на котором будет происходить взаимодействие с пользователем.

    * GPU сервер с AI моделью, которая проводит скоринг по запросу с CPU сервера.


<h1 align="center">СPU часть проекта</h1>

Запускает FastAPI сервис на первом сервере архитектуры. 

**/predict** Ручка получает сообщение от пользователя. После получения обрабатывает его - отправляет запрос на GPU через брокера сообщений rabbitmq. Так же сервис записывает уникальный номер запроса в БД и устанавливает статус "Pending".

**/status/{task_id}** По task_id из /predict вытаскиваем статус запроса из БД, результат работы AI модели с GPU сервера.


<h1 align="center">Настройка сервисов на СPU</h1>

Выполняется после развертывания необходимого ПО на сервере (~/README.MD, пункт 1-3)


<h3 align="center">1. Поднимаем сервисы </h3>

<b>4.1 Создаем docker образ </b>

<code>docker-compose build </code> 

<b>4.2 Запускаем сервисы  </b>

<code>docker-compose up </code> 

<b>4.3 Создаем обменник в UI версии, у меня поднимается с типом direct  </b>

<code>http://CPU_IP:15672/#/exchanges</code> 

<code>direct_exchange </code> 


<h3 align="center">2. Проверяем работу сервисов (после поднятия сервисов на GPU) </h3>


<h5 align="left">2.1 Сервис оценки текста - написан ли он при помощи AI </h5>

<b>2.1.1 Пример запроса сгенерирован ли текст "Привет как дела?" моделью. Отправляется по адресу IP_CPU_SERVER:8000/predict :</b>

<code>curl -X POST "http://IP_CPU_SERVER:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}'</code> 

<b>2.1.2 Ожидаем ответ от сервиса - сгенерированный task id, пример ответа:</b>

<code>{"task_id":"64268f77-73d8-4491-b441-4d790b3ccc34"}</code> 

<b>2.1.3 Отправляем запрос с task id для получении ответа от сервера: </b>

<code>curl -X GET "http://IP_CPU_SERVER:8000/status/bdf1fdec-8985-415e-be24-e709216f9257"</code> 

<b>2.1.4 Пример ответа о запросе:</b>

<code>{"task_id":"bdf1fdec-8985-415e-be24-e709216f9257","status":"completed","result":"Processed text: Привет как дела?, probability generated text = 0.527"}</code> 


<h5 align="left">2.2 RabbitMQ </h5>

<b>2.2.1 UI сервиса</b>

<code>http://IP_CPU_SERVER:15672/#/exchanges </code> 

<b>2.2.2 Проверяем логирование пользовательских запросов в БД </b>

<code>docker exec -it postgres_db psql -U postgres -d rabbitmq_db</code> 

<code>select * from tasks_detecting_generated_text;</code> 


<h5 align="left">2.3 PostgeSQL </h5>

<b>2.3.1 Проверить подключение к PostgeSQL с сервера (бд mlflow_db)</b>

<code>psql -h localhost -U postgres -d mlflow_db -p 5432 </code> 


<h5 align="left">2.4 MlFlow </h5>

<b>2.2.1 MlFlow крутится на 5050 порту</b>

<code>http://IP_CPU_SERVER:5050</code> 

<b>2.2.2 Проверим переменные окружения в контейнере MlFlow и подключение к postgres</b>

<code>docker exec -it mlflow-service bash
env | grep MLFLOW </code> 

<code>apt update && apt install postgresql-client -y</code> 

<code>psql -h postgres_db -U postgres -d mlflow_db -p 5432</code> 


<h5 align="left">2.5 Общие проверки </h5>

<b>2.6 Проверить логи контейнеров</b>

<code>docker logs container_name --tail 50</code> 


<h1 align="center"> 3. Файлы из директории CPU сервера</h1>

**main.py** - скрипт для запуска сервиса на CPU сервере. 

**main_no_psql.py** - скрипт для запуска сервиса на CPU сервере без Postgresql с общением CPU & GPU только через RabbitMQ. (Будет удалено)

**Dockerfile** Инструкция для развертывания сервиса на FastAPI

**Docker-compose.yaml** Настраиваем инфраструктуру сервера

**pyproject.toml** Poetry инструкция для настройки виртуального окружения

**/.config** Директория с конфигами для сервисов