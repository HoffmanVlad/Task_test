from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

order_products = db.Table(
    'order_products',
    db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'))
)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(50))
    weight = db.Column(db.Float)
    price = db.Column(db.Float)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    orders = db.relationship('Order', secondary='order_products', back_populates='products')

class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    street = db.Column(db.String(100))
    previous_address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    previous_address = db.relationship('Address', remote_side=[id])

    def __repr__(self):
        return f"{self.country} - {self.city} - {self.street}"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    status = db.Column(db.String(20)) 

    address = db.relationship('Address', backref='orders')
    products = db.relationship('Product', secondary='order_products', back_populates='orders')

    def __repr__(self):
        return f"<Order {self.id} - {self.customer_name}>"
