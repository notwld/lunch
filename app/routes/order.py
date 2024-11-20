from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db, Cart, CartItem,MenuItem ,Child

order = Blueprint('order', __name__)

@order.route('/order', methods=['GET'])
@login_required
def order_page():
    childern = current_user.children
    today = datetime.now()
    current_year = today.year
    current_month = today.month

    # Generate all weekdays of the current month
    def get_weekdays_of_month(year, month):
        days = []
        total_days = (date(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        for day in range(1, total_days + 1):
            day_date = date(year, month, day)
            if day_date.weekday() < 5:  # Only weekdays (Monday-Friday)
                days.append(day_date)
        return days

    weekdays = get_weekdays_of_month(current_year, current_month)

    # Sample menu (you can fetch actual menu from the database)
    menu = {
        "entrees": [{"name": "Buttered Noodles V", "price": 3.5}, {"name": "Pasta", "price": 4.0}],
        "sides": [{"name": "All Beef Meatballs", "price": 2.0}, {"name": "Grilled Veggies", "price": 2.5}],
        "produce": [{"name": "Locally Grown Apple Slices", "price": 1.0}, {"name": "Carrot Sticks", "price": 1.2}],
        "desserts": [{"name": "Sugar Cookie", "price": 1.5}, {"name": "Brownie", "price": 2.0}],
        "drinks": [{"name": "No Drink", "price": 0.0}, {"name": "Orange Juice", "price": 1.5}],
    }

    # Determine locked days
    locked_days = {day: day < today.date() for day in weekdays}

    return render_template(
        'order.html',
        weekdays=weekdays,
        menu=menu,
        locked_days=locked_days,
        current_date=today.date(),
        children=childern
    )
@order.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    order_data = request.json  # Assuming you send JSON from the frontend
    child = Child.query.filter_by(id=order_data['child_id']).first()

    filtered_selections = []
    for day in order_data['items']:
        if day['entree']['name'] == 'None' and day['side']['name'] == 'None' and day['produce']['name'] == 'None' and day['dessert']['name'] == 'None' and day['drink']['name'] == 'None':
            continue
        filtered_selections.append(day)

    if not filtered_selections:
        return "No valid items to add to cart.", 400  # If no valid selections, return a message
    return jsonify({
        "child": child.first_name + " " + child.last_name,
        "cart": filtered_selections
    })
    # # Create a new cart for the current user and child
    # new_cart = Cart(user_id=current_user.id, child_id=order_data['child_id'])
    # db.session.add(new_cart)
    # try:
    #     db.session.commit()  # Commit to get the cart's ID
    # except Exception as e:
    #     print(f"Error creating cart: {e}")
    #     db.session.rollback()

    # # Iterate over the filtered selections and add CartItems
    # for day in filtered_selections:
    #     # Fetch MenuItems for each category (entree, side, produce, dessert, drink)
    #     entree = MenuItem.query.filter_by(name=day['entree']['name'], type='entree').first()
    #     side = MenuItem.query.filter_by(name=day['side']['name'], type='side').first()
    #     produce = MenuItem.query.filter_by(name=day['produce']['name'], type='produce').first()
    #     dessert = MenuItem.query.filter_by(name=day['dessert']['name'], type='dessert').first()
    #     drink = MenuItem.query.filter_by(name=day['drink']['name'], type='drink').first()

    #     # Debugging: Check if MenuItems exist
    #     if not entree or not side or not produce or not dessert or not drink:
    #         print(f"Missing MenuItem for day {day['day']}")
    #         continue  # Skip this day if any MenuItem is missing
    #     try:
    #         cart_item = CartItem(
    #         cart_id=new_cart.id,
    #         day=day['day'],
    #         entree=entree,
    #         side=side,
    #         produce=produce,
    #         dessert=dessert,
    #         drink=drink,
    #         price=entree.price + side.price + produce.price + dessert.price + drink.price)
    #         db.session.add(cart_item)
    #     except Exception as e:
    #         print(f"Error adding cart item: {e}")
    #         db.session.rollback()
    #         return "Failed to add items to cart.", 500

    # # Commit all changes
    # try:
    #     db.session.commit()
    #     return "Items added to cart successfully.", 200
    # except Exception as e:
    #     print(f"Error adding cart items: {e}")
    #     db.session.rollback()  # Roll back if there's an error
    #     return "Failed to add items to cart.", 500

@order.route('/cart', methods=['GET'])
@login_required
def cart():
    # Get the cart for the current user, ensuring a cart exists
    cart = CartItem.query.all()
    for c in cart:
        print(c.day)
    
    return render_template('cart.html', cart=cart)
        

@order.route('/cart/remove/', methods=['GET'])
@login_required
def remove_cart_item():
    cart_item = Cart.query.all()
    for c in cart_item:
        db.session.delete(c)
        db.session.commit()
    return redirect('/cart')

