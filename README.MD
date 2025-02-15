<h1 align="center">Курс "Распределенные системы"</h1>

<h2 align="center">Построение сервиcа связанного с ВКР: 

"Идентификация искусственно сгенерированных текстов: разработка методов для обеспечения информационной достоверности"</h2>

Для выполнения ДЗ ниже приложена инструкция по пошаговому развертыванию сервиса на пустом Linux-сервере, в частности я арендую такой тут: <a href="https://timeweb.cloud" target="_blank">timeweb.cloud</a>  

* 1) Настройка инфраструктуры сервера
* 2) Настройка сервера для разработки (Miniconda, Poetry, Docker, ect)
* 3) Настройка окружения для обучения модели
* 4) Поднимаем docker-compose
* 5) Проверяем работу сервисов

<h3 align="center">1. Настройка инфраструктуры сервера</h3>

<b>1.1 Закинем публичный ключ на сервер </b>

<code>ssh-copy-id -i ~/.ssh/id_rsa.pub root@server_ip </code>

<b>1.2 Создаем пользователя и даём права sudo</b>

<code>adduser admin</code>

<code>usermod -aG sudo admin</code>

<code>su -- admin</code>

<code>cd ~/</code>

<h3 align="center">2. Настройка сервера для разработки (Miniconda, Poetry, Docker, ect)</h3>

<b>2.1 Устанавливаем Git, net-tools, PSQL</b>

<code>sudo apt update && sudo apt install git && sudo apt install postgresql-client -y && sudo apt install net-tools</code>

<b>2.2 Копируем репозиторий с проектом в папку ~/project/</b>

<code>mkdir project && cd project </code>

<code>git clone -b checkpoint_2 https://github.com/Dangennadevich/HSE_Homeworks.git </code>

<code>mv HSE_Homeworks/* .</code>

<b>2.3 Скачиваем Miniconda, Запускаем установку</b>

<code>cd ~/</code>

<code>wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh</code>

<code>bash Miniconda3-latest-Linux-x86_64.sh</code>

<b>2.4 Добавляем переменную окружения </b>

<code>nano ~/.bashrc</code>

<code>PATH="$HOME/miniconda3/bin:$PATH" </code>

<b>2.5 Применим изменения в оболочке </b>

<code>source ~/.bashrc </code>

<b>2.6 инициализируем Conda  </b>

<code>conda init </code>

<b>2.7 Удалим архив  </b>

<code>rm Miniconda3-latest-Linux-x86_64.sh </code>

<b>2.8 Проверим python и conda  </b>

<code>which python</code>
<code>conda --version</code>

<b>2.9 Установим poetry для управления зависимостями и проверим установку  </b>

<code>pip install poetry</code>

<code>poetry config virtualenvs.create false</code>

<code>poetry --version</code>

<b>2.10 Создадим и виртуальное окружение без библиотек  </b>

<code>conda create --no-default-packages -n train_env python=3.11</code>
<code>conda activate train_env</code>

<b>2.11 Установим Docker  </b>

<code>sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg</code>

<code>echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null</code>

<code>sudo apt-get update</code>

<code>sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin docker-compose </code>

<code>sudo groupadd docker</code>
<code>sudo usermod -aG docker $USER</code>
<code>newgrp docker</code>


<b>2.12 Настроим DNS-серверы для всех контейнеров, добавить в файл </b>

<code>sudo nano /etc/docker/daemon.json</code>

<code>{
  "dns": ["8.8.8.8", "8.8.4.4"]
}</code>


<b>2.13 Перезапустите Docker-демон  </b>

<code> sudo systemctl restart docker </code>

<b>2.14 Проверим установку docker </b>

<code> docker run hello-world </code>



<h3 align="center">3. Настройка окружения для обучения модели </h3>

<b>3.1 Активируем окружение для обучения модели </b>

<code>conda activate train_env </code> 

<b>3.2 Команды ниже выполняем из директории project </b>

<code>cd ~/project/ </code> 

<b>3.3 Выполнем инициализацию poetry, устанавливаем библиотеки</b>

<code>poetry install --no-root </code> 

<b>3.4 Создаем файл .env с кредами </b>

<code>nano ~/project/.env</code>

<code>nAWS_SECRET_ACCESS_KEY = 
AWS_ACCESS_KEY_ID = 
POSTGRES_PASSWORD =
</code> 


<h3 align="center">4. Поднимаем docker-compose </h3>

<b>4.1 Команды ниже выполняем из директории project </b>

<code>cd ~/project/ </code> 

<b>4.2 Создаем docker образ </b>

<code>docker-compose build </code> 

<b>4.3 Запускаем сервисы  </b>

<code>docker-compose up </code> 

<h3 align="center">5. Проверяем работу сервисов </h3>

<b>5.1 Проверим запущены ли контейнеры</b>

<code>docker ps </code> 

<b>5.2 Сервис предсказания сгенерирован ли текст моделью крутится на 8000 порту. В примере временный публичный IP (временный)</b>

<code>http://92.255.111.116:8000</code> 

<b>5.3 Отправляем запрос на сервис. Ожидается ответ в виде числа.</b>

<code>curl -X POST "http://92.255.111.116:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}' </code> 
# Ожидается ответ в виде числа, которое может быть оценкой вероятности того, что текст был сгенерирован моделью

<b>5.4 # MlFlow крутится на 5050 порту</b>

<code>http://92.255.111.116:5050</code> 

<b>5.5 Проверим переменные окружения в контейнере MlFlow и подключение к postgres</b>

<code>docker exec -it mlflow-service bash
env | grep MLFLOW </code> 

<code> apt update && apt install postgresql-client -y
psql -h postgres_db -U postgres -d mlflow_db -p 5432</code> 

<b>5.6 Проверить подключение к PostgeSQL с сервера</b>

<code>psql -h localhost -U postgres -d mlflow_db -p 5432 </code> 

<b>5.7 Проверить логи контейнеров</b>

<code>docker logs nginx_proxy --tail 50</code> 
<code>docker logs mlflow-service --tail 50</code> 
<code>docker logs postgres_db --tail 50</code> 
<code>docker logs fastapi_container --tail 50</code> 
