<h1 align="center">Курс "Распределенные системы"</h1>

<h2 align="center">Построение сервиcа связанного с ВКР: 

"Идентификация искусственно сгенерированных текстов: разработка методов для обеспечения информационной достоверности"</h2>

Для выполнения ДЗ ниже приложена инструкция по пошаговому развертыванию сервиса на пустом Linux-сервере, в частности я арендую такой тут: <a href="https://timeweb.cloud" target="_blank">timeweb.cloud</a>  



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


<h3 align="center">2. Настройка сервера для разработки (Miniconda, Poetry, Docker, ect)</h3>

<b>2.1 Устанавливаем Git</b>

<code>sudo apt update
sudo apt install git </code>

<b>2.2 Копируем репозиторий в папку  ~/project/</b>

<code>mkdir project && cd project </code>
<code>git clone -b checkpoint_2 https://github.com/Dangennadevich/HSE_Homeworks.git </code>
<code>cd .. </code>

<b>2.3 Скачиваем Miniconda, Запускаем установку</b>

<code>wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh </code>

<b>2.4 Добавляем переменную окружения </b>

<code>nano ~/.bashrc
PATH="$HOME/miniconda3/bin:$PATH" </code>

<b>2.5 Применим изменения в оболочке </b>

<code>source ~/.bashrc </code>

<b>2.6 инициализируем Conda  </b>

<code>conda init </code>

<b>2.7 Удалим архив  </b>

<code>rm Miniconda3-latest-Linux-x86_64.sh </code>

<b>2.8 Проверим python и conda  </b>

<code>which python
conda --version </code>

<b>2.9 Создадим и виртуальное окружение без библиотек  </b>

<code>conda create --no-default-packages -n train_env python=3.11 </code>

<b>2.10 Установим poetry для управления зависимостями и проверим установку  </b>

<code>pip install poetry
poetry config virtualenvs.create false
poetry --version</code>

<b>2.11 Установим Docker  </b>

<code>sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
</code>

<b>2.12 Настроим DNS-серверы для всех контейнеров, добавить в файл </b>

<code>sudo nano /etc/docker/daemon.json

{
  "dns": ["8.8.8.8", "8.8.4.4"]
} </code>


<b>2.13 Перезапустите Docker-демон  </b>

<code> sudo systemctl restart docker </code>

<b>2.14 Проверим установку docker </b>

<code> docker run hello-world </code>

<b>2.15 Установим netstat </b>

<code> sudo apt install net-tools </code>



<h3 align="center">3. Настройка окружения для обучения модели </h3>

<b>3.1 Активируем окружение для обучения модели </b>

<code>conda activate train_env </code> 

<b>3.2 Команды ниже выполняем из директории project </b>

<code>cd ~/project/ </code> 

<b>3.3 Выполнем инициализацию poetry </b>

<code>poetry install --no-root </code> 



<h3 align="center">4. Поднимаем сервис </h3>

<b>4.1 Команды ниже выполняем из директории project </b>

<code>cd ~/project/ </code> 

<b>4.2 Создаем docker образ  </b>

<code>docker-compose build </code> 

<b>4.3 Запускаем сервисы  </b>

<code>docker-compose up </code> 

<b>4.4 Слушаем, что на порту сервера  </b>

<code>netstat -tuln | grep :8000 </code> 

<b>4.5 Отправляем запрос в модель, в примере временный публичный IP</b>

<code>curl -X POST "http://103.74.94.14:8000/predict" -H "Content-Type: application/json" -d '{"text": "Привет как дела?"}' </code> 

<b>4.6 # Модель крутится на 8000 порту</b>

<code>http://103.74.94.14:8000 </code> 
