import csv
from typing import Union, List
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

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

# Tag model for tags data
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

@app.get("/movies", response_model=List[Movie])
async def get_movies():
    movies = load_movies_from_file(
        r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\movies.csv"
    )
    return movies

@app.get("/links", response_model=List[Link])
async def get_links():
    links = load_links_from_file(
        r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\links.csv"
    )
    return links

@app.get("/ratings", response_model=List[Rating])
async def get_ratings():
    ratings = load_ratings_from_file(
        r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\ratings.csv"
    )
    return ratings

@app.get("/tags", response_model=List[Tag])
async def get_tags():
    tags = load_tags_from_file(
        r"C:\Users\maciek\PycharmProjects\ApiZaj4\data\tags.csv"
    )
    return tags