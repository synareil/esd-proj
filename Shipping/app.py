"""
This is a Flask API for managing shipping details.

Endpoints:
- GET /shipping: Retrieves all shipping details.
- GET /shipping/<string:OrderID>: Retrieves shipping details by OrderID.
- POST /shipping/createshipping: Creates a new shipping record.
- PUT /shipping/<string:ShippingID>: Updates shipping records by ShippingID.
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

# Initialize SQLAlchemy ORM
db = SQLAlchemy(app)

# Define database model for Shipping
class Shipping(db.Model):
    __tablename__ = 'shipping'

    ShippingID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    UserID = db.Column(db.Integer, nullable=False)
    shippingAddress = db.Column(db.String(100), nullable=False)
    ShippingStatus = db.Column(db.String(100), nullable=False)

    def __init__(self, OrderID, UserID, shippingAddress, ShippingStatus):
        self.OrderID = OrderID
        self.UserID = UserID
        self.shippingAddress = shippingAddress
        self.ShippingStatus = ShippingStatus

    def json(self):
        return {"ShippingID": self.ShippingID, "OrderID": self.OrderID, "UserID": self.UserID, 
                "shippingAddress": self.shippingAddress, "ShippingStatus": self.ShippingStatus}

# Retrieve all shipping details
@app.route("/shipping", methods=["GET"])
def get_all():
    """
    Retrieves all shipping details.
    ---
    responses:
        200:
            description: A list of shipping details.
    """
    shipping_details = Shipping.query.all()
    return jsonify({"code": 200, "data": {"Details": [data.json() for data in shipping_details]}}), 200

# Retrieve shipping details by OrderID
@app.route("/shipping/<string:OrderID>", methods=["GET"])
def get_shipping_details_by_OrderID(OrderID):
    """
    Retrieves shipping details by OrderID.
    ---
    parameters:
      - name: OrderID
        in: path
        type: string
        required: true
        description: The OrderID to retrieve shipping details for.
    responses:
        200:
            description: Shipping details for the specified OrderID.
        404:
            description: Shipping details not found.
    """
    details = Shipping.query.filter_by(OrderID=OrderID).first()
    if details:
        return jsonify({"code": 200, "data": details.json()}), 200
    return jsonify({"code": 404, "message": "Shipping details not found."}), 404

# Create new shipping record
@app.route("/shipping/createshipping", methods=['POST'])
def create_shipping_record():
    """
    Creates a new shipping record.
    ---
    requestBody:
        description: Shipping details
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        OrderID:
                            type: integer
                            description: The OrderID associated with the shipping.
                        UserID:
                            type: integer
                            description: The UserID associated with the shipping.
                        shippingAddress:
                            type: string
                            description: The shipping address.
                        ShippingStatus:
                            type: string
                            description: The shipping status.
    responses:
        201:
            description: Shipping record created successfully.
        500:
            description: An error occurred creating the shipping record.
    """
    data = request.json
    shipping_details = Shipping(**data)
    try:
        db.session.add(shipping_details)
        db.session.commit()
        return jsonify({"code": 201, "data": shipping_details.json()}), 201
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred creating the shipping details.", "error": str(e)}), 500

# Update shipping record by ShippingID
@app.route("/shipping/<string:ShippingID>", methods=['PUT'])
def update_shipping_records(ShippingID):
    """
    Updates shipping records by ShippingID.
    ---
    parameters:
      - name: ShippingID
        in: path
        type: string
        required: true
        description: The ID of the shipping record to update.
    requestBody:
        description: Shipping details
        required: true
        content:
            application/json:
                schema:
                    type: object
                    properties:
                        shippingAddress:
                            type: string
                            description: The updated shipping address.
                        ShippingStatus:
                            type: string
                            description: The updated shipping status.
    responses:
        201:
            description: Shipping record updated successfully.
        404:
            description: Shipping ID not found.
        500:
            description: An error occurred while updating the shipping record.
    """
    try:
        shipping_details = Shipping.query.get(ShippingID)
        if not shipping_details:
            return jsonify({"code": 404, "message": "Shipping ID not found."}), 404

        data = request.json
        if data:
            if 'shippingAddress' in data:
                shipping_details.shippingAddress = data['shippingAddress']
            if 'ShippingStatus' in data:
                shipping_details.ShippingStatus = data['ShippingStatus']
            db.session.commit()
            return jsonify({"code": 201, "data": shipping_details.json()}), 201
    except Exception as e:
        return jsonify({"code": 500, "message": "An error occurred while updating the shipping details.", "error": str(e)}), 500

# Create database tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database tables created.")

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
