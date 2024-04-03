"""
This is a Flask API for managing shopping carts.

Endpoints:
- GET /health: Checks the health of the application.
- GET /cart: Retrieves all active carts.
- GET /cart/<string:userID>: Retrieves items in the active cart for a specific user.
- GET /cart/item/<string:itemID>: Retrieves users with the specified item in their active cart.
- POST /cart/close/<string:userID>: Closes the active cart for a specific user.
- PUT /cart/<string:userID>: Updates the active cart for a specific user.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flasgger import Swagger
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Swagger for API documentation
swagger = Swagger(app)

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define database model for Cart
class Cart(db.Model):
    __tablename__ = 'cart'

    cartID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(self, userID, active):
        self.userID = userID
        self.active = active

    def json(self):
        return {"cartID": self.cartID, "userID": self.userID, "active": self.active}

# Define database model for CartItem
class CartItem(db.Model):
    __tablename__ = 'cartItem'

    cartID = db.Column(db.Integer, primary_key=True)
    itemID = db.Column(db.String(100), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer)

    def __init__(self, cartID, itemID, quantity):
        self.cartID = cartID
        self.itemID = itemID
        self.quantity = quantity

    def json(self):
        return {"cartID": self.cartID, "itemID": self.itemID, "quantity": self.quantity}

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    """
    Health Check Endpoint.
    ---
    responses:
        200:
            description: Application is healthy.
    """
    return jsonify({"status": "healthy"}), 200

# Retrieve all active carts
@app.route("/cart", methods=["GET"])
def get_cart():
    """
    Retrieves all active carts.
    ---
    responses:
        200:
            description: List of active carts.
        404:
            description: No active carts found.
    """
    cartlist = Cart.query.filter_by(active=True).all()

    if cartlist:
        return jsonify({"code": 200, "data": {"cart": [cart.json() for cart in cartlist]}})
    return jsonify({"code": 404, "message": "No active carts found."}), 404

# Retrieve items in the active cart for a specific user
@app.route("/cart/<string:userID>", methods=["GET"])
def get_item_in_cart_by_userID(userID):
    """
    Retrieves items in the active cart for a specific user.
    ---
    parameters:
      - name: userID
        in: path
        type: string
        required: true
        description: The ID of the user.
    responses:
        202:
            description: List of items in the user's active cart.
    """
    cart = Cart.query.filter_by(userID=userID, active=True).first()

    if not cart:
        cart = Cart(userID=userID, active=True)
        db.session.add(cart)
        db.session.flush()
        db.session.refresh(cart)

    cart_items = CartItem.query.filter_by(cartID=cart.cartID).all()
    cart_items_list = [item.json() for item in cart_items]
    return jsonify({"code": 202, "data": cart_items_list}), 202

# Retrieve users with the specified item in their active cart
@app.route("/cart/item/<string:itemID>", methods=["GET"])
def get_users_with_itemID_in_active_cart(itemID):
    """
    Retrieves users with the specified item in their active cart.
    ---
    parameters:
      - name: itemID
        in: path
        type: string
        required: true
        description: The ID of the item.
    responses:
        202:
            description: List of users with the item in their active cart.
    """
    carts = CartItem.query.filter_by(itemID=itemID).all()
    users_return = []
    # users_return = [cart.userID for cart in carts if Cart.query.filter_by(cartID=cart.cartID, active=True).first()]
    for cartItemModel in carts:
        cartID = cartItemModel.cartID
        UserModel = Cart.query.filter_by(cartID=cartID, active=True).first()
        userID = UserModel.userID
        users_return.append(userID)

    return jsonify({"code": 202, "data": users_return}), 202

# Close the active cart for a specific user
@app.route("/cart/close/<string:userID>", methods=["POST"])
def close_cart(userID):
    """
    Closes the active cart for a specific user.
    ---
    parameters:
      - name: userID
        in: path
        type: string
        required: true
        description: The ID of the user.
    responses:
        204:
            description: Cart closed successfully.
        404:
            description: Cart not found.
        500:
            description: An error occurred while updating the cart.
    """
    try:
        cart = Cart.query.filter_by(userID=userID, active=True).first()
        if not cart:
            return jsonify({"code": 404, "message": "Cart not found."}), 404

        cart.active = False
        db.session.commit()
        return jsonify({"code": 204, "message": "No Content"}), 204
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred while updating the cart.", "error": str(e)}), 500

# Update the active cart for a specific user
@app.route("/cart/<string:userID>", methods=["PUT"])
def update_cart(userID):
    """
    Updates the active cart for a specific user.
    ---
    parameters:
      - name: userID
        in: path
        type: string
        required: true
        description: The ID of the user.
      - in: body
        name: body
        description: The updated cart details.
        schema:
          type: object
          properties:
            addItem:
              type: array
              items:
                type: object
                properties:
                  itemID:
                    type: string
                  quantity:
                    type: integer
            deleteItem:
              type: array
              items:
                type: object
                properties:
                  itemID:
                    type: string
                  quantity:
                    type: integer
    responses:
        200:
            description: Cart updated successfully.
        404:
            description: Cart not found.
        500:
            description: An error occurred while updating the cart.
    """
    try:
        data = request.get_json()
        cart = Cart.query.filter_by(userID=userID, active=True).first()
        if not cart:
            cart = Cart(userID=userID, active=True)
            db.session.add(cart)
            db.session.flush()
            db.session.refresh(cart)

        if 'addItem' in data:
            for item in data['addItem']:
                itemID = item["itemID"]
                quantity = item["quantity"]
                cart_item = CartItem.query.filter_by(cartID=cart.cartID, itemID=itemID).first()
                if cart_item:
                    cart_item.quantity += quantity
                else:
                    cart_item = CartItem(cartID=cart.cartID, itemID=itemID, quantity=quantity)
                    db.session.add(cart_item)

        if 'deleteItem' in data:
            for item in data['deleteItem']:
                itemID = item["itemID"]
                quantity = item["quantity"]
                cart_item = CartItem.query.filter_by(cartID=cart.cartID, itemID=itemID).first()
                if cart_item.quantity - quantity <= 0:
                    db.session.delete(cart_item)
                else:
                    cart_item.quantity -= quantity

        db.session.commit()
        return jsonify({"code": 200, "message": "Cart updated successfully"}), 200

    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred while updating the cart.", "error": str(e)}), 500

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created.")

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
