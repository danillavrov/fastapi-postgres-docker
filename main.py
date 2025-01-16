import json
import random
from typing import List

import redis
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from celery_config import get_book
from models import *
from schemas import *

SENTRY_DSN = os.getenv("SENTRY_DSN")
redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)



sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
)
app = FastAPI()


# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/books/{book_name}")
def get_book_by_name(book_name: str, db: Session = Depends(get_db)):
    random_int = random.randint(1, 100000)
    task_number = str(random_int)
    cache_key = f'{book_name}'
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print('данные взяты из кэша')
        decoded_string = cached_data.decode('utf-8')
        data_dict = json.loads(decoded_string)
        print(data_dict)
        redis_client.setex(task_number, 60, decoded_string)
        return {"task_number": task_number, "status": "ready by cache"}
    print('запускаем запрос celery')

    task_number = str(random_int)
    get_book.delay(book_name, task_number)
    return {"task_number": task_number, "status": "started"}

@app.get("/tasks/{task_number}")
def get_result(task_number: str, db: Session = Depends(get_db)):
    result_red = redis_client.get(task_number)
    if result_red:
        result = result_red.decode('utf-8')
        data_dict = json.loads(result)
        name = data_dict['name']
        data_json = json.dumps(data_dict)
        redis_client.setex(name, 60, data_json)
        return json.loads(result)
    else:
        return('результата пока нет, попробуйте позже')

# Добавление нового пользователя
@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email}
@app.post("/takebook/", response_model=dict)
def take_book(act: TakeBook, db: Session = Depends(get_db)):
    new_record = BookOwner(user_id=act.user_id, book_id=act.book_id)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return {"succes"}


# Удаление пользователя по ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}


# Получение списка всех пользователей
@app.get("/users/", response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
@app.get("/book_owners/", response_model=List[BookOwnerResponse])
def read_bookowners(db: Session = Depends(get_db)):
    bookowners = db.query(BookOwner).all()
    return bookowners

@app.get("/books/", response_model=List[BookResponse])
def read_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

@app.post("/books/", response_model=dict)
def add_book(book: AddBook, db: Session = Depends(get_db)):
    new_book = Book(name=book.name, author_id=book.author_id, category_id=book.category_id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"id": new_book.id, "name": new_book.name, "author": new_book.author_id, "category": new_book.category_id}

@app.get("/authors/", response_model=List[AuthorResponse])
def read_authors(db: Session = Depends(get_db)):
    authors = db.query(Author).all()
    return authors

@app.post("/authors/", response_model=dict)
def add_author(author: AddAuthor, db: Session = Depends(get_db)):
    new_author = Author(name=author.name, second_name=author.second_name)
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return {"id": new_author.id, "name": new_author.name, "second_name": new_author.second_name}

@app.get("/categories/", response_model=List[CategoryResponse])
def read_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@app.post("/categories/", response_model=dict)
def add_category(category: AddCategory, db: Session = Depends(get_db)):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"id": new_category.id, "name": new_category.name}

@app.delete("/book_owners/{user_id}/{book_id}")
def delete_user(user_id: int, book_id: int, db: Session = Depends(get_db)):
    record = db.query(BookOwner).filter(BookOwner.user_id == user_id).filter(BookOwner.book_id == book_id).first()
    db.delete(record)
    db.commit()
    return {"detail": "record deleted"}
