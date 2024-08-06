# tests/conftest.py

import pytest
from FrontPage import app, db
from FrontPage import User

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for testing purposes

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing purposes

    with app.test_client() as testing_client:
        with app.app_context():
            print("Creating database")
            db.create_all()
            yield testing_client
            print("Dropping database")
            db.drop_all()

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', password='password')
    return user
