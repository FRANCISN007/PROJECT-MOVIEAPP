# main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from auth import pwd_context, authenticate_user, create_access_token, get_current_user
from typing import List
from jose import JWTError, jwt
from datetime import datetime, timedelta
from database import engine, Base, get_db
from typing import Optional

import crud, models, schemas, auth

#from passlib.context import CryptContext
#from pydantic import BaseModel

#from fastapi import Depends, FastAPI, HTTPException
#from fastapi.security import OAuth2PasswordRequestForm
# sqlalchemy.orm import Session
#from auth import authenticate_user, create_access_token, get_current_user
#import crud, schema
#from database import engine, Base, get_db
#from auth import pwd_context
#from typing import Optional


Base.metadata.create_all(bind=engine)
# Initialize FastAPI app
app = FastAPI()

#app.include_router(patient_router, prefix ="/Patient", tags =["Patients"])
#app.include_router(doctor_router, prefix ="/Doctor", tags = ["Doctors"])
#app.include_router(appointment_router, prefix="/Appointment", tags= ["Appointment"])



# CORS middleware
#app.add_middleware(
    #CORSMiddleware,
    #allow_origins=["*"],  # Change this based on your frontend URL
    #allow_credentials=True,
    #allow_methods=["*"],
    #allow_headers=["*"],
#)

# Secret key to sign JWT token
#SECRET_KEY = "your-secret-key"
#ALGORITHM = "HS256"
#ACCESS_TOKEN_EXPIRE_MINUTES = 30

@app.post("/Registration", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)
    

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# Movie endpoints
@app.post("/movies/", response_model=schemas.Movie)
def create_new_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return crud.create_movie(db=db, movie=movie, user_id=current_user.id)

@app.get("/movies/", response_model=List[schemas.Movie])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_movies(db=db, skip=skip, limit=limit)

@app.get("/movies/{movie_id}", response_model=schemas.Movie)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    return movie

@app.put("/movies/{movie_id}", response_model=schemas.Movie)
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    existing_movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if existing_movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    if existing_movie.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this movie")
    return crud.update_movie(db=db, movie_id=movie_id, movie=movie)

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    existing_movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if existing_movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    if existing_movie.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this movie")
    crud.delete_movie(db=db, movie_id=movie_id)
    return {"message": "Movie deleted successfully"}

# Rating endpoints
@app.post("/movies/{movie_id}/rate/", response_model=schemas.Rating)
def rate_movie(movie_id: int, rating: schemas.RatingCreate, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    db_rating = crud.create_rating(db=db, rating=rating, movie_id=movie_id)
    return db_rating

@app.get("/movies/{movie_id}/ratings/", response_model=List[schemas.Rating])
def get_ratings_for_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    return crud.get_ratings_for_movie(db=db, movie_id=movie_id)

# Comment endpoints
@app.post("/movies/{movie_id}/comments/", response_model=schemas.Comment)
def create_comment(movie_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    db_comment = crud.create_comment(db=db, comment=comment, movie_id=movie_id)
    return db_comment

@app.get("/movies/{movie_id}/comments/", response_model=List[schemas.Comment])
def get_comments_for_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, please select another one")
    return crud.get_comments_for_movie(db=db, movie_id=movie_id)