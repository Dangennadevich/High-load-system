import numpy as np
import aio_pika
import asyncio
import logging
import json
import os

from databases import Database
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("[Setup] Getting .env settings")

load_dotenv()

RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")

if not RABBITMQ_DEFAULT_USER or not RABBITMQ_DEFAULT_PASS:
    raise ValueError("RABBITMQ_DEFAULT_USER and RABBITMQ_DEFAULT_PASS must be set in the .env file")

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USER = os.getenv("POSTGRES_USER")
if not POSTGRES_PASSWORD or not POSTGRES_USER:
    raise ValueError("POSTGRES_PASSWORD and POSTGRES_USER must be set in the .env file")

CPU_SERVER_IP = os.getenv("CPU_SERVER_IP")
if not CPU_SERVER_IP:
    raise ValueError("CPU_SERVER_IP must be set in the .env file")

# Connect to PostgreSQL
logger.info("[Setup] Connect to PostgreSQL")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{CPU_SERVER_IP}:5432/rabbitmq_db"
database = Database(DATABASE_URL, min_size=2, max_size=10)

async def startup():
    await database.connect()

async def shutdown():
    await database.disconnect()

async def connect_to_rabbitmq():
    '''We will establish a connection to RabbitMQ on the CPU server'''
    try:
        logger.info(f"Connecting to RabbitMQ at {CPU_SERVER_IP}...")
        connection = await aio_pika.connect_robust(
            f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{CPU_SERVER_IP}/"
        )
        logger.info("Successfully connected to RabbitMQ!")
        return connection
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise


async def process_message(message: aio_pika.abc.AbstractMessage):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            
            # Проверяем, что данные — это плоский список [task_id, text]
            if isinstance(data, list) and len(data) >= 2:
                task_data = data[0]  # Первый элемент — это [task_id, text]
                task_id = task_data[0]  # task_id — строка
                text = task_data[1]     # text — строка
            else:
                logger.error("Invalid data format. Expected [task_id, text].")
                return

            logger.info(f"Processing task {task_id}: {text}")

            # Ваша логика обработки (например, генерация вероятности)
            prob = round(np.random.rand(), 3)
            result = f"Processed text: {text}, probability = {prob}"
            
            # Обновление статуса в базе данных
            query = "UPDATE tasks_detecting_generated_text SET status = 'completed', result = :result WHERE task_id = :task_id"
            await database.execute(query, values={"task_id": task_id, "result": result})
        except Exception as e:
            logger.error(f"Database error: {e}")


async def consume():
    async with await connect_to_rabbitmq() as connection:
        async with connection.channel() as channel:
            exchange = await channel.declare_exchange("celery", aio_pika.ExchangeType.DIRECT, durable=True)
            
            # Слушаем очередь tasks_pred_gen_txt
            queue = await channel.declare_queue("tasks_pred_gen_txt", durable=True)
            await queue.bind(exchange=exchange, routing_key="tasks_pred_gen_txt")
            
            await queue.consume(process_message)
            await asyncio.Future()  # Бесконечный цикл

def main():
    '''Запуск сервиса'''
    loop = asyncio.get_event_loop()
    loop.run_until_complete(startup())  # Connect to db
    try:
        loop.run_until_complete(consume())
    except KeyboardInterrupt:
        print("Остановка сервиса...")
    finally:
        # Closing all asynchronous resources
        loop.run_until_complete(asyncio.sleep(0))
        loop.close()

if __name__ == "__main__":
    main()