<h1 align="center">Проект по распознованию сгенерированного AI моделью текста</h1>

Проект по распознованию AI-сгенерированного текста, основные компоненты:

    * CPU сервер с FastAPI сервером, на котором будет происходить взаимодействие с пользователем.

    * GPU сервер с AI моделью, которая проводит скоринг по запросу с CPU сервера.



<h1 align="center">СPU часть проекта</h1>

При помощи Minikube поднимаем FastAPI сервис на первом сервере архитектуры. так же в текущей версии проекта через Minicube поднимаеся вся необходимая архитектура для работы сервиса: PostgreSQL, RabbitMQ. На втором сервере поднимаем сервис, где будет модель.

**/predict** Ручка получает сообщение от пользователя. После получения обрабатывает его - отправляет запрос на GPU через брокера сообщений rabbitmq. Так же сервис записывает уникальный номер запроса в БД и устанавливает статус "Pending".

**/status/{task_id}** По task_id из /predict вытаскиваем статус запроса из БД, результат работы AI модели с GPU сервера.

Связи сервиса GPU с другими объектами архитектуры: 

**CPU >> [RabbitMQ, PSQL DB]**

**CPU >> PSQL DB >> CPU**

<h1 align="center">Настройка сервисов на СPU</h1>

Выполняется после развертывания необходимого ПО на сервере (~/README.MD, пункт 1-3)



<h3 align="center">1. Поднимаем сервисы в директории cpu_server </h3>

<b>1.1 Создаем секреты </b>

<code>kubectl create secret generic app-secrets \
  --from-env-file=.env \
  -n default</code>

<h3 align="left">1.2 Postgres </h3>

<b>1.2.1 Применяем манифесты </b>

<code>kubectl apply -f k8s/postgres-configmap.yaml</code>

<code>kubectl apply -f k8s/postgres-pvc.yaml</code>

<code>kubectl apply -f k8s/postgres-deployment.yaml</code>

<code>kubectl apply -f k8s/postgres-service.yaml</code>

<b>1.2.2 Проверка pods</b>

<code>kubectl get pods -l app=postgres</code>

<b>1.2.3 Проверка поднятых БД</b>

<code>kubectl exec -it deployment/postgres -- psql -U postgres -d mlflow_db -c "\l"</code>

<b>1.2.4 Прокидываем порты (GPU сервер должен иметь доступ к БД для обновления логов (вносит результат)) </b>

<code>kubectl port-forward --address 0.0.0.0 service/postgres 5432:5432 > /dev/null 2>&1 &</code>

<h3 align="left">1.3 RabbitMQ </h3>

<b>1.3.1 Применяем манифесты </b>

<code>kubectl apply -f k8s/rabbitmq-deployment.yaml</code>

<code>kubectl apply -f k8s/rabbitmq-service.yaml</code>

<b>1.3.2 Проверка pods </b>

<code>kubectl get pods -l app=rabbitmq</code>

<b>1.3.3 Прокидываем порты (Брокер нужен для общение с внешним GPU сервером) </b>

<code>kubectl port-forward --address 0.0.0.0 service/rabbitmq 15672:15672 > /dev/null 2>&1 &</code>

<code>kubectl port-forward --address 0.0.0.0 service/rabbitmq 5672:5672 > /dev/null 2>&1 &</code>

<b>1.3.4 Проверяем UI и создаем очередь direct с именем direct_exchange</b>

<code>http://<IP_CPU_SERVER>:15672/#/exchanges</code>

<h3 align="left">1.4 fastapi-service</h3>

<b>1.4.1 Создаем контейнер на основе Dockerfile </b>

<code>eval $(minikube docker-env)</code>

<code>docker build -t fastapi-app:latest .</code>

<b>1.4.2 Применяем манифесты </b>

<code>kubectl apply -f k8s/fastapi-deployment.yaml</code>

<code>kubectl apply -f k8s/fastapi-service.yaml</code>

<b>1.4.3 Проверка pods </b>

<code>kubectl get pods -l app=fastapi-app</code>

<b>1.4.4 Прокидываем порты </b>

<code>kubectl port-forward --address 0.0.0.0 service/fastapi-app 8000:8000 > /dev/null 2>&1 &</code>

<b>1.4.5 Проверка сервиса </b>

<code>curl -v http://localhost:8000</code>

<code>curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет, как дела?"}'</code>

<h3 align="center">2. Проверяем работу сервисов (после поднятия сервисов на GPU) </h3>


<h3 align="left">2.1 Сервис оценки текста - написан ли он при помощи AI </h3>

<b>2.1.1 Пример запроса сгенерирован ли текст "Привет как дела?" моделью. Отправляется по адресу IP_CPU_SERVER:8000/predict :</b>

<code>curl -X POST "http://IP_CPU_SERVER:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}'</code> 

<b>2.1.2 Ожидаем ответ от сервиса - сгенерированный task id, пример ответа:</b>

<code>{"task_id":"64268f77-73d8-4491-b441-4d790b3ccc34"}</code> 

<b>2.1.3 Отправляем запрос с task id для получении ответа от сервера: </b>

<code>curl -X GET "http://IP_CPU_SERVER:8000/status/bdf1fdec-8985-415e-be24-e709216f9257"</code> 

<b>2.1.4 Пример ответа о запросе:</b>

<code>{"task_id":"bdf1fdec-8985-415e-be24-e709216f9257","status":"completed","result":"Processed text: Привет как дела?, probability generated text = 0.527"}</code> 

<b>2.1.5 Если работает только на localhost.. Возможно закрыт порт - откроем его</b>

<code>sudo ufw allow 8000/tcp</code> 

<code>sudo ufw reload</code> 


<h1 align="center"> 3. Файлы из директории CPU сервера</h1>

**main.py** - скрипт для запуска сервиса на CPU сервере. 

**main_no_psql.py** - скрипт для запуска сервиса на CPU сервере без Postgresql с общением CPU & GPU только через RabbitMQ. (Будет удалено)

**Dockerfile** Инструкция для развертывания сервиса на FastAPI

**Docker-compose.yaml** Настраиваем инфраструктуру сервера через Docker-compose

**pyproject.toml** Poetry инструкция для настройки виртуального окружения

**/.config** Директория с конфигами для сервисов

**/k8s** Директория с конфигами/манифестами для сервисов k8s