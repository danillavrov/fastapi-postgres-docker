from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import *
from models import *
from typing import List

app = FastAPI()

# Получение сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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



