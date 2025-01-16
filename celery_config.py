import json
import time

import redis
from celery import Celery
from celery.schedules import crontab

from models import *

redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
celery_app = Celery(
    "tasks",
    broker=f'redis://{redis_host}:{redis_port}/3',
    backend=f'redis://{redis_host}:{redis_port}/3',
)

celery_app.conf.beat_schedule = {
    "print_message_periodically": {
        "task": "print_message",
        "schedule": crontab(minute="*/1"),
    },
}


@celery_app.task(name='print_message')
def print_message():
    """Задача Celery для периодической печати сообщения."""
    print("Periodic message: Hello from Celery!")
    return time.time()


@celery_app.task
def get_book(book_name, task_number):
    time.sleep(10)
    db = SessionLocal()
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        book_data = db.query(Book).filter(Book.name == book_name).first()
        book = to_dict(book_data)
        book_json = json.dumps(book)
        print(f'celery сделал запрос {book}')
        r.set(task_number, book_json)
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
