import csv
from contextlib import asynccontextmanager
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
from sqlalchemy import select
from fastapi import Depends, FastAPI, HTTPException


app = FastAPI()
Base.metadata.create_all(bind=engine)

class Movie(BaseModel):
    id: int
    title: str
    genres: str

class Link(BaseModel):
    id: int | None = None
    movieId: int
    imdbId: str
    tmdbId: str

class Rating(BaseModel):
    id: int | None = None
    userId: int
    movieId: int
    rating: float
    timestamp: int

class Tag(BaseModel):
    id: int | None = None
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Start---
    db = next(get_db())
    try:
        if not db.scalars(select(movies.Movie)).first():
            movie_data = load_movies_from_file(r"data\movies.csv")
            db_movies = [
                movies.Movie(id=m.id,
                             title=m.title,
                             genres=m.genres)
                for m in movie_data
            ]
            db.bulk_save_objects(db_movies)
            db.commit()
            print(f"{len(movie_data)} movies")

        if not db.scalars(select(links.Link)).first():
            link_data = load_links_from_file(r"data\links.csv")
            db_links = [
                links.Link(
                    movieId=l.movieId,
                    imdbId=l.imdbId,
                    tmdbId=l.tmdbId
                )
                for l in link_data
            ]
            db.bulk_save_objects(db_links)
            db.commit()
            print(f"Loaded {len(link_data)} links")

        if not db.scalars(select(ratings.Rating)).first():
            rating_data = load_ratings_from_file(r"data\ratings.csv")
            db_ratings = [
                ratings.Rating(
                    userId=r.userId,
                    movieId=r.movieId,
                    rating=r.rating,
                    timestamp=r.timestamp
                )
                for r in rating_data
            ]
            db.bulk_save_objects(db_ratings)
            db.commit()
            print(f"Loaded {len(rating_data)} ratings")

        if not db.scalars(select(tags.Tag)).first():
            tag_data = load_tags_from_file(r"data\tags.csv")
            db_tags = [
                tags.Tag(
                    userId=t.userId,
                    movieId=t.movieId,
                    tag=t.tag,
                    timestamp=t.timestamp
                )
                for t in tag_data
            ]
            db.bulk_save_objects(db_tags)
            db.commit()
            print(f"Loaded {len(tag_data)} tags")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()
    yield




app = FastAPI(lifespan=lifespan)


#
#
#   Movies
#
#
@app.get("/movies", response_model=List[Movie])
def get_movies(db: Session = Depends(get_db)):
    db_movies = db.scalars(select(movies.Movie)).all()
    return db_movies

@app.post("/movies", response_model=Movie)
def create_movie(movie: Movie, db: Session = Depends(get_db)):
    db_movie = movies.Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.get("/movies/{movie_id}", response_model=Movie)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.get(movies.Movie, movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@app.put("/movies/{movie_id}", response_model=Movie)
def update_movie(movie_id: int, movie: Movie, db: Session = Depends(get_db)):
    db_movie = db.get(movies.Movie, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    for key, value in movie.model_dump().items():
        setattr(db_movie, key, value)

    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.get(movies.Movie, movie_id)
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    db.delete(db_movie)
    db.commit()
    return {"message": "Movie deleted successfully"}

#
#
#   LINKS
#
#

@app.get("/links", response_model=List[Link])
def get_links(db: Session = Depends(get_db)):
    return db.scalars(select(links.Link)).all()

@app.post("/links", response_model=Link)
def create_link(link: Link, db: Session = Depends(get_db)):
    db_link = links.Link(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link
@app.get("/links/{link_id}", response_model=Link)
def get_link(link_id: int, db: Session = Depends(get_db)):
    db_link = db.get(links.Link, link_id)
    if db_link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return db_link


@app.put("/links/{link_id}", response_model=Link)
def update_link(link_id: int, link: Link, db: Session = Depends(get_db)):
    db_link = db.get(links.Link, link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Movie not found")

    for key, value in link.model_dump().items():
        setattr(db_link, key, value)

    db.commit()
    db.refresh(db_link)
    return db_link

@app.delete("/links/{link_id}")
def delete_link(link_id: int, db: Session = Depends(get_db)):
    db_link = db.get(links.Link, link_id)
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")

    db.delete(db_link)
    db.commit()
    return {"message": "Link deleted successfully"}

@app.get("/ratings", response_model=List[Rating])
def get_ratings(db: Session = Depends(get_db)):
    return db.scalars(select(ratings.Rating)).all()

@app.post("/ratings", response_model=Rating)
def create_rating(rating: Rating, db: Session = Depends(get_db)):
    db_rating = ratings.Rating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.get("/ratings/{rating_id}", response_model=Rating)
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.get(ratings.Rating, rating_id)
    if db_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")
    return db_rating

@app.put("/ratings/{rating_id}", response_model=Rating)
def update_rating(rating_id: int, rating: Rating, db: Session = Depends(get_db)):
    db_rating = db.get(ratings.Rating, rating_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    for key, value in rating.model_dump().items():
        setattr(db_rating, key, value)

    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.delete("/ratings/{rating_id}")
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.get(ratings.Rating, rating_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")

    db.delete(db_rating)
    db.commit()
    return {"message": "Rating deleted successfully"}

@app.get("/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_db)):
    return db.scalars(select(tags.Tag)).all()

@app.post("/tags", response_model=Tag)
def create_tag(tag: Tag, db: Session = Depends(get_db)):
    db_tag = tags.Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.get("/tags/{tag_id}", response_model=Tag)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.get(tags.Tag, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return db_tag

@app.put("/tags/{tag_id}", response_model=Tag)
def update_tag(tag_id: int, tag: Tag, db: Session = Depends(get_db)):
    db_tag = db.get(tags.Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    for key, value in tag.model_dump().items():
        setattr(db_tag, key, value)

    db.commit()
    db.refresh(db_tag)
    return db_tag

@app.delete("/tags/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.get(tags.Tag, tag_id)
    if not db_tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(db_tag)
    db.commit()
    return {"message": "Tag deleted successfully"}