from app.models import db, MenuItem
from app import create_app
# Define the menu items

menu = {
    "entrees": [{"name": "Buttered Noodles V", "price": 3.5}, {"name": "Pasta", "price": 4.0}],
    "sides": [{"name": "All Beef Meatballs", "price": 2.0}, {"name": "Grilled Veggies", "price": 2.5}],
    "produce": [{"name": "Locally Grown Apple Slices", "price": 1.0}, {"name": "Carrot Sticks", "price": 1.2}],
    "desserts": [{"name": "Sugar Cookie", "price": 1.5}, {"name": "Brownie", "price": 2.0}],
    "drinks": [{"name": "No Drink", "price": 0.0}, {"name": "Orange Juice", "price": 1.5}],
}

# Function to add menu items
def add_menu_items():
    for category, items in menu.items():
        for item in items:
            # Check if the item already exists to prevent duplicates
            existing_item = MenuItem.query.filter_by(name=item['name'], type=category).first()
            if not existing_item:
                # Create new menu item
                new_item = MenuItem(
                    name=item['name'],
                    price=item['price'],
                    type=category,  # Use category name (e.g., 'Entree', 'Side', etc.)
                    description="",  # Optional: You can add a description if you want
                    dietary_info="",  # Optional: You can add dietary information if necessary
                    availability_dates="[]"  # Default to an empty list of available dates
                )
                # Add to the session
                db.session.add(new_item)
    
    # Commit the changes to the database
    db.session.commit()
    print("Menu items added successfully!")

with create_app().app_context():
    db.create_all()
    add_menu_items()