import numpy as np
import aio_pika
import asyncio
import json
import uuid
import os

load_dotenv()

RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")


# Функция для подключения к RabbitMQ
async def connect_to_rabbitmq():
    return await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@SOME_IP/"
        )

# Функция для обработки сообщения
async def process_message(message: aio_pika.abc.AbstractMessage):
    async with message.process():
        data = json.loads(message.body.decode())

        # Тут будет вызов нейросетки
        prob = round(np.random.rand(), 3)
        result = f"Processed text: {data['text']}, probability generated text = {prob}"

        # Ответ отправляется в очередь "results" с тем же correlation_id
        await send_result(message.correlation_id, result)

# Функция для отправки результата обратно в очередь
async def send_result(correlation_id, result):
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=result.encode(),
            correlation_id=correlation_id  # Ответ с тем же correlation_id
        ),
        routing_key="results_pred_gen_txt", # Отправляем в очередь
    )

    await connection.close()

# Функция для получения сообщений из очереди
async def consume():
    connection = await connect_to_rabbitmq()
    channel = await connection.channel()

    queue = await channel.declare_queue("tasks_pred_gen_txt", durable=True)
    await queue.consume(process_message)

# Запуск сервера B
async def main():
    await consume()

# Запуск сервера B
if __name__ == "__main__":
    asyncio.run(main())
