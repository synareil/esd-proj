from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Cart(db.Model):
    __tablename__ = 'cart'

    cartID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(100), nullable=False)

    def __init__(self, cartID, userID):
        self.cartID = cartID
        self.userID = userID

    def json(self):
        return {"cartID": self.cartID, "userID": self.userID}

class CartItem(db.Model):
    __tablename__ = 'cartItem'

    cartID = db.Column(db.Integer, primary_key=True)
    itemID = db.Column(db.String(100), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer)

    def __init__(self, cartID, itemID, quantity):
        self.cartID = cartID
        self.itemID = itemID
        self.quantity = quantity

    def json(self):
        return {"cartID": self.cartID, "itemID": self.itemID, "quantity": self.quantity}

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200

#get all carts 
@app.route("/cart")
def get_cart():
    cartlist = db.session.scalars(db.select(Cart)).all()

    if True:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "cart": [cart.json() for cart in cartlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There is nothing in the cart."
        }
    ), 404


#get cart by userID
@app.route("/cart/<string:userID>")
def get_item_in_cart_by_userID(userID):
    cart = db.session.scalars(
    	db.select(Cart).filter_by(userID=userID)
    ).first()

    if cart == None:   
        return jsonify(
            {
                "code": 404,
                "message": "Cart not found."
            }
        ), 404
        
    cart_items = db.session.query(CartItem).filter(CartItem.cartID == cart.cartID).all()
    cart_items_list = [item.json() for item in cart_items]
    return jsonify(
            {
                "code": 202,
                "data":cart_items_list
            }
        ), 202
    

# update or delete item in cart by userID
@app.route("/cart/<string:userID>", methods=["PUT"])
def update_cart(userID):
    try:
        data = request.get_json()

        # Find the cart for the given userID
        cart = Cart.query.filter_by(userID=userID).first()
        if not cart:
            cart = Cart(None, userID)
            db.session.add(cart)
            db.session.flush()
            db.session.refresh(cart)


        # Add item to cart if provided in the request
        if 'addItem' in data:
            itemID = data['addItem']
            if 'quanity' in data:
                quantity = data['quantity']
            else:
                quantity = 1
            cart_item = CartItem(cart.cartID, itemID, quantity)
            db.session.add(cart_item)

        # Delete item from cart if provided in the request
        if 'deleteItem' in data:
            itemID = data['deleteItem']
            cart_item = CartItem.query.filter_by(cartID=cart.cartID, itemID=itemID).first()
            if cart_item:
                db.session.delete(cart_item)

        # Commit changes to the database
        db.session.commit()

        return jsonify(
            {
                "code": 200,
                "message": "Cart updated successfully"
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500, 
                "message": "An error occurred while updating the cart.", 
                "error": str(e)
            }
        ), 500
        
with app.app_context():
    db.create_all()
    print("Database tables created.")
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)