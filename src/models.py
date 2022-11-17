from sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    address = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,

            # do not serialize the password, its a security breach
        }
class Items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    unit_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Items %r>' % self.product_name

    def serialize(self):
        return{
            "id": self.id,
            "item": self.product_name,
            "price": self.unit_price
        }

class AltVendors(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return '<AltVendor %r>' % self.vendor_name

    def serialize(self):
        return{
            "id": self.id,
            "vendor": self.vendor_name,
            "price": self.price
        }