import csv
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel
from models import movies
from models import links
from models import ratings
from models import tags
from database import get_db
from database import engine
from database import Base
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI()
Base.metadata.create_all(bind=engine)

class Movie(BaseModel):
    id: int
    title: str
    genres: str

class Link(BaseModel):
    movieId: int
    imdbId: str
    tmdbId: str

class Rating(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int

class Tag(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int


def load_movies_from_file(file_path: str) -> List[Movie]:
    movies = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            movie = Movie(
                id=int(row['movieId']),
                title=row['title'],
                genres=row['genres']
            )
            movies.append(movie)
    return movies

def load_links_from_file(file_path: str) -> List[Link]:
    links = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            link = Link(
                movieId=int(row['movieId']),
                imdbId=row['imdbId'],
                tmdbId=row['tmdbId']
            )
            links.append(link)
    return links

def load_ratings_from_file(file_path: str) -> List[Rating]:
    ratings = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            rating = Rating(
                userId=int(row['userId']),
                movieId=int(row['movieId']),
                rating=float(row['rating']),
                timestamp=int(row['timestamp'])
            )
            ratings.append(rating)
    return ratings

def load_tags_from_file(file_path: str) -> List[Tag]:
    tags = []
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            tag = Tag(
                userId=int(row['userId']),
                movieId=int(row['movieId']),
                tag=row['tag'],
                timestamp=int(row['timestamp'])
            )
            tags.append(tag)
    return tags

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.on_event("startup")
def startup_event():
    db = next(get_db())

    if not db.query(movies.Movie).first():
        movie_data = load_movies_from_file(r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\movies.csv")
        for movie in movie_data:
            db_movie = movies.Movie(
                id=movie.id,
                title=movie.title,
                genres=movie.genres
            )
            db.add(db_movie)
        db.commit()
        print(f"✅ Loaded {len(movie_data)} movies")

    if not db.query(links.Link).first():
        link_data = load_links_from_file(r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\links.csv")
        for link in link_data:
            db_link = links.Link(
                movieId=link.movieId,
                imdbId=link.imdbId,
                tmdbId=link.tmdbId
            )
            db.add(db_link)
        db.commit()
        print(f"✅ Loaded {len(link_data)} links")

    if not db.query(ratings.Rating).first():
        rating_data = load_ratings_from_file(r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\ratings.csv")
        for rating in rating_data:
            db_rating = ratings.Rating(
                userId=rating.userId,
                movieId=rating.movieId,
                rating=rating.rating,
                timestamp=rating.timestamp
            )
            db.add(db_rating)
        db.commit()
        print(f"✅ Loaded {len(rating_data)} ratings")

    if not db.query(tags.Tag).first():
        tag_data = load_tags_from_file(r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\tags.csv")
        for tag in tag_data:
            db_tag = tags.Tag(
                userId=tag.userId,
                movieId=tag.movieId,
                tag=tag.tag,
                timestamp=tag.timestamp
            )
            db.add(db_tag)
        db.commit()
        print(f"✅ Loaded {len(tag_data)} tags")

    db.close()

@app.get("/movies", response_model=List[Movie])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()

@app.get("/links", response_model=List[Link])
def get_links(db: Session = Depends(get_db)):
    return db.query(Link).all()

@app.get("/ratings", response_model=List[Rating])
def get_ratings(db: Session = Depends(get_db)):
    return db.query(Rating).all()

@app.get("/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()
