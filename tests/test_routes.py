# tests/test_routes.py
import pytest
from werkzeug.security import generate_password_hash
from FrontPage import app, db, User

def test_home_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'The Bean Project' in response.data

def test_login_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data

# tests/test_registration.py

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', password=generate_password_hash('password', method='pbkdf2:sha256'))
    return user

# tests/test_registration.py


