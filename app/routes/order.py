from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db,Child,Order,OrderItem,MenuItem,Coupons

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

    menu_items = MenuItem.query.all()
    menu = {
        "entrees": [],
        "sides": [],
        "produce": [],
        "desserts": [],
        "drinks": []
    }

    # Group menu items by their type
    for item in menu_items:
        if item.type in menu:
            menu[item.type].append({"name": item.name, "price": item.price, "description": item.description,"cautions": item.cautions})

    # Determine locked days
    locked_days = {day: day < today.date() for day in weekdays}

    return render_template(
        'order.html',
        weekdays=weekdays,
        menu=menu,
        locked_days=locked_days,
        current_date=today.date(),
        children=[
    {"id": child.id, "first_name": child.first_name, "last_name": child.last_name, "allergies": child.allergies or ""}
    for child in childern
]

    )
@order.route('/get-child-allergies/<int:child_id>', methods=['GET'])
@login_required
def get_child_allergies(child_id):
    child = Child.query.get_or_404(child_id)
    return jsonify({"allergies": child.allergies})

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
@order.route('/cart', methods=['GET'])
def cart():
    return render_template('cart.html')

@order.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_data = request.json.get("cart", [])
    discount = request.json.get("discount", None)
    coupon_code = request.json.get("coupon_code", None)
    parent_id = current_user.id

    if not cart_data or not parent_id:
        return jsonify({"error": "Invalid data"}), 400

    try:
        # Create a single order
        order = Order(
            parent_id=parent_id,
            order_date=datetime.now(),
            total_cost=0.0,  # Placeholder, we'll calculate later
            status="Pending"
        )
        db.session.add(order)

        total_cost = 0  # Initialize total cost for the order

        for item in cart_data:
            child_name = item['child']
            child = Child.query.filter_by(
                first_name=child_name.split()[0],
                last_name=child_name.split()[1]
            ).first()

            if not child:
                return jsonify({"error": f"Child {child_name} not found"}), 404

            for cart_item in item['cart']:
                # Create OrderItem
                order_item = OrderItem(
                    order=order,
                    child_id=child.id,
                    day=cart_item['day'],
                    dessert_name=cart_item['dessert']['name'],
                    dessert_price=cart_item['dessert']['price'],
                    drink_name=cart_item['drink']['name'],
                    drink_price=cart_item['drink']['price'],
                    entree_name=cart_item['entree']['name'],
                    entree_price=cart_item['entree']['price'],
                    produce_name=cart_item['produce']['name'],
                    produce_price=cart_item['produce']['price'],
                    side_name=cart_item['side']['name'],
                    side_price=cart_item['side']['price'],
                )
                db.session.add(order_item)

                # Update total cost
                total_cost += order_item.total_price

        # Update order total cost after calculating
        order.total_cost = float(total_cost)
        if discount and coupon_code:
            # discount is in percentage
            order.total_cost *= (1 - discount / 100)
            order.total_cost = round(order.total_cost, 2)
            coupon = Coupons.query.filter_by(code=coupon_code).first()
            coupon.status = "Used"
            db.session.add(coupon)




        db.session.commit()

        return jsonify({"message": "Order placed successfully", "order_id": order.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@order.route('/delete-order/<int:id>', methods=['DELETE'])
@login_required
def delete_order(id):
    order = Order.query.get(id)
    order.status = "Cancelled"
    db.session.commit()
    flash('Order Cancelled successfully')
    return redirect('/')

@order.route('/order/<int:id>', methods=['GET'])
@login_required
def order_detail(id):
    order = Order.query.get(id)
    if order is None:
        flash('Order not found')
        return redirect('/')
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    child = Child.query.get(order_items[0].child_id)
    return render_template('order_details.html', order=order, order_items=order_items ,child=child)

