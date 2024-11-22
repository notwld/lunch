from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db,Child,Order,OrderItem,MenuItem,Coupons
import stripe
from calendar import month_name

order = Blueprint('order', __name__)
stripe_keys = {
    "publishable_key": "pk_test_51QBLnNKvpNRsCJqfxmG8PuASERhdFSD03OuYCzs3bkzThj4o2FVXl7XTIbtGPr3rIYi87ImQ8xedqn6PfusaE5yv00G63f55Io",
    "secret_key": "sk_test_51QBLnNKvpNRsCJqfyoz2ds9no6RmGmynP4THyGYWOUdHZUqCttyqceoQ0K06A78Wavc9a9fIAMD6FXQZ0HWnKMeD00A0zSasxq",
}

stripe.api_key = stripe_keys["secret_key"]

@order.route('/order', methods=['GET'])
@login_required
def order_page():
    children = current_user.children
    today = datetime.now()
    current_year = today.year
    current_month = today.month 

    # Generate all weekdays for a given year and month
    def get_weekdays_of_month(year, month):
        days = []
        total_days = (date(year, month + 1, 1) - timedelta(days=1)).day if month < 12 else 31
        for day in range(1, total_days + 1):
            day_date = date(year, month, day)
            if day_date.weekday() < 5:  # Only weekdays (Monday-Friday)
                days.append(day_date)
        return days

    # Generate weekdays for the current and next month
    weekdays_by_month = {}
    for i in range(3):
        month = current_month + i
        year = current_year
        if month > 12:
            month -= 12
            year += 1
        month_key = f"{month_name[month]} {year}"  # Use month name and year as key
        weekdays = get_weekdays_of_month(year, month)
        weekdays_by_month[month_key] = weekdays

    # Prepare menu
    menu_items = MenuItem.query.all()
    menu = {
        "entrees": [],
        "sides": [],
        "produce": [],
        "desserts": [],
        "drinks": []
    }

    for item in menu_items:
        if item.type in menu:
            menu[item.type].append({
                "name": item.name,
                "price": item.price,
                "description": item.description,
                "cautions": item.cautions
            })

    # Determine locked days
    locked_days = {}
    for month_key, days in weekdays_by_month.items():
        locked_days[month_key] = {day.strftime('%Y-%m-%d'): day < today.date() for day in days}

    # Convert weekdays_by_month to string format for JSON compatibility
    weekdays_by_month_str = {
        month_key: [day.strftime('%Y-%m-%d') for day in days]
        for month_key, days in weekdays_by_month.items()
    }

    return render_template(
        'order.html',
        weekdays_by_month=weekdays_by_month_str,
        menu=menu,
        locked_days=locked_days,
        children=[
            {
                "id": child.id,
                "first_name": child.first_name,
                "last_name": child.last_name,
                "allergies": child.allergies or ""
            }
            for child in children
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
    if not child:
        return "Child not found.", 404
    
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


@order.route('/edit-order/<int:id>', methods=['GET'])
@login_required
def edit_order(id):
    # order = Order.query.get(id)
    # if order is None:
    #     flash('Order not found')
    #     return redirect('/')
    
    # edit_deadline = order.paid_at + timedelta(days=1)
    # if datetime.utcnow() > edit_deadline:
    #     flash('Order can only be edited within 1 day of payment.', 'error')
    #     return redirect('/')
    
    menu_items = MenuItem.query.all()
    menu = {
        "entrees": [],
        "sides": [],
        "produce": [],
        "desserts": [],
        "drinks": []
    }

    for item in menu_items:
        if item.type in menu:
            menu[item.type].append({
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "description": item.description,
                "cautions": item.cautions
            })
    order_items = OrderItem.query.filter_by(id=id).first()
    total = order_items.entree_price + order_items.side_price + order_items.produce_price + order_items.dessert_price + order_items.drink_price
    print(order_items)

    return render_template('edit_order.html',total=total,order_items=order_items, menu=menu,key=stripe_keys['publishable_key'])

@order.route('/edit-order/<int:id>', methods=['POST'])
@login_required
def edit_order_post(id):
    try:
        data = request.form
        print(dict(data))
        menu_items = []
        for each in dict(data):
            item = MenuItem.query.filter_by(id=int(data[each])).first()
            menu_items.append({
                "name": item.name,
                "price": item.price,
                "type": item.type
            })
        
        order_items = OrderItem.query.filter_by(id=id).first()
        order = Order.query.get(order_items.order_id)
        if order is None:
            flash('Order not found')
            return redirect('/')
        total_cost = 0
        for item in menu_items:
            if item['type'] == 'entrees':
                order_items.entree_name = item['name']
                order_items.entree_price = item['price']
                total_cost += item['price']
            elif item['type'] == 'sides':
                order_items.side_name = item['name']
                order_items.side_price = item['price']
                total_cost += item['price']
            elif item['type'] == 'produce':
                order_items.produce_name = item['name']
                order_items.produce_price = item['price']
                total_cost += item['price']
            elif item['type'] == 'desserts':
                order_items.dessert_name = item['name']
                order_items.dessert_price = item['price']
                total_cost += item['price']
            elif item['type'] == 'drinks':
                order_items.drink_name = item['name']
                order_items.drink_price = item['price']
                total_cost += item['price']

        print(total_cost)
        # check if new total cost is less than the previous total cost
        if total_cost < order.total_cost:
            amount = round(order.total_cost - total_cost, 2)
            print(amount,"is the amount to be refunded")
            refund = stripe.Refund.create(
                payment_intent=order.payment_intent_id,
                amount=int(amount * 100)
            )
            if refund.status == 'succeeded':
                flash('Refund successful')
            else:
                flash('Refund failed, please contact support')
        else:
            # If new total cost is greater, handle additional charge
            amount = round(total_cost - order.total_cost, 2)
            print(amount, "is the amount to be charged")
 

        order.total_cost = total_cost
        db.session.commit() 
        redirect(f'/')


            
        flash('Order updated successfully')
        # return redirect(f'/order/{id}')
        return redirect('/')
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        print(e)
        return redirect('/')




@order.route('/order/<int:id>/payment', methods=['GET'])
@login_required
def payment(id):
    order = Order.query.get(id)
    if order is None:
        flash('Order not found')
        return redirect('/')
    order_items = OrderItem.query.filter_by(order_id=order.id).all()
    amount = int(order.total_cost * 100)
    return render_template('checkout.html', order=order, order_items=order_items, amount=amount, key=stripe_keys['publishable_key'])

@order.route('/order/<int:id>/payment', methods=['POST'])
@login_required
def payment_post(id):
    # Retrieve the order
    order = Order.query.get(id)
    if not order:
        flash("Order not found.")
        return redirect("/")
   

    # Get payment method ID from the form
    payment_method_id = request.form.get("payment_method_id")
    if not payment_method_id:
        flash("Payment method not provided.")
        return redirect(f"/order/{id}/payment")

    # Calculate the total amount in cents (Stripe expects amount in the smallest currency unit)
    amount = int(order.total_cost * 100)

    try:
        # Create a new Stripe customer for the order
        customer = stripe.Customer.create(email=order.parent.email)

        # Create a PaymentIntent with the provided payment method
        payment_intent = stripe.PaymentIntent.create(
            customer=customer.id,
            description=f"Paid by {order.parent.email} for Order ID: {order.id}",
            amount=amount,
            currency="usd",
            payment_method=payment_method_id,
            off_session=True,  # Payment without user interaction
            confirm=True,      # Immediately confirm the payment
        )

        # Check if payment was successful
        if payment_intent.status == 'succeeded':
            flash(f"Payment successful for Order ID: {order.id}")
            order.status = "Paid"
            order.paid_at = datetime.now()
            order.payment_intent_id = payment_intent.id
            order.payment_method_id = payment_method_id
            order.cust_id = customer.id
            db.session.commit()  # Update the order status
        else:
            # Handle failed payments (e.g., declined card, insufficient funds)
            flash(f"Payment failed: {payment_intent.last_payment_error.message}")
            return redirect(f"/order/{id}/payment")

    except stripe.error.CardError as e:
        # Handle card errors (e.g., declined cards)
        flash(f"Payment failed: {e.error.message}")
        return redirect(f"/order/{id}/payment")

    except stripe.error.StripeError as e:
        # Handle other Stripe errors (e.g., API issues)
        flash(f"An error occurred: {e.user_message}")
        return redirect(f"/order/{id}/payment")

    except Exception as e:
        # Handle any unexpected errors
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(f"/order/{id}/payment")

    return redirect("/")

@order.route('/rate', methods=['POST'])
def rate_order():
    try:
        order_id = request.form['order_id']
        rating = float(request.form['rating'])
        if rating < 1 or rating > 5:
            flash('Invalid rating value. Please provide a rating between 1 and 5.')
            return redirect('/')
        if not order_id:
            flash('Order ID not provided.')
            return redirect('/')
        order = Order.query.get(order_id)
        if order:
            order.rating = rating
            db.session.commit()

        return redirect("/")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect('/')