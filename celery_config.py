import redis
from celery import Celery
from models import *
redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
celery_app = Celery(
    "tasks",
    broker=f'redis://{redis_host}:{redis_port}/3',
    backend=f'redis://{redis_host}:{redis_port}/3',
)



@celery_app.task
def get_book(book_name):
    """Задача Celery для получения книги из базы данных."""
    db = SessionLocal()
    try:
        book_data = db.query(Book).filter(Book.name == book_name).first()
        book = to_dict(book_data)
        print(f'celery сделал запрос {book}')
        return book
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


