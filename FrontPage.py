import stripe, os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from functools import wraps


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to use sessions

# Stripe configuration
app.config['STRIPE_SECRET_KEY'] = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'
app.config['STRIPE_PUBLISHABLE_KEY'] = 'pk_test_TYooMQauvdEDq54NiTphI7jx'

stripe.api_key = 'sk_test_51PhatZRrgscvEcuPjdbKha29XQWC4j0WJh2FwjcqrNJgutsq7qJ0SIp2uAWoo4BFRSRSBrSkzax97Fw5ZzhFZqjk00L4e3eDoO'

# Update  newly created database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user1:user1pass@localhost/user_and_pass'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

admin_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')



db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    order_histories = db.relationship('OrderHistory', backref='user', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_details = db.relationship('OrderDetail', backref='order', lazy=True)
    order_histories = db.relationship('OrderHistory', backref='order', lazy=True)

class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    availability = db.Column(db.String(50), nullable=False)
    order_details = db.relationship('OrderDetail', backref='menu_item', lazy=True)


class OrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)



# Dummy user data
users = {
    "admin": generate_password_hash("password123", method='pbkdf2:sha256'),
    "user": generate_password_hash("userpass", method='pbkdf2:sha256')
}
# Sample menu items
menu_items = [
    {'id': 1, 'name': 'Grilled Harissa Chicken Rice', 'price': 10.99, 'availability': 'In stock', 'image': 'product1.webp', 'category': 'Halal', "reviews": [], "average_rating": 0},
    {'id': 2, 'name': 'Charcoal-Grilled Steak and Vegetable', 'price': 8.99, 'availability': 'In stock', 'image': 'product2.webp', 'category': 'Healthy',"reviews": [], "average_rating": 0},
    {'id': 3, 'name': 'Tuna Steak and Avocado Salads', 'price': 6.99, 'availability': 'In stock', 'image': 'product3.webp', 'category': 'Healthy', "reviews": [], "average_rating": 0},
    {'id': 4, 'name': 'Falafel and Hummus Salad', 'price': 11.99, 'availability': 'In stock', 'image': 'product4.webp', 'category': 'Vegan', "reviews": [], "average_rating": 0},
    {'id': 5, 'name': 'Mushroom pate and Hummus Sandwich', 'price': 9.99, 'availability': 'In stock', 'image': 'product5.webp', 'category': 'Vegan', "reviews": [], "average_rating": 0},
    {'id': 6, 'name': 'Sweet and Sour Thai Vegetable Soup', 'price': 7.99, 'availability': 'In stock', 'image': 'product6.webp', 'category': 'Vegan', "reviews": [], "average_rating": 0},
]
with app.app_context():
    db.create_all()

# Route to insert menu items

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/menu')
def menu():
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'featured')

    # Filter items by category
    if category == 'halal':
        items = [item for item in menu_items if item['category'] == 'Halal']
    elif category == 'healthy':
        items = [item for item in menu_items if item['category'] == 'Healthy']
    elif category == 'vegan':
        items = [item for item in menu_items if item['category'] == 'Vegan']
    else:
        items = menu_items

    # Sort items
    if sort_by == 'price-asc':
        items = sorted(items, key=lambda x: x['price'])
    elif sort_by == 'price-desc':
        items = sorted(items, key=lambda x: x['price'], reverse=True)
    elif sort_by == 'name-asc':
        items = sorted(items, key=lambda x: x['name'])
    elif sort_by == 'name-desc':
        items = sorted(items, key=lambda x: x['name'], reverse=True)

    # Fetch recommended items
    recommended_items = []
    recommended_item_ids = (
        db.session.query(OrderDetail.product_id)
        .join(Order)
        .group_by(OrderDetail.product_id)
        .having(db.func.sum(OrderDetail.quantity) > 1)
        .all()
    )

    for item_id in recommended_item_ids:
        item = next((i for i in menu_items if i['id'] == item_id[0]), None)
        if item:
            recommended_items.append(item)

    return render_template('menu.html', items=items, recommended_items=recommended_items, category=category, sort_by=sort_by)

