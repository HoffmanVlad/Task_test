from flask import Flask, render_template, request, redirect, request, jsonify, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from models import Product, Address, Order, db
from celery import Celery
from flask_jsonrpc import JSONRPC
from functools import wraps
from jsonrpcserver import method, Result, Success, dispatch
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1:3306/db'
app.config['SECRET_KEY'] = '4df56hg4dfv6c5n4t9gfnfgnf864n56f'

db.init_app(app)
migrate = Migrate(app, db)
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/'
client = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
client.conf.update(app.config)
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
jsonrpc = JSONRPC(app, "/api", enable_web_browsable_api=True)

class OrderAdmin(ModelView):
    column_list = ['customer_name', 'address', 'status']

    form_choices = {
        'status': [
            ('Обробляється', 'Обробляється'),
            ('Виконано', 'Виконано'),
            ('Відмінено', 'Відмінено')
        ]
    }

admin = Admin(app, name='microblog', template_mode='bootstrap4')
admin.add_view(ModelView(Product, db.session))
admin.add_view(ModelView(Address, db.session))
admin.add_view(OrderAdmin(Order, db.session))

def admin_auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin: 
            return redirect(url_for('login')) 
        return fn(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/addresses')
def addresses():
    addresses = Address.query.all()
    return render_template('addresses.html', addresses=addresses)

@app.route('/create_order', methods=['POST'])
def create_order():
    customer_name = request.form.get('customer_name')
    address_id = request.form.get('address_id')
    status = 'Обробляється'
    order = Order(customer_name=customer_name, address_id=address_id, status=status)
    db.session.add(order)
    db.session.commit()
    return redirect('/orders')

@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@client.task
def track_order_status(order_id, new_status):
    event = f"Замовлення {order_id} змінило статус на {new_status}"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'E:\Technical Task Ilya Flask\flask_product\order_events.txt')
    with open(file_path, 'a', encoding="utf-8") as file:
        file.write(event + '\n')
    return event

def check_auth(username, password):
    return username == 'your_username' and password == 'your_password'

def authorized(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonrpc.response({"error": "Unauthorized"}, code=401)
        return fn(*args, **kwargs)
    return wrapper

def retrieve_order_status(order_id: int):
    order = Order.query.get(order_id)
    if order is None:
        return "Order not found"
    return order.status

@jsonrpc.method('order.get_status(order_id=int)')
def get_order_status(order_id: int):
    status = retrieve_order_status(order_id)
    response = {"order_id": order_id, "status": status}
    return response

# Виклик функції get_order_status з JSON-RPC
@app.route('/get_order_status/<int:order_id>', methods=['GET'])
def get_order_status_endpoint(order_id):
    response = get_order_status(order_id)
    return jsonify(response)

@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    order = Order.query.get(order_id)
    if not order:
        flash(f'Order with ID {order_id} not found.', 'error')
        return redirect('/orders')

    if 'status' not in request.form:
        flash('Status not provided.', 'error')
        return redirect('/orders')

    new_status = request.form['status']
    previous_status = order.status
    order.status = new_status
    db.session.commit()

    event = f"Замовлення {order_id} змінило статус на {new_status}"
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'order_events.txt')
    with open(file_path, 'a') as file:
        file.write(event + '\n')

    flash(f'Order status updated from {previous_status} to {new_status}.', 'success')
    return redirect('/orders')

