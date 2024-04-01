from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from sqlalchemy.exc import SQLAlchemyError
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
swagger = Swagger(app)
db = SQLAlchemy(app)


class Item(db.Model):
    __tablename__ = 'item'


    itemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(64), nullable=False)
    qty = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    salesPrice = db.Column(db.Float(precision=2), nullable=True)
    image = db.Column(db.String(100), nullable=True)


    def __init__(self, itemID, name, description, qty, category, price, salesPrice, image):
        self.itemID = itemID
        self.name = name
        self.description = description
        self.qty = qty
        self.category = category
        self.price = price
        self.salesPrice = salesPrice
        self.image = image


    def json(self):
        return {"itemID": self.itemID, "name": self.name, "description": self.description, "qty": self.qty, "category": self.category, "price": self.price, "salesPrice": self.salesPrice, "image":self.image}

with app.app_context():
    db.create_all()
    
# get all items
@app.route('/item', methods=['GET'])
def get_all():
    """
    Retrieves all items from the database.
    ---
    responses:
        200:
            description: A list of items.
        404:
            description: No items found.
    """
    itemlist = db.session.scalars(db.select(Item)).all()

    if True:
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
@app.route("/item/<string:itemID>", methods=['GET'])
def get_item_by_itemID(itemID):
    """
    Retrieves a single item by itemID.
    ---
    parameters:
      - name: itemID
        in: path
        type: string
        required: true
        description: The ID of the item to retrieve.
    responses:
        200:
            description: Details of an item.
        404:
            description: Item not found.
    """
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
@app.route("/item", methods=['POST'])
def create_item():
    """
    Creates a new item in the database.
    ---
    parameters:
      - in: body
        name: item
        description: The item to create.
        schema:
          type: object
          required:
            - name
            - description
            - qty
            - category
            - price
            - salesPrice
          properties:
            name:
              type: string
            description:
              type: string
            qty:
              type: integer
            category:
              type: string
            price:
              type: number
            salesPrice:
              type: number
    responses:
        201:
            description: Item created successfully.
        400:
            description: Invalid input.
        500:
            description: Internal server error.
    """
    # if (db.session.scalars(
    #   db.select(Item).filter_by(itemID=itemID).
    #   limit(1)
    #   ).first()
    #   ):
    #     return jsonify(
    #         {
    #             "code": 400,
    #             "data": {
    #                 "itemID": itemID
    #             },
    #             "message": "Item already exists."
    #         }
    #     ), 400


    data = request.get_json()
    item = Item(**data, itemID = None)


    try:
        db.session.add(item)
        db.session.commit()
        db.session.refresh(item)
    except:
        return jsonify(
            {
                "code": 500,
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
def update_item(itemID):
    """
    Updates an existing item by itemID.
    ---
    parameters:
      - name: itemID
        in: path
        type: string
        required: true
        description: The ID of the item to update.
      - in: body
        name: item
        description: Updated item details.
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            qty:
              type: integer
            category:
              type: string
            price:
              type: number
            salesPrice:
              type: number
    responses:
        200:
            description: Item updated successfully.
        404:
            description: Item not found.
        500:
            description: Internal server error.
    """
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
                if int(data['qty']) < 0:
                    item.qty = item.qty + int(data['qty'])
                else:
                    item.qty = data['qty']
            if 'salesPrice' in data:
                item.salesPrice = data['salesPrice']
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

# update item by itemID
@app.route("/item/checkout", methods=['POST'])
def checkout_items():
    data = request.get_json()
    if data:
        try:
            totalPrice = 0
            for item_checkout in data["checkout"]:
                itemID = int(item_checkout.get("itemID"))
                quantity = item_checkout.get("quantity")
                
                item = db.session.scalars(
                db.select(Item).filter(Item.itemID==itemID).
                limit(1)
                ).first()
                
                
                if item.salesPrice:
                    totalPrice += item.salesPrice
                else:
                    totalPrice += item.price
                    
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
                    
                item.qty = item.qty - quantity
                if item.qty < 0:
                    db.session.rollback()
                    return jsonify(
                        {
                            "code": 422,
                            "data": {
                                "itemID": itemID,
                                "quantity": item.qty + quantity,
                                "requestedQuantity": quantity
                            },
                            "message": "Item out of stock"
                        }
                    ), 422
            db.session.commit()
            return jsonify(
                        {
                            "code": 200,
                            "data": {
                                "totalPrice": totalPrice
                            }
                        }
                    ), 200
        
        
        except SQLAlchemyError as e:
            db.session.rollback()
 
#search
@app.route('/item/search')
def search():
    query = request.args.get('q')
    if query:
        items = Item.query.filter(
            (Item.name.like(f'%{query}%')) | 
            (Item.description.like(f'%{query}%')) | 
            (Item.category.like(f'%{query}%'))
        ).all()
        return jsonify([item.json() for item in items])
    else:
        return jsonify([]), 400
               
# rollback for checkout
@app.route("/item/checkout/rollback", methods=['POST'])
def rollback_checkout_items():
    data = request.get_json()
    if data:
        try:
            for item_checkout in data["checkout"]:
                itemID = int(item_checkout["itemID"])
                quantity = item_checkout["quantity"]
                
                item = db.session.scalars(
                db.select(Item).filter(Item.itemID==itemID).
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
                    
                item.qty = item.qty + quantity
                if item.qty < 0:
                    db.session.rollback()
                    return jsonify(
                        {
                            "code": 422,
                            "data": {
                                "itemID": itemID,
                                "quantity": item.qty + quantity,
                                "requestedQuantity": quantity
                            },
                            "message": "Item out of stock"
                        }
                    ), 422
            db.session.commit()
            return jsonify(
                {
                    "code": 202,
                }
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            
                

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)