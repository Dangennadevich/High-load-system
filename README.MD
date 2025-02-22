<h1 align="center">Курс "Распределенные системы"</h1>

<h2 align="center">Построение сервиcа связанного с ВКР: 

"Идентификация искусственно сгенерированных текстов: разработка методов для обеспечения информационной достоверности"</h2>

Для выполнения ДЗ ниже приложена инструкция по пошаговому развертыванию сервиса на пустом Linux-сервере, в частности я арендую такой тут: <a href="https://timeweb.cloud" target="_blank">timeweb.cloud</a>  

* 1) Создаем пользователя
* 2) Настройка сервера для разработки (Miniconda, Poetry, Docker, ect)
* 3) Настройка окружения для работы сервисов
* 4) Поднимаем сервисы (ссылка на инструкции)
* 5) Запрос к сервису

По итогу развертывания сервиса будет доступно API, на который можно будет отправлять текст с целью оценки вероятности того, что текст был сгенерирован AI моделью.

На данный момент вместо модели оценки вероятности сгенерирован ли текст стоит затычка в виде np.random.rand() на GPU сервере, модель будеьт добавлена в результате работы над дипломной работой.

В директориях CPU и GPU серверов находится инструкция по развертыванию сервисов.


<h3 align="center">1. Создаем пользователя и даём права sudo</h3>

<h5 align="left">Для CPU & GPU сервера</h5>

<code>adduser admin</code>

<code>usermod -aG sudo admin</code>

<code>su -- admin</code>


<h3 align="center">2. Настройка сервера для разработки (Miniconda, Poetry, Docker, ect)</h3>

<h5 align="left">Для CPU & GPU сервера</h5>

<b>2.1 Устанавливаем Git, net-tools, PSQL</b>

<code>sudo apt update && sudo apt install git && sudo apt install postgresql-client -y && sudo apt install net-tools</code>

<b>2.2 Копируем репозиторий с проектом</b>

<code>git clone -b checkpoint_3 https://github.com/Dangennadevich/High-load-system.git </code>

<code>mv High-load-system/* .</code>

<b>2.3 Скачиваем Miniconda в корень (~/), Запускаем установку</b>

<code>wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh</code>

<code>bash Miniconda3-latest-Linux-x86_64.sh</code>

<b>2.4 Добавляем переменную окружения </b>

<code>nano ~/.bashrc</code>

<code>PATH="$HOME/miniconda3/bin:$PATH" </code>

<b>2.5 Применим изменения в оболочке </b>

<code>source ~/.bashrc </code>

<b>2.6 Удалим архив  </b>

<code>rm Miniconda3-latest-Linux-x86_64.sh </code>

<b>2.7 Проверим python и conda  </b>

<code>which python</code>
<code>conda --version</code>

<b>2.8 Установим poetry для управления зависимостями и проверим установку  </b>

<code>sudo apt update  && sudo apt install python3-poetry</code>

<code>poetry config virtualenvs.create false</code>

<code>poetry --version</code>

<b>2.9 Создадим и виртуальное окружение без библиотек  </b>

<code>conda create --no-default-packages -n train_env python=3.11</code>

<code>conda activate train_env</code>

<b>2.10 [train_env] Установим Docker  </b>

<a href="https://docs.docker.com/engine/install/ubuntu/" target="_blank">docs.docker.com</a>  

<code>sudo groupadd docker</code>

<code>sudo usermod -aG docker $USER</code>

<code>newgrp docker</code>

<b>2.11 [train_env]  Настроим DNS-серверы для всех контейнеров, добавить в файл </b>

<code>sudo nano /etc/docker/daemon.json</code>

<code>{
  "dns": ["8.8.8.8", "8.8.4.4"]
}</code>

<b>2.12 [train_env]  Перезапустите Docker-демон  </b>

<code> sudo systemctl restart docker </code>

<b>2.12 [train_env]  Проверим установку docker </b>

<code> docker run hello-world </code>


<h3 align="center">3. Общая настройка окружения для работы сервера </h3>

<h5 align="left">Для CPU & GPU сервера</h5>

<b>3.1 [train_env] Команды ниже выполняем из директории cpu_server или gpu_server для CPU и GPU сервера соответсвенно </b>

<code>cd *pu_server/ </code> 

<b>3.3 [train_env] Выполнем инициализацию poetry, устанавливаем библиотеки</b>

<code>poetry install --no-root </code> 

<b>3.4 [train_env]  Создаем файл .env с кредами </b>

<code>nano ~/*pu_server/.env</code>

<code>AWS_SECRET_ACCESS_KEY = 
AWS_ACCESS_KEY_ID = 
POSTGRES_PASSWORD =
RABBITMQ_DEFAULT_USER =
RABBITMQ_DEFAULT_PASS =
</code> 


<h3 align="center">4. Поднимаем сервисы </h3>

<b>4.1 Инструкция для CPU сервера находится в ~/cpu_server/README.MD </b>

<b>4.2 Инструкция для GPU сервера находится в ~/gpu_server/README.MD </b>


<h3 align="center">5. Запрос к сервису (IP CPU сервера) </h3>

<b>Отправляем запрос на сервис. Ожидается ответ.</b>

Ожидается ответ в виде числа, которое может быть оценкой вероятности того, что текст был сгенерирован моделью

<code>curl -X POST "http://92.255.111.116:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}' </code> 

Ответ: {"text":"Привет как дела?","result":"Processed text: Привет как дела?, **probability generated text = 0.013**"}% 

![Alt text](example_post_request_to_server.png)