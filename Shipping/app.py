from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/proj_shipping'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Shipping(db.Model):
    __tablename__ = 'Shipping'

    ShippingID = db.column(db.Integer, primary_key=True)
    OrderID = db.column(db.Integer, nullable=False)
    UserID= db.column(db.Integer, nullable=False)
    shippingAddress = db.column(db.String(100), nullable=False)
    ShippingStatus = db.column(db.String(100), nullable=False)

    def __init__(self, ShippingID, OrderID, UserID, shippingAddress, ShippingStatus):
        self.ShippingID = ShippingID
        self.OrderID = OrderID
        self.UserID = UserID
        self.shippingAddress = shippingAddress
        self.ShippingStatus = ShippingStatus

    def json(self):
        return {"ShippingID": self.ShippingID, "OrderID": self.OrderID, "UserID": self.UserID, 
                "shippingAddress": self.shippingAddress, "ShippingStatus": self.ShippingStatus}

# GET shipping details
@app.route("/shipping")
def get_all():
    shipping_details = db.session.scalars(db.select(Shipping)).all()


    if len(shipping_details):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Details": [data.json() for data in shipping_details]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is nothing in shipping_details."
        }
    ), 404

# get shipping_details by OrderID
@app.route("/shipping/<string:OrderID>")
def get_shipping_details_by_OrderID(OrderID):
    details = db.session.scalars(
    	db.select(Shipping).filter_by(OrderID=OrderID).
    	limit(1) #not sure if want to limit 1 for the shipping records, for now i assume so. 
    ).first()


    if details:
        return jsonify(
            {
                "code": 200,
                "data": details.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Shipping details not found."
        }
    ), 404

# create new shipping record
@app.route("/shipping/<string:OrderID>", methods=['POST'])
def create_shipping_record(OrderID):
    if (db.session.scalars(
      db.select(Shipping).filter_by(OrderID=OrderID).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "OrderID": OrderID
                },
                "message": "Shipping record for " + OrderID+ " already exists."
            }
        ), 400

    data = request.get_json()
    print(data)
    shipping_details = Shipping(OrderID, **data)


    try:
        db.session.add(shipping_details)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "OrderID": OrderID
                },
                "message": "An error occurred creating the shipping details."
            }
        ), 500
    return jsonify(
        {
            "code": 201,
            "data": shipping_details.json()
        }
    ), 201


# update shipping Record by ShippingID
@app.route("/shipping/<string:ShippingID>", methods=['PUT'])
def update_shipping_records(ShippingID):
    try:
        shipping_details = db.session.scalars(
        db.select(Shipping).filter_by(ShippingID=ShippingID).
        limit(1)
        ).first()
        if not shipping_details:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "ShippingID": ShippingID
                    },
                    "message": "Shipping details not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data:
            if 'shippingAddress' in data:
                shipping_details.shippingAddress = data['shippingAddress']
            if 'ShippingStatus ' in data:
                shipping_details.ShippingStatus = data['ShippingStatus']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": shipping_details.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "ShippingID": ShippingID
                },
                "message": "An error occurred while updating the shipping details. " + str(e) 
            }
        ), 500

#Lowkey not sure if we need this for the AMQP part
# import pika

# def callback(ch, method, properties, body):
#     print("Received %r" % body)

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()

# channel.queue_declare(queue='shipping_queue')

# channel.basic_consume(queue='shipping_queue', on_message_callback=callback, auto_ack=True)

# print('Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()

if __name__ == '__main__':
    app.run(port=5000, debug=True)