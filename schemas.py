# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    username: str
    #full_name: str

class UserCreate(UserBase):
    full_name: str
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class MovieBase(BaseModel):
    title: str
    description: str

class MovieCreate(MovieBase):
    pass

class MovieUpdate(MovieBase):
    pass

class Movie(MovieBase):
    id: int

class MovieInDB(MovieBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class RatingBase(BaseModel):
    stars: int

class RatingCreate(RatingBase):
    pass

class Rating(RatingBase):
    id: int
    movie_id: int

    class Config:
        orm_mode = True

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    movie_id: int

    class Config:
        orm_mode = True
        

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    full_name: str

class User(UserBase):
    id: int
    full_name: str

class UserInDB(UserBase):
    hashed_password: str

    class Config:
        orm_mode = True
