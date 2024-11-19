from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date

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
