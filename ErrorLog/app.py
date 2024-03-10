
#####################################
#Simple Service to store error logs
#####################################

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/proj_error'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Errors(db.Model):
    __tablename__ = 'Error'

    ErrorID = db.Column(db.Integer, primary_key=True)
    DateTime = db.Column(db.DateTime, nullable=False) #not sure if this is the correct format -> idk if yall want use the sql date or should we just create the date ourselves. 
    #new_record = MyModel(Date=date.today(), ...) -> how it works!
    Desc = db.Column(db.String(100), nullable=False)
    Microservice = db.Column(db.String(100), nullable=False) #format: "Shipping, Order" -> split by "," into an array later

    def __init__(self, ErrorID, DateTime, Desc, Microservice):
        self.ErrorID = ErrorID
        self.DateTime = DateTime
        self.Desc = Desc
        self.Microservice = Microservice

    def json(self):
        return {"ErrorID": self.ErrorID, "DateTime": self.DateTime,
                "Desc": self.Desc, "Microservice": self.Microservice}

# GET Error Logs
@app.route("/error")
def get_all_errors():
    error_logs = db.session.scalars(db.select(Errors)).all()


    if len(error_logs):
        return jsonify(
            {
                "code": 201,
                "data": {
                    "Details": [error.json() for error in error_logs]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is nothing in error logs."
        }
    ), 404

# get error details by errorID -> can consider creating another function for getting via date etc
@app.route("/error/<string:ErrorID>")
def get_error_log_by_errorID(ErrorID):
    details = db.session.scalars(
    	db.select(Errors).filter_by(ErrorID=ErrorID).
    	limit(1)
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
            "message": "Error Log: " + ErrorID + "not found."
        }
    ), 404

# create new error log
@app.route("/error/<string:ErrorID>", methods=['POST'])
def create_error_log(ErrorID):
    if (db.session.scalars(
        db.select(Errors).filter_by(ErrorID=ErrorID).
        limit(1)
        ).first()
        ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "ErrorID": ErrorID
                },
                "message": "Error record " + ErrorID + " already exists."
            }
        ), 400

    data = request.get_json()
    print(data)
    error_log_details = Errors(ErrorID, **data)

    try:
        db.session.add(error_log_details)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "ErrorID": ErrorID
                },
                "message": "An error occurred creating the error log."
            }
        ), 500
    return jsonify(
        {
            "code": 201,
            "data": error_log_details.json()
        }
    ), 201


#Lowkey not sure if we need this for the AMQP part
# import pika

# def callback(ch, method, properties, body):
#     print("Received %r" % body)

# connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
# channel = connection.channel()

# channel.queue_declare(queue='error_queue')

# channel.basic_consume(queue='error_queue', on_message_callback=callback, auto_ack=True)

# print('Waiting for messages. To exit press CTRL+C')
# channel.start_consuming()

if __name__ == '__main__':
    app.run(port=5000, debug=True)