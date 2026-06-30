import os
import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import scoped_session

# Set environment variable before backend.app is imported
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from backend.app import app as flask_app
from backend.database import db as database


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Fixture to configure and return the Flask application for testing."""
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Fixture to provide a Flask test client."""
    return app.test_client()


@pytest.fixture
def db_session(app: Flask) -> Generator[scoped_session, None, None]:
    """Fixture to expose the database session."""
    with app.app_context():
        yield database.session


@pytest.fixture(autouse=True)
def clean_db(app: Flask) -> Generator[None, None, None]:
    """Fixture to clean the database before and after each test."""
    with app.app_context():
        database.create_all()
        yield
        database.session.remove()
        database.drop_all()
