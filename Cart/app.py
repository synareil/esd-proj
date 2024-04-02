from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

class Cart(db.Model):
    __tablename__ = 'cart'

    cartID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.String(100), nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(self, cartID, userID, active):
        self.cartID = cartID
        self.userID = userID
        self.active = active

    def json(self):
        return {"cartID": self.cartID, "userID": self.userID, "active": self.active}

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


#get_item_in_cart_by_userID
@app.route("/cart/<string:userID>")
def get_item_in_cart_by_userID(userID):
    cart = db.session.query(Cart).filter(Cart.userID == userID).filter(Cart.active == True).first()

    if not cart:
        cart = Cart(None, userID, active=True)
        db.session.add(cart)
        db.session.flush()
        db.session.refresh(cart)
        
    cart_items = db.session.query(CartItem).filter(CartItem.cartID == cart.cartID).all()
    cart_items_list = [item.json() for item in cart_items]
    return jsonify(
            {
                "code": 202,
                "data":cart_items_list
            }
        ), 202
    
#get_users_with_itemID_in_active_cart
@app.route("/cart/item/<string:itemID>")
def get_users_with_itemID_in_active_cart(itemID):
    carts = db.session.query(CartItem).filter(CartItem.itemID == itemID).all()

    users_return = []
    for cart in carts:
        cartID = cart.cartID
        userID = db.session.query(Cart).filter(Cart.cartID == cartID).filter(Cart.active == True).first()
        if userID != None:
            users_return.append(userID.userID)
        
        
    return jsonify(
            {
                "code": 202,
                "data": users_return
            }
        ), 202
    
# closecart
@app.route("/cart/close/<string:userID>", methods=["POST"])
def close_cart(userID):
    try:
        # Find the cart for the given userID
        cart = Cart.query.filter_by(userID=userID).filter_by(active=True).first()
        if not cart:
            return jsonify(
                {
                    "code": 404,
                    "message": "Cart not found."
                }
            ), 404
            
        cart.active = False
        db.session.commit()
        return jsonify(
                {
                    "code": 204,
                    "message": "No Content"
                }
            ), 204
    except Exception as e:
        return jsonify(
            {
                "code": 500, 
                "message": "An error occurred while updating the cart.", 
                "error": str(e)
            }
        ), 500
            
    
    
# update or delete item in cart by userID
@app.route("/cart/<string:userID>", methods=["PUT"])
def update_cart(userID):
    try:
        data = request.get_json()

        # Find the cart for the given userID
        cart = Cart.query.filter_by(userID=userID).filter_by(active=True).first()
        if not cart:
            cart = Cart(None, userID, active=True)
            db.session.add(cart)
            db.session.flush()
            db.session.refresh(cart)


        # Add item to cart if provided in the request
        if 'addItem' in data:
            for item in data['addItem']:
                itemID = item["itemID"]
                quantity = item["quantity"]
                cartItem = db.session.query(CartItem).filter(CartItem.cartID ==  cart.cartID).filter(CartItem.itemID == itemID).first()
                
                if cartItem:
                    cartItem.quantity += quantity
                else:
                    cart_item = CartItem(cart.cartID, itemID, quantity)
                    db.session.add(cart_item)

        # Delete item from cart if provided in the request
        if 'deleteItem' in data:
            for item in data['deleteItem']:
                itemID = item["itemID"]
                quantity = item["quantity"]
                cart_item = CartItem.query.filter_by(cartID=cart.cartID, itemID=itemID).first()
                if cart_item.quantity - quantity <= 0:
                    db.session.delete(cart_item)
                else:
                    cart_item.quantity -= quantity


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