@app.route('/update-availability', methods=['POST'])
def update_availability():
    item_id = int(request.form.get('item_id'))
    new_availability = request.form.get('availability')
    for item in menu_items:
        if item['id'] == item_id:
            item['availability'] = new_availability
            break
    return jsonify({'status': 'success', 'item_id': item_id, 'new_availability': new_availability})

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    for item in cart_items:
        menu_item = next((menu for menu in menu_items if menu['id'] == int(item['product_id'])), None)
        if menu_item:
            item['image'] = menu_item['image']
            item['product_name'] = menu_item['name']
            item['product_price'] = menu_item['price']
            item['total_price'] = menu_item['price'] * int(item['quantity'])

    return render_template('cart.html', cart_items=cart_items)



@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        if 'username' not in session:
            return redirect(url_for('login'))

        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('menu'))

        order = Order(user_id=user.id)
        db.session.add(order)
        db.session.commit()
        order_id = order.id  # Get the order id after committing

        cart_items = session.get('cart', [])
        total_amount = sum(float(item['product_price']) * int(item['quantity']) for item in cart_items) * 100  # in cents

        for item in cart_items:
            product_id = item['product_id']
            quantity = int(item['quantity'])
            price = float(item['product_price'])
            total_price = price * quantity
            order_detail = OrderDetail(order_id=order.id, product_id=product_id, quantity=quantity, price=total_price)
            db.session.add(order_detail)

        db.session.commit()  # Commit the order details

        session.pop('cart', None)
        flash('Order placed successfully!', 'success')
        return redirect(url_for('order_confirmation', order_id=order.id))
    else:
        cart_items = session.get('cart', [])
        for item in cart_items:
            item['total_price'] = float(item['product_price']) * int(item['quantity'])
        total_amount = sum(item['total_price'] for item in cart_items) * 100  # in cents

        try:
            # Create a PaymentIntent with the order amount and currency
            payment_intent = stripe.PaymentIntent.create(
                amount=int(total_amount),
                currency='eur',
            )
            client_secret = payment_intent.client_secret
            payment_intent_id = payment_intent.id

            # Debugging print statements
            print(f"Client Secret: {client_secret}")
            print(f"Payment Intent ID: {payment_intent_id}")
            print(f"Cart Items: {cart_items}")

            # Create an order in the database for this checkout session
            if 'username' in session:
                user = User.query.filter_by(username=session['username']).first()
                if user:
                    order = Order(user_id=user.id)
                    db.session.add(order)
                    db.session.commit()
                    order_id = order.id
                    for item in cart_items:
                        product_id = item['product_id']
                        quantity = int(item['quantity'])
                        price = float(item['product_price'])
                        total_price = price * quantity
                        order_detail = OrderDetail(order_id=order.id, product_id=product_id, quantity=quantity, price=total_price)
                        db.session.add(order_detail)
                    db.session.commit()
                    print(f"Order ID: {order_id}, Order Details: {OrderDetail.query.filter_by(order_id=order_id).all()}")
                else:
                    order_id = None
            else:
                order_id = None

        except Exception as e:
            print(f"Error creating payment intent: {e}")
            flash('Error creating payment intent', 'danger')
            return redirect(url_for('cart'))

        return render_template(
            'checkout.html',
            cart_items=cart_items,
            client_secret=client_secret,
            payment_intent_id=payment_intent_id,
            order_id=order_id,
            stripe_publishable_key= 'pk_test_51PhatZRrgscvEcuPEl8tAncWsvbP8EblAoUWN6KBG1Z0s0PwJrUmVZo2XkDGthvkQ8QbTbru8Jm40yJHkLWccs2o00xXn46S8F'
        )

