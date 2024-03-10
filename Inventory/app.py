from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/proj_inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


class Item(db.Model):
    __tablename__ = 'item'


    itemID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    salesPrice = db.Column(db.Float(precision=2), nullable=False)


    def __init__(self, itemID, name, description, qty, category, price, salesPrice):
        self.itemID = itemID
        self.name = name
        self.description = description
        self.qty = qty
        self.category = category
        self.price = price
        self.salesPrice = salesPrice


    def json(self):
        return {"itemID": self.itemID, "name": self.name, "description": self.description, "qty": self.qty, "category": self.category, "price": self.price, "salesPrice": self.salesPrice}


# get all items
@app.route("/item")
def get_all():
    itemlist = db.session.scalars(db.select(Item)).all()


    if len(itemlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "items": [item.json() for item in itemlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no items."
        }
    ), 404

# get item by itemID
@app.route("/item/<string:itemID>")
def get_item_by_itemID(itemID):
    item = db.session.scalars(
    	db.select(Item).filter_by(itemID=itemID).
    	limit(1)
    ).first()


    if item:
        return jsonify(
            {
                "code": 200,
                "data": item.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Item not found."
        }
    ), 404

# create item
@app.route("/item/<string:itemID>", methods=['POST'])
def create_item(itemID):
    if (db.session.scalars(
      db.select(Item).filter_by(itemID=itemID).
      limit(1)
      ).first()
      ):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "itemID": itemID
                },
                "message": "Item already exists."
            }
        ), 400


    data = request.get_json()
    print(data)
    item = Item(itemID, **data)


    try:
        db.session.add(item)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "itemID": itemID
                },
                "message": "An error occurred creating the item."
            }
        ), 500
    return jsonify(
        {
            "code": 201,
            "data": item.json()
        }
    ), 201


# update item by itemID
@app.route("/item/<string:itemID>", methods=['PUT'])
def update_book(itemID):
    try:
        item = db.session.scalars(
        db.select(Item).filter_by(itemID=itemID).
        limit(1)
        ).first()
        if not item:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "itemID": itemID
                    },
                    "message": "Item not found."
                }
            ), 404

        # update status
        data = request.get_json()
        if data:
            if 'name' in data:
                item.name = data['name']
            if 'qty' in data:
                item.qty = data['qty']
            if 'description' in data:
                item.description = data['description']
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": item.json()
                }
            ), 200
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "itemID": itemID
                },
                "message": "An error occurred while updating the item. " + str(e) 
            }
        ), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)