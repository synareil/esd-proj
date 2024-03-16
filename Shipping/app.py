from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Shipping(db.Model):
    __tablename__ = 'shipping'

    ShippingID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    UserID= db.Column(db.Integer, nullable=False)
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


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

# GET ALL shipping details
@app.route("/shipping/")
def get_all():
    shipping_details = db.session.scalars(db.select(Shipping)).all()

    return jsonify(
        {
            "code": 200,
            "data": {
                "Details": [data.json() for data in shipping_details]
            }
        }
    )

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
@app.route("/shipping/createshipping", methods=['POST'])
def create_shipping_record():
    data = request.get_json()
    print(data)

    data.pop('ShippingID', None)
    shipping_details = Shipping(**data)

    try:
        db.session.add(shipping_details)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "ShippingID": data.get('ShippingID', '')  # Assuming OrderID is part of the request data
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

# update shipping Record by ShippingID -> not sure if want update via orderID or shippingID
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
                    "message": "Shipping ID not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data:
            if 'shippingAddress' in data:
                shipping_details.shippingAddress = data['shippingAddress']
            if 'ShippingStatus' in data:
                shipping_details.ShippingStatus = data['ShippingStatus']
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
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
    
# @app.route("/createshipping/<string:ShippingID>", methods=['POST'])
# def create_shipping_record(ShippingID):
#     if (db.session.scalars(
#       db.select(Shipping).filter_by(ShippingID=ShippingID).
#       limit(1)
#       ).first()
#       ):
#         return jsonify(
#             {
#                 "code": 400,
#                 "data": {
#                     "ShippingID": ShippingID
#                 },
#                 "message": "Shipping record " + ShippingID + " already exists."
#             }
#         ), 400

#     data = request.get_json()
#     print(data)
#     shipping_details = Shipping(ShippingID, **data)


#     try:
#         db.session.add(shipping_details)
#         db.session.commit()
#     except:
#         return jsonify(
#             {
#                 "code": 500,
#                 "data": {
#                     "OrderID": OrderID
#                 },
#                 "message": "An error occurred creating the shipping details."
#             }
#         ), 500
#     return jsonify(
#         {
#             "code": 201,
#             "data": shipping_details.json()
#         }
#     ), 201

with app.app_context():
    db.create_all()
    print("Database tables created.")
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)