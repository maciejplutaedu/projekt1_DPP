import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app, get_db, Base
from models import movies, links, ratings, tags

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- RATINGS TESTS ---

def test_create_movie(client, db_session):
    payload = {"id": 1, "title": "Inception", "genres": "Action|Sci-Fi"}
    response = client.post("/movies", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Inception"
    assert data["id"] == 1

    db_movie = db_session.query(movies.Movie).filter(movies.Movie.id == 1).first()
    assert db_movie is not None
    assert db_movie.title == "Inception"


def test_get_movies_list(client, db_session):
    movie1 = movies.Movie(id=10, title="Movie A", genres="Drama")
    movie2 = movies.Movie(id=20, title="Movie B", genres="Comedy")
    db_session.add_all([movie1, movie2])
    db_session.commit()

    response = client.get("/movies")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == 10
    assert data[1]["id"] == 20


def test_get_movie_by_id(client, db_session):
    existing_movie = movies.Movie(id=99, title="The Matrix", genres="Sci-Fi")
    db_session.add(existing_movie)
    db_session.commit()

    response_ok = client.get("/movies/99")

    assert response_ok.status_code == 200
    assert response_ok.json()["title"] == "The Matrix"
    print("1 (Found): OK")

    response_404 = client.get("/movies/9999")

    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Movie not found"
    print("2 (404): OK")


def test_update_movie(client, db_session):
    movie = movies.Movie(id=1, title="Old Title", genres="Drama")
    db_session.add(movie)
    db_session.commit()

    payload = {"id": 1, "title": "New Updated Title", "genres": "Drama"}
    response = client.put("/movies/1", json=payload)

    assert response.status_code == 200
    assert response.json()["title"] == "New Updated Title"

    updated_movie = db_session.query(movies.Movie).filter(movies.Movie.id == 1).first()
    assert updated_movie.title == "New Updated Title"


def test_delete_movie(client, db_session):
    movie = movies.Movie(id=1, title="To Delete", genres="Horror")
    db_session.add(movie)
    db_session.commit()

    response = client.delete("/movies/1")

    assert response.status_code == 200
    assert db_session.query(movies.Movie).filter(movies.Movie.id == 1).first() is None

# --- TAGS TESTS ---

def test_create_link(client, db_session):
    payload = {"id": 1, "movieId": 100, "imdbId": "tt0133093", "tmdbId": "603"}
    response = client.post("/links", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["imdbId"] == "tt0133093"
    assert data["id"] == 1

    db_link = db_session.query(links.Link).filter(links.Link.id == 1).first()
    assert db_link is not None
    assert db_link.tmdbId == "603"


def test_get_links_list(client, db_session):
    link1 = links.Link(id=1, movieId=10, imdbId="tt111", tmdbId="111")
    link2 = links.Link(id=2, movieId=20, imdbId="tt222", tmdbId="222")
    db_session.add_all([link1, link2])
    db_session.commit()

    response = client.get("/links")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["imdbId"] == "tt111"
    assert data[1]["imdbId"] == "tt222"


def test_get_link_by_id(client, db_session):
    existing_link = links.Link(id=99, movieId=500, imdbId="tt999", tmdbId="999")
    db_session.add(existing_link)
    db_session.commit()

    response_ok = client.get("/links/99")

    assert response_ok.status_code == 200
    assert response_ok.json()["imdbId"] == "tt999"
    print("1 (Found): OK")

    response_404 = client.get("/links/9999")

    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Link not found"
    print("2 (404): OK")


def test_update_link(client, db_session):
    link = links.Link(id=1, movieId=100, imdbId="tt_old", tmdbId="old")
    db_session.add(link)
    db_session.commit()

    payload = {"id": 1, "movieId": 100, "imdbId": "tt_new", "tmdbId": "new_tmdb"}
    response = client.put("/links/1", json=payload)

    assert response.status_code == 200
    assert response.json()["imdbId"] == "tt_new"

    updated_link = db_session.query(links.Link).filter(links.Link.id == 1).first()
    assert updated_link.imdbId == "tt_new"
    assert updated_link.tmdbId == "new_tmdb"


def test_delete_link(client, db_session):
    link = links.Link(id=1, movieId=100, imdbId="tt_del", tmdbId="del")
    db_session.add(link)
    db_session.commit()

    response = client.delete("/links/1")

    assert response.status_code == 200
    assert db_session.query(links.Link).filter(links.Link.id == 1).first() is None



# --- RATINGS TESTS ---

def test_create_rating(client, db_session):
    payload = {"id": 1, "userId": 101, "movieId": 50, "rating": 4.5, "timestamp": 123456789}
    response = client.post("/ratings", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["rating"] == 4.5
    assert data["userId"] == 101

    db_rating = db_session.query(ratings.Rating).filter(ratings.Rating.id == 1).first()
    assert db_rating is not None
    assert db_rating.rating == 4.5


def test_get_ratings_list(client, db_session):
    r1 = ratings.Rating(id=1, userId=1, movieId=10, rating=5.0, timestamp=111)
    r2 = ratings.Rating(id=2, userId=2, movieId=20, rating=3.0, timestamp=222)
    db_session.add_all([r1, r2])
    db_session.commit()

    response = client.get("/ratings")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["rating"] == 5.0
    assert data[1]["rating"] == 3.0


def test_get_rating_by_id(client, db_session):
    existing_rating = ratings.Rating(id=99, userId=1, movieId=1, rating=2.0, timestamp=100)
    db_session.add(existing_rating)
    db_session.commit()

    response_ok = client.get("/ratings/99")

    assert response_ok.status_code == 200
    assert response_ok.json()["rating"] == 2.0
    print("1 (Found): OK")

    response_404 = client.get("/ratings/9999")

    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Rating not found"
    print("2 (404): OK")


def test_update_rating(client, db_session):
    rating = ratings.Rating(id=1, userId=1, movieId=1, rating=1.0, timestamp=100)
    db_session.add(rating)
    db_session.commit()

    payload = {"id": 1, "userId": 1, "movieId": 1, "rating": 5.0, "timestamp": 100}
    response = client.put("/ratings/1", json=payload)

    assert response.status_code == 200
    assert response.json()["rating"] == 5.0

    updated_rating = db_session.query(ratings.Rating).filter(ratings.Rating.id == 1).first()
    assert updated_rating.rating == 5.0


def test_delete_rating(client, db_session):
    rating = ratings.Rating(id=1, userId=1, movieId=1, rating=3.0, timestamp=100)
    db_session.add(rating)
    db_session.commit()

    response = client.delete("/ratings/1")

    assert response.status_code == 200
    assert db_session.query(ratings.Rating).filter(ratings.Rating.id == 1).first() is None


# --- TAGS TESTS ---

def test_create_tag(client, db_session):
    payload = {"id": 1, "userId": 50, "movieId": 10, "tag": "funny", "timestamp": 999}
    response = client.post("/tags", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["tag"] == "funny"
    assert data["id"] == 1

    db_tag = db_session.query(tags.Tag).filter(tags.Tag.id == 1).first()
    assert db_tag is not None
    assert db_tag.tag == "funny"


def test_get_tags_list(client, db_session):
    t1 = tags.Tag(id=1, userId=1, movieId=1, tag="classic", timestamp=100)
    t2 = tags.Tag(id=2, userId=1, movieId=2, tag="action", timestamp=200)
    db_session.add_all([t1, t2])
    db_session.commit()

    response = client.get("/tags")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["tag"] == "classic"


def test_get_tag_by_id(client, db_session):
    existing_tag = tags.Tag(id=55, userId=1, movieId=1, tag="scary", timestamp=123)
    db_session.add(existing_tag)
    db_session.commit()

    response_ok = client.get("/tags/55")

    assert response_ok.status_code == 200
    assert response_ok.json()["tag"] == "scary"
    print("1 (Found): OK")

    response_404 = client.get("/tags/9999")

    assert response_404.status_code == 404
    assert response_404.json()["detail"] == "Tag not found"
    print("2 (404): OK")


def test_update_tag(client, db_session):
    tag = tags.Tag(id=1, userId=1, movieId=1, tag="boring", timestamp=100)
    db_session.add(tag)
    db_session.commit()

    payload = {"id": 1, "userId": 1, "movieId": 1, "tag": "exciting", "timestamp": 100}
    response = client.put("/tags/1", json=payload)

    assert response.status_code == 200
    assert response.json()["tag"] == "exciting"

    updated_tag = db_session.query(tags.Tag).filter(tags.Tag.id == 1).first()
    assert updated_tag.tag == "exciting"


def test_delete_tag(client, db_session):
    tag = tags.Tag(id=1, userId=1, movieId=1, tag="to_delete", timestamp=100)
    db_session.add(tag)
    db_session.commit()

    response = client.delete("/tags/1")

    assert response.status_code == 200
    assert db_session.query(tags.Tag).filter(tags.Tag.id == 1).first() is None