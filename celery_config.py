import json
import os
import time

import redis
from celery import Celery
from celery.schedules import crontab

from models import Book, SessionLocal, to_dict

rabbitmq_host = os.getenv("RABBITMQ_HOST")
redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)
BROKER_URL = f'amqp://guest:guest@rabbitmq:{rabbitmq_host}//'

celery_app = Celery(
    "tasks",
    broker=BROKER_URL,
    backend=f'redis://{redis_host}:{redis_port}/3',
)

# celery_app.conf.beat_schedule = {
#     "print_message_periodically": {
#         "task": "print_message",
#         "schedule": crontab(minute="*/1"),
#     },
# }
#
#
# @celery_app.task(name='print_message')
# def print_message():
#     """Задача Celery для периодической печати сообщения."""
#     print("Periodic message: Hello from Celery!")
#     return time.time()


@celery_app.task
def get_book(book_name):
    time.sleep(10)
    db = SessionLocal()
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        cache_key = f"{book_name}"
        cached_data = redis_client.get(cache_key)
        if cached_data:
            decoded_string = cached_data.decode('utf-8')
            return json.loads(decoded_string)

        book_data = db.query(Book).filter(Book.name == book_name).first()
        book_dict = to_dict(book_data)
        book = str(book_dict)
        print(f'celery сделал запрос {book}')
        r.setex(book_name, 60, book)
        print(book)
        return book
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
