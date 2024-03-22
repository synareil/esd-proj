from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flasgger import Swagger


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER'] = {
    'title': 'Order microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Allows create, retrieve, update, and delete of Orders'
}
swagger = Swagger(app)

db = SQLAlchemy(app)


class Order(db.Model):
    __tablename__ = 'orders'


    orderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userID = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(64), nullable=False)


    def __init__(self, orderID, userID, status):
        self.orderID = orderID
        self.userID = userID
        self.status = status


    def json(self):
        return {"orderID": self.orderID, "userID": self.userID, "status": self.status}
    
    
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

# get all orders
@app.route("/order")
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
    orderlist = db.session.scalars(db.select(Order)).all()


    if True:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders."
        }
    ), 404

# get order by orderID
@app.route("/order/<string:orderID>")
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
    order = db.session.scalars(
    	db.select(Order).filter_by(orderID=orderID).
    	limit(1)
    ).first()


    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Order not found."
        }
    ), 404

# delete order by orderID
@app.route("/order/<string:orderID>", methods=["DELETE"])
def delete_order_by_orderID(orderID):
    """
    Delete a single order by orderID.
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
    order = db.session.scalars(
    	db.select(Order).filter_by(orderID=orderID).
    	limit(1)
    ).first()


    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify(
            {
                "code": 204,
            }
        ), 204
    return jsonify(
        {
            "code": 404,
            "message": "Order not found."
        }
    ), 404
    
# get order by status
@app.route("/order/status/<string:status>")
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
    orderlist = db.session.scalars(
    	db.select(Order).filter_by(status=status)
    ).all()


    if orderlist:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No orders found."
        }
    ), 404

# create order + orderitems
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
                        properties:
                            userID:
                                type: integer
                                description: descripiton
                            status:
                                type: string
                                description: descripiton                                
                            items:
                                type: array
                                description: descripiton                                
    responses:
        201:
            description: Order created successfully.
        400:
            description: Invalid input or order already exists.
        500:
            description: An error occurred creating the order.
    """

    # data = request.get_json()
    # # Check if a record with the same ShippingID already exists
    # existing = Order.query.filter_by(orderID=data.get('orderID')).first()
    # if existing is not None:
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "data": {
    #                 "ShippingID": data.get('ShippingID')
    #             },
    #             "message": "A record with the same ShippingID of " +  data.get('ShippingID') + "already exists."
    #         }
    #     ), 400

    data = request.get_json()
    order = Order(None, userID=data['userID'], status=data['status'])

    db.session.add(order)
    db.session.flush()
    db.session.refresh(order)
    orderID = order.orderID
    
    for item in data["items"]:
        itemID = int(item.get("itemID"))
        quantity = item.get("quantity")
        orderItem_model = OrderItem(orderID, itemID, quantity)
        try:
            db.session.add(orderItem_model)
        except:
            return jsonify(
                {
                    "code": 500,
                    "data": {
                        "orderID": orderID
                    },
                    "message": "An error occurred creating the order."
                }
                ), 500
            
    db.session.commit()
    return jsonify(
        {
            "code": 201,
            "message": "Order created succesfully",
            "data": {
                        "orderID": orderID
                    }
        }
    ), 201

# update order by orderID
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
        name: status
        required: true
        schema:
          type: object
          properties:
            status:
              type: string
              description: New status of the order
    responses:
        200:
            description: Order updated successfully.
        404:
            description: Order not found.
        500:
            description: An error occurred while updating the order.
    """
    try:
        order = db.session.scalars(
        db.select(Order).filter_by(orderID=orderID).
        limit(1)
        ).first()
        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "orderID": orderID
                    },
                    "message": "Order not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data['status']:
            order.status = data['status']
            return jsonify(
                {
                    "code": 200,
                    "data": order.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "orderID": orderID
                },
                "message": "An error occurred while updating the order. " + str(e) 
            }
        ), 500

# get order + order items by orderID
@app.route("/order/orderitem/<string:orderID>")
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
    order = db.session.scalars(
    	db.select(Order).filter_by(orderID=orderID).
    	limit(1)
    ).first()


    if order:
        itemlist = db.session.scalars(
    	db.select(OrderItem).filter_by(orderID=orderID)
        ).all()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "order": order.json(),
                    "items": [item.json() for item in itemlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No orders found."
        }
    ), 404 

with app.app_context():
    db.create_all()
    print("Database tables created.")
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)