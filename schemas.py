from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    class Config:
        orm_mode = True

class AddBook(BaseModel):
    name: str
    author_id: int
    category_id: int
    class Config:
        orm_mode = True
class AddAuthor(BaseModel):
    name: str
    second_name: str
    class Config:
        orm_mode = True
class AddCategory(BaseModel):
    name: str
    class Config:
        orm_mode = True
class TakeBook(BaseModel):
    user_id: int
    book_id: int

    class Config:
        orm_mode = True
class BookResponse(BaseModel):
    id: int
    name: str
    author_id: int
    category_id: int
    class Config:
        orm_mode = True
class CategoryResponse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True

class AuthorResponse(BaseModel):
    id: int
    name: str
    second_name: str
    class Config:
        orm_mode = True
        from_attributes = True

class BookOwnerResponse(BaseModel):
    id: int
    user_id: int
    book_id: int
    class Config:
        orm_mode = True