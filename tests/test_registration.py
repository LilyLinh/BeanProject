# tests/test_registration.py

import pytest
from FrontPage import User, db

def test_registration(test_client):
    print("Test started")
    """
    GIVEN a Flask application
    WHEN the '/signup' page is posted to (POST)
    THEN check if the new user is successfully registered and added to the database
    """
    # Simulate a POST request to the registration endpoint
    response = test_client.post('/signup', data=dict(
        username='testuser',
        password='password',
        confirm_password='password'
    ), follow_redirects=True)

    print("Request sent")
    print(response.data.decode('utf-8'))

    # Check if the response is successful
    assert response.status_code == 200

    # Verify the user is in the database
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'
    print("Test completed")
