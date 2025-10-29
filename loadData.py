import csv
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, init_db
import models


def load_movies(db):
    print("Loading movies...")
    with open("data/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie = models.Movie(
                id=int(row["movieId"]),
                title=row["title"],
                genres=row["genres"]
            )
            db.add(movie)
    db.commit()


def load_links(db):
    print("Loading links...")
    with open("data/links.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Some links might have missing IMDb or TMDB IDs
            imdb = row["imdbId"] or None
            tmdb = row["tmdbId"] or None

            link = models.Link(
                movieId=int(row["movieId"]),
                imdbId=imdb,
                tmdbId=tmdb
            )
            db.add(link)
    db.commit()


def load_ratings(db):
    print("Loading ratings...")
    with open("data/ratings.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rating = models.Rating(
                userId=int(row["userId"]),
                movieId=int(row["movieId"]),
                rating=float(row["rating"]),
                timestamp=int(row["timestamp"])
            )
            db.add(rating)
    db.commit()


def load_tags(db):
    print("Loading tags...")
    with open("data/tags.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag = models.Tag(
                userId=int(row["userId"]),
                movieId=int(row["movieId"]),
                tag=row["tag"],
                timestamp=int(row["timestamp"])
            )
            db.add(tag)
    db.commit()


def load_all_data():
    init_db()
    db = SessionLocal()

    try:
        load_movies(db)
        load_links(db)
        load_ratings(db)
        load_tags(db)
        print("✅ All data loaded successfully!")
    except IntegrityError as e:
        db.rollback()
        print(f"⚠️ Database error: {e}")
    finally:
        db.close()


load_all_data()
