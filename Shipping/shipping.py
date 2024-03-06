#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


#this is for shipping record
@app.route("/shipping", methods=['POST'])
def receiveOrder():
    # Check if the order contains valid JSON
    order = None
    if request.is_json:
        order = request.get_json()
        result = processOrder(order)
        return jsonify(result), result["code"]
    else:
        data = request.get_data()
        print("Received an invalid order:")
        print(data)

        #SEND IT TO THE DATABASE FOR LOGGING / Record in File for database HERE

        return jsonify({"code": 400,
                        # make the data string as we dunno what could be the actual format
                        "data": str(data),
                        "message": "Order should be in JSON."}), 400  # Bad Request input


def processOrder(order):
    print("Processing an order for shipping:")
    print(order)
    # Can do anything here, but aiming to keep it simple (atomic)
    order_id = order['order_id']
    # If customer id contains "ERROR", simulate failure
    if "ERROR" in order['customer_id']:
        code = 400
        message = '[FAIL] Could not create shipping order record for order ' + order_id
        #SEND IT TO THE DATABASE FOR LOGGING / Record in File for database HERE

    else:  # simulate success
        code = 201
        message = '[SUCCESS] Created shipping order record for order ' + order_id + ' successfully.'
        #SEND IT TO THE DATABASE FOR LOGGING / Record in File for database HERE

    print(message)
    print()

    return {
        'code': code,
        'data': {
            'order_id': order_id
        },
        'message': message
    }


# execute this program only if it is run as a script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          ": shipping for orders ...")
    app.run(host='0.0.0.0', port=5002, debug=True)
