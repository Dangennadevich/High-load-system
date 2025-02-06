<h1 align="center">Курс "Распределенные системы"</h1>

<h2 align="center">Построение сервсина связанного с темой ВКР: "Идентификация искусственно сгенерированных текстов: разработка методов для обеспечения информационной достоверности"</h2>

Для выполнения ДЗ будет приложена инструкция по пошаговому развертыванию сервиса на пустом Linux-сервере, в частности я арендую такой тут: timeweb.cloud

<h3 align="center">1. Настройка инфраструктуры сервера</h3>

<b>1.1 Закинем публичный ключ на сервер </b>
<code>ssh-copy-id -i ~/.ssh/id_rsa.pub root@server_ip </code>

<b>1.2 Создаем пользователя </b>
<code>adduser admin</code>

<b>1.3 Даём права sudo </b>
<code>usermod -aG sudo admin  </code>

<b>1.4 Переключаемся на admin </b>
<code>su -- admin
cd ~/</code>


####################
# Установим Miniconda для локальной разработки

# Скачиваем Miniconda, Запускаем установку
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Добавляем переменную окружения 
nano ~/.bashrc
PATH="$HOME/miniconda3/bin:$PATH"

# После установки активируем conda
source ~/.bashrc

# тут может потребоваться открыть новый терминал и/или перезапустить bash exec bash 
conda init

# Удалим архив
rm Miniconda3-latest-Linux-x86_64.sh

# Проверим python и conda
which python
conda --version

# Создадим и виртуальное окружение без библиотек
conda create --no-default-packages -n train_env python=3.11

####################
# Установим poetry для управления зависимостями и проверим установку

pip install poetry
poetry config virtualenvs.create false
poetry --version


####################
# Docker # 

# Устанавливаем Docker
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# https://docs.docker.com/engine/install/linux-postinstall/
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker

# Настроим DNS-серверы для всех контейнеров
sudo nano /etc/docker/daemon.json

# Добавить без кавычек

"
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
"

# Перезапустите Docker-демон:
sudo systemctl restart docker

# Проверим установку
docker run hello-world

####################

# Установим netstat
sudo apt install net-tools


######################################## 2. Настройка окружения для обучения модели

# Создадим проект
mkdir ~/project && cd ~/project/

# Активируем окружение для обучения модели
conda activate train_env

# Выполнем инициализацию poetry 
poetry init

# Добавим зависимости
poetry add mlflow requests aiohttp aiohttp-jinja2 pika pandas fastapi uvicorn


######################################## 3. Поднимаем сервис

# Создаем Dockerfile

# Создаем образ
docker build -t fastapi_app .

# Запускаем контейнер
docker run -d -p 8000:80 --name fastapi_container fastapi_app

# Устанавливаем net-tools, ушаем что на порту сервера
sudo apt install net-tools
netstat -tuln | grep :8000

# Смотрим логи контейнера
docker logs fastapi_container

# на случай перезапускка
docker rm fastapi_container

# Отправляем запрос в модель, в примере временный публичный IP
curl -X POST "http://103.74.94.14:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}'

# Модель крутится на 8000 порту
http://103.74.94.14:8000