@app.route('/order_confirmation/<int:order_id>', methods=['GET'])
def order_confirmation(order_id):
    print(f"Debug - Order Confirmation: Received order_id = {order_id}")

    order = db.session.get(Order, order_id)
    if not order:
        print(f"Debug - Order Confirmation: No order found with id = {order_id}")
        flash('Order not found', 'danger')
        return redirect(url_for('menu'))

    order_details = OrderDetail.query.filter_by(order_id=order_id).all()
    if not order_details:
        print(f"Debug - Order Confirmation: No order details found for order_id = {order_id}")
        flash('Order details not found', 'danger')
        return redirect(url_for('menu'))

    print(f"Debug - Order Confirmation: Order found with id = {order_id}")
    return render_template('order_confirmation.html', order=order, order_details=order_details)

@app.route('/order_history')
def order_history():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('menu'))

    orders = Order.query.filter_by(user_id=user.id).all()
    return render_template('order_history.html', orders=orders)

def get_recommended_menu(user_id):
    # Get all orders for the user
    user_orders = Order.query.filter_by(user_id=user_id).all()
    product_counts = {}

    # Count the frequency of each product in the user's order history
    for order in user_orders:
        for detail in order.order_details:
            product_id = detail.product_id
            if product_id in product_counts:
                product_counts[product_id] += detail.quantity
            else:
                product_counts[product_id] = detail.quantity

    # Sort products by frequency
    sorted_products = sorted(product_counts.items(), key=lambda item: item[1], reverse=True)

    # Get the top 5 most frequently ordered products
    recommended_products = []
    for product_id, count in sorted_products[:5]:
        product = MenuItem.query.get(product_id)
        if product:
            recommended_products.append({
                'id': product.id,
                'name': product.name,
                'price': product.price,
                'availability': product.availability,
                'image': product.image  # Include the image attribute
            })

    return recommended_products

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))

        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('product_id')
    product_name = request.form.get('product_name')
    product_price = float(request.form.get('product_price'))
    quantity = int(request.form.get('quantity'))
    image = request.form.get('image')


    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        'product_id': product_id,
        'product_name': product_name,
        'product_price': product_price,
        'quantity': quantity,
        'image': image

    })

    flash(f'{product_name} added to cart!', 'success')
    return redirect(url_for('menu'))



@app.context_processor
def inject_cart_quantity():
    cart = session.get('cart', [])
    total_quantity = sum(item['quantity'] for item in cart)
    return {'cart_quantity': total_quantity}

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    product_id = request.form.get('product_id')
    if 'cart' in session:
        cart = session['cart']
        session['cart'] = [item for item in cart if item['product_id'] != product_id]
        flash('Item deleted from cart', 'success')
    else:
        flash('No items in cart to delete', 'danger')
    return redirect(url_for('cart'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/protected')
@login_required
def protected():
    return 'This is a protected route.'

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or session['username'] != 'admin':
            flash('You need to be an admin to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin_users')
def admin_users():
    if 'username' in session and session['username'] == 'admin':
        users = User.query.all()
        orders = Order.query.all()
        return render_template('admin_users.html', users=users, orders=orders)
    else:
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('login'))

@app.route('/recommended_menu')
@login_required
def recommended_menu():
    user = User.query.filter_by(username=session['username']).first()
    recommended_items = get_recommended_menu(user.id)
    return render_template('recommended_menu.html', items=recommended_items)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    product_id = int(request.form.get('product_id'))
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment', '')

    if not (1 <= rating <= 5):
        flash('Rating must be between 1 and 5.')
        return redirect(url_for('menu'))

    for item in menu_items:
        if item['id'] == product_id:
            item['reviews'].append({'rating': rating, 'comment': comment})
            item['average_rating'] = sum([review['rating'] for review in item['reviews']]) / len(item['reviews'])
            break

    flash('Your review has been submitted!')
    return redirect(url_for('product_reviews', product_id=product_id))

@app.route('/product_reviews/<int:product_id>')
def product_reviews(product_id):
    product = next((item for item in menu_items if item['id'] == product_id), None)
    if not product:
        flash('Product not found.')
        return redirect(url_for('menu'))

    return render_template('product_reviews.html', product=product)

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()  # Create database tables
        print("Database tables created successfully")
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred: {e}")
