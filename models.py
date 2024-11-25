from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@db:5432/library"

# Создание синхронного движка SQLAlchemy
engine = create_engine(DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Category(Base):
    __tablename__ = "Category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

class Author(Base):
    __tablename__ = "Author"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    second_name = Column(String, index=True)

class Book(Base):
    __tablename__ = "Book"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey(Category.id), index=True)
    author_id = Column(Integer, ForeignKey(Author.id), index=True)


class AuthorBook(Base):
    __tablename__ = "AuthorBook"
    book_id = Column(Integer, ForeignKey(Book.id), index=True, primary_key=True)
    author_id = Column(Integer, ForeignKey(Author.id), index=True)

class BookOwner(Base):
    __tablename__ = "BookOwner"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id), index=True)
    book_id = Column(Integer, ForeignKey(Book.id), index=True)

Base.metadata.create_all(bind=engine)