"""
This is a Flask API for managing orders.

Endpoints:
- GET /order: Retrieves all orders from the database.
- GET /order/<string:orderID>: Retrieves a single order by orderID.
- DELETE /order/<string:orderID>: Deletes a single order by orderID.
- GET /order/status/<string:status>: Retrieves orders by their status.
- POST /order: Creates a new order along with associated order items.
- PUT /order/<string:orderID>: Updates the status of an existing order by orderID.
- GET /order/orderitem/<string:orderID>: Retrieves an order and its associated items by orderID.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flasgger import Swagger

# Initialize Flask app
app = Flask(__name__)

# Configure database connection
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Swagger for API documentation
app.config['SWAGGER'] = {
    'title': 'Order microservice API',
    'version': 1.0,
    'openapi': "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of Orders'
}
swagger = Swagger(app)

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define database model for Order
class Order(db.Model):
    __tablename__ = 'orders'

    orderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(64), nullable=False)

    def __init__(self, userID, status):
        self.userID = userID
        self.status = status

    def json(self):
        return {"orderID": self.orderID, "userID": self.userID, "status": self.status}

# Define database model for OrderItem
class OrderItem(db.Model):
    __tablename__ = 'orderItem'

    orderID = db.Column(db.Integer, primary_key=True)
    itemID = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer)

    def __init__(self, orderID, itemID, quantity):
        self.orderID = orderID
        self.itemID = itemID
        self.quantity = quantity

    def json(self):
        return {"orderID": self.orderID, "itemID": self.itemID, "quantity": self.quantity}

# Retrieve all orders
@app.route("/order", methods=["GET"])
def get_all_orders():
    """
    Retrieves all orders from the database.
    ---
    responses:
        200:
            description: A list of orders.
        404:
            description: No orders found.
    """
    orderlist = Order.query.all()

    if orderlist:
        return jsonify({"code": 200, "data": {"order": [order.json() for order in orderlist]}})
    return jsonify({"code": 404, "message": "There are no orders."}), 404

# Retrieve a single order by orderID
@app.route("/order/<string:orderID>", methods=["GET"])
def get_order_by_orderID(orderID):
    """
    Retrieves a single order by orderID.
    ---
    parameters:
      - name: orderID
        in: path
        type: string
        required: true
        description: The ID of the order to retrieve.
    responses:
        200:
            description: Details of an order.
        404:
            description: Order not found.
    """
    order = Order.query.get(orderID)

    if order:
        return jsonify({"code": 200, "data": order.json()})
    return jsonify({"code": 404, "message": "Order not found."}), 404

# Delete a single order by orderID
@app.route("/order/<string:orderID>", methods=["DELETE"])
def delete_order_by_orderID(orderID):
    """
    Deletes a single order by orderID.
    ---
    parameters:
      - name: orderID
        in: path
        type: string
        required: true
        description: The ID of the order to delete.
    responses:
        204:
            description: Order deleted successfully.
        404:
            description: Order not found.
    """
    order = Order.query.get(orderID)

    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"code": 204}), 204
    return jsonify({"code": 404, "message": "Order not found."}), 404

# Retrieve orders by status
@app.route("/order/status/<string:status>", methods=["GET"])
def get_order_by_status(status):
    """
    Retrieves orders by their status.
    ---
    parameters:
      - name: status
        in: path
        type: string
        required: true
        description: The status of the orders to retrieve.
    responses:
        200:
            description: A list of orders filtered by status.
        404:
            description: No orders found with the specified status.
    """
    orderlist = Order.query.filter_by(status=status).all()

    if orderlist:
        return jsonify({"code": 200, "data": {"order": [order.json() for order in orderlist]}})
    return jsonify({"code": 404, "message": "No orders found."}), 404

# Create a new order along with associated order items
@app.route("/order", methods=["POST"])
def create_order():
    """
    Creates a new order along with associated order items.
    ---
    requestBody:
        description: Order details
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        userID:
                            type: integer
                            description: User ID of the order.
                        status:
                            type: string
                            description: Status of the order.
                        items:
                            type: array
                            items:
                                type: object
                                properties:
                                    itemID:
                                        type: integer
                                        description: Item ID.
                                    quantity:
                                        type: integer
                                        description: Quantity of the item.
    responses:
        201:
            description: Order created successfully.
        500:
            description: An error occurred creating the order.
    """
    try:
        data = request.json
        order = Order(userID=data['userID'], status=data['status'])
        db.session.add(order)
        db.session.flush()

        for item in data["items"]:
            order_item = OrderItem(orderID=order.orderID, itemID=item["itemID"], quantity=item["quantity"])
            db.session.add(order_item)

        db.session.commit()
        return jsonify({"code": 201, "message": "Order created successfully", "data": {"orderID": order.orderID}}), 201
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred creating the order.", "error": str(e)}), 500

# Update the status of an existing order by orderID
@app.route("/order/<string:orderID>", methods=["PUT"])
def update_order(orderID):
    """
    Updates the status of an existing order by orderID.
    ---
    parameters:
      - name: orderID
        in: path
        type: string
        required: true
        description: The ID of the order to update.
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              description: New status of the order.
    responses:
        200:
            description: Order updated successfully.
        404:
            description: Order not found.
        500:
            description: An error occurred while updating the order.
    """
    try:
        data = request.json
        order = Order.query.get(orderID)
        if not order:
            return jsonify({"code": 404, "message": "Order not found."}), 404

        order.status = data["status"]
        db.session.commit()
        return jsonify({"code": 200, "message": "Order updated successfully", "data": order.json()}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred while updating the order.", "error": str(e)}), 500

# Retrieve an order and its associated items by orderID
@app.route("/order/orderitem/<string:orderID>", methods=["GET"])
def get_orderitem_by_orderID(orderID):
    """
    Retrieves an order and its associated items by orderID.
    ---
    parameters:
      - name: orderID
        in: path
        type: string
        required: true
        description: The ID of the order to retrieve items for.
    responses:
        200:
            description: An order and its items.
        404:
            description: No order found with the specified ID.
    """
    order = Order.query.get(orderID)

    if order:
        items = OrderItem.query.filter_by(orderID=orderID).all()
        return jsonify({"code": 200, "data": {"order": order.json(), "items": [item.json() for item in items]}})
    return jsonify({"code": 404, "message": "No orders found."}), 404

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created.")

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
