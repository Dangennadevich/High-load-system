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
database = Database(DATABASE_URL)

async def startup():
    await database.connect()

async def shutdown():
    await database.disconnect()

async def connect_to_rabbitmq():
    '''We will establish a connection to RabbitMQ on the CPU server'''
    return await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{CPU_SERVER_IP}/"
    )

async def process_message(message: aio_pika.abc.AbstractMessage):
    '''Message processing'''
    async with message.process():
        data = json.loads(message.body.decode())
        task_id = data["task_id"]
        text = data["text"]

        logger.info(f"Processing task {task_id}: {text}")

        # Generate a random probability, there will be an AI model in the future.
        prob = round(np.random.rand(), 3)
        result = f"Processed text: {data['text']}, probability generated text = {prob}"
        
        logger.info(f"Task {task_id} processed, result: {result}")

        # Update task status
        query = "UPDATE tasks_detecting_generated_text SET status = 'completed', result = :result WHERE task_id = :task_id"
        await database.execute(query, values={"task_id": task_id, "result": result})


async def consume():
    '''Listening to the queue'''
    async with await connect_to_rabbitmq() as connection:
        async with connection.channel() as channel:

            exchange = await channel.declare_exchange(
                "direct_exchange", aio_pika.ExchangeType.DIRECT, durable=True
            )

            # Declaring and linking a queue
            queue = await channel.declare_queue("tasks_pred_gen_txt", durable=True)
            await queue.bind(exchange=exchange, routing_key="tasks_pred_gen_txt")

            # Starting message processing
            await queue.consume(process_message)
            while True:
                await asyncio.sleep(1) # Leaves the service in an endless loop

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