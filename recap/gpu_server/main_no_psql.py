import numpy as np
import aio_pika
import asyncio
import json
import uuid
import os
from dotenv import load_dotenv

import logging

# IP-server with RabbitMQ
CPU_SERVER_IP = '178.253.40.134'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

RABBITMQ_DEFAULT_USER = os.getenv("RABBITMQ_DEFAULT_USER")
RABBITMQ_DEFAULT_PASS = os.getenv("RABBITMQ_DEFAULT_PASS")

async def connect_to_rabbitmq():
    '''We will establish a connection to RabbitMQ on the CPU server'''
    return await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{CPU_SERVER_IP}/"
    )

async def process_message(message: aio_pika.abc.AbstractMessage):
    '''Message processing'''
    async with message.process():
        data = json.loads(message.body.decode())

        logger.info(f"Processing message: {data}")

        # We generate a random probability, there will be an AI model in the future.
        prob = round(np.random.rand(), 3)
        result = f"Processed text: {data['text']}, probability generated text = {prob}"
        
        logger.info(f"Send message: {result}")

        await send_result(message.correlation_id, result)

async def send_result(correlation_id, result):
    '''Send result to CPU'''
    try:
        async with await aio_pika.connect_robust(
            f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{CPU_SERVER_IP}/"
        ) as connection:
            async with connection.channel() as channel:
                # We are announcing the direct_exchange exchanger
                exchange = await channel.declare_exchange(
                    "direct_exchange", 
                    aio_pika.ExchangeType.DIRECT, 
                    durable=True
                )

                # Send message
                await exchange.publish(
                    aio_pika.Message(
                        body=result.encode(),
                        correlation_id=correlation_id,
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                    ),
                    routing_key="results_pred_gen_txt", # Queue for GPU Server responses
                )

                logger.info(f"Result sent with ID: {correlation_id}")
                
    except Exception as e:
        logger.error(f"Error sending result: {e}")
        raise

async def consume():
    '''Listening to the queue'''
    async with await connect_to_rabbitmq() as connection:
        async with connection.channel() as channel:

            # Declaring and linking a queue
            queue = await channel.declare_queue("tasks_pred_gen_txt", durable=True)
            await queue.bind(exchange="direct_exchange", routing_key="tasks_pred_gen_txt")
            
            # Starting message processing
            await queue.consume(process_message)
            while True:
                await asyncio.sleep(1) # Leaves the service in an endless loop
                
def main():
    '''Запуск сервиса'''
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
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