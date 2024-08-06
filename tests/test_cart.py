# tests/test_cart.py

import pytest
from FrontPage import app, db

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing purposes

    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

def test_add_to_cart(test_client):
    """
    GIVEN a Flask application
    WHEN the '/add_to_cart' page is posted to (POST)
    THEN check if the item is successfully added to the cart
    """
    # Simulate a POST request to add an item to the cart
    response = test_client.post('/add_to_cart', data=dict(
        product_id='1',
        product_name='Test Product',
        product_price='10.00',
        quantity='2',
        image='test_image.png'
    ), follow_redirects=True)

    # Check if the response is successful
    assert response.status_code == 200

    # Verify the item is in the cart
    with test_client.session_transaction() as sess:
        cart = sess.get('cart', [])
        assert len(cart) == 1
        assert cart[0]['product_id'] == '1'
        assert cart[0]['product_name'] == 'Test Product'
        assert cart[0]['product_price'] == 10.00
        assert cart[0]['quantity'] == 2
        assert cart[0]['image'] == 'test_image.png'
