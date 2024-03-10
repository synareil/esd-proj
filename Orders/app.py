from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/proj_order'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Order(db.Model):
    __tablename__ = 'orders'


    orderID = db.Column(db.Integer, primary_key=True)
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
    itemID = db.Column(db.Integer, nullable=False)


    def __init__(self, orderID, itemID):
        self.orderID = orderID
        self.itemID = itemID


    def json(self):
        return {"orderID": self.orderID, "itemID": self.itemID}

# get all orders
@app.route("/order")
def get_all():
    orderlist = db.session.scalars(db.select(Order)).all()


    if len(orderlist):
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

# get order by status
@app.route("/order/status/<string:status>")
def get_order_by_status(status):
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
@app.route("/order/<string:orderID>", methods=["POST"])
def create_order(orderID):
    if (db.session.scalars(
      db.select(Order).filter_by(orderID=orderID).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "orderID": orderID
                },
                "message": "Order already exists."
            }
        ), 400


    data = request.get_json()
    print(data)
    order = Order(orderID, data['userID'], data['status'])
    orderItemList = []
    for item in data["items"]:
        orderItemList.append(OrderItem(orderID, item))


    try:
        db.session.add(order)
        db.session.add_all(orderItemList)
        db.session.commit()
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
    return jsonify(
        {
            "code": 201,
            "data": order.json(),
            "items": [item.json() for item in orderItemList]
        }
    ), 201

# update order by orderID
@app.route("/order/<string:orderID>", methods=["PUT"])
def update_order(orderID):
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

# get order items by orderID
@app.route("/orderitem/<string:orderID>")
def get_orderitem_by_orderID(orderID):
    pass


if __name__ == '__main__':
    app.run(port=5000, debug=True)