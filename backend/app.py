from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'food_ordering.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# ---------------------- MODELS ----------------------

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    image_emoji = db.Column(db.String(10), default="🍽️")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "image_emoji": self.image_emoji,
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20))
    address = db.Column(db.String(255))
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_name": self.customer_name,
            "customer_phone": self.customer_phone,
            "address": self.address,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "items": [i.to_dict() for i in self.items],
        }


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_item.id"), nullable=False)
    item_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "menu_item_id": self.menu_item_id,
            "item_name": self.item_name,
            "quantity": self.quantity,
            "price": self.price,
            "subtotal": round(self.price * self.quantity, 2),
        }


# ---------------------- SEED DATA ----------------------

def seed_menu():
    if MenuItem.query.count() > 0:
        return
    items = [
        MenuItem(name="Classic Cheese Burger", description="Beef patty, cheddar, lettuce, tomato", price=189.0, category="Burgers", image_emoji="🍔"),
        MenuItem(name="Margherita Pizza", description="Fresh mozzarella, basil, tomato sauce", price=299.0, category="Pizza", image_emoji="🍕"),
        MenuItem(name="Chicken Biryani", description="Fragrant basmati rice with spiced chicken", price=249.0, category="Rice", image_emoji="🍛"),
        MenuItem(name="Paneer Tikka", description="Grilled cottage cheese with spices", price=219.0, category="Starters", image_emoji="🧆"),
        MenuItem(name="Veg Noodles", description="Stir-fried noodles with fresh vegetables", price=159.0, category="Chinese", image_emoji="🍜"),
        MenuItem(name="Cold Coffee", description="Chilled coffee blended with ice cream", price=99.0, category="Beverages", image_emoji="🥤"),
        MenuItem(name="Chocolate Brownie", description="Warm brownie with chocolate sauce", price=129.0, category="Desserts", image_emoji="🍰"),
        MenuItem(name="Masala Dosa", description="Crispy rice crepe with potato filling", price=139.0, category="South Indian", image_emoji="🥞"),
    ]
    db.session.add_all(items)
    db.session.commit()


# ---------------------- ROUTES ----------------------

@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})


@app.route("/api/menu", methods=["GET"])
def get_menu():
    category = request.args.get("category")
    query = MenuItem.query
    if category:
        query = query.filter_by(category=category)
    items = query.all()
    return jsonify([i.to_dict() for i in items])


@app.route("/api/menu/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    return jsonify(item.to_dict())


@app.route("/api/menu", methods=["POST"])
def add_menu_item():
    data = request.get_json(force=True)
    if not data.get("name") or data.get("price") is None:
        return jsonify({"error": "name and price are required"}), 400
    item = MenuItem(
        name=data["name"],
        description=data.get("description", ""),
        price=float(data["price"]),
        category=data.get("category", "General"),
        image_emoji=data.get("image_emoji", "🍽️"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/api/orders", methods=["GET"])
def get_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@app.route("/api/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    order = Order.query.get_or_404(order_id)
    return jsonify(order.to_dict())


@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True)

    if not data.get("customer_name"):
        return jsonify({"error": "customer_name is required"}), 400
    if not data.get("items"):
        return jsonify({"error": "at least one item is required"}), 400

    order = Order(
        customer_name=data["customer_name"],
        customer_phone=data.get("customer_phone", ""),
        address=data.get("address", ""),
        status="pending",
    )
    db.session.add(order)
    db.session.flush()  # get order.id before commit

    total = 0.0
    for item_data in data["items"]:
        menu_item = MenuItem.query.get(item_data["menu_item_id"])
        if not menu_item:
            continue
        qty = int(item_data.get("quantity", 1))
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            item_name=menu_item.name,
            quantity=qty,
            price=menu_item.price,
        )
        total += menu_item.price * qty
        db.session.add(order_item)

    order.total_amount = round(total, 2)
    db.session.commit()

    return jsonify(order.to_dict()), 201


@app.route("/api/orders/<int:order_id>/status", methods=["PATCH"])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    data = request.get_json(force=True)
    new_status = data.get("status")
    if new_status not in ("pending", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"):
        return jsonify({"error": "invalid status"}), 400
    order.status = new_status
    db.session.commit()
    return jsonify(order.to_dict())


with app.app_context():
    db.create_all()
    seed_menu()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
