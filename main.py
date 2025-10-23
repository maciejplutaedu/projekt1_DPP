from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models
from database import SessionLocal, init_db


app = FastAPI()
init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Database connected!"}


@app.get("/movies")
def get_movies(db: Session = Depends(get_db)):
    return db.query(models.Movie).all()


@app.get("/links")
def get_links(db: Session = Depends(get_db)):
    return db.query(models.Link).all()


@app.get("/ratings")
def get_ratings(db: Session = Depends(get_db)):
    return db.query(models.Rating).all()


@app.get("/tags")
def get_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).all()
