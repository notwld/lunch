from app.models import db, MenuItem,Parent,School
from app import create_app
# Define the menu items
menu_items = [
    # Entrees
    {
        "name": "Buttered Noodles V",
        "price": 3.5,
        "type": "entrees",
        "description": "Delicious noodles tossed with creamy butter and herbs.",
        "img_url": "https://example.com/images/buttered_noodles.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Pasta Primavera",
        "price": 4.0,
        "type": "entrees",
        "description": "Pasta with a medley of fresh seasonal vegetables.",
        "img_url": "https://example.com/images/pasta_primavera.jpg",
        "cautions": "Contains gluten.",
    },
    {
        "name": "Grilled Chicken Plate",
        "price": 5.0,
        "type": "entrees",
        "description": "Juicy grilled chicken served with a side of rice.",
        "img_url": "https://example.com/images/grilled_chicken.jpg",
        "cautions": "None.",
    },
    {
        "name": "Vegetarian Lasagna",
        "price": 5.5,
        "type": "entrees",
        "description": "Layered pasta with ricotta, spinach, and marinara.",
        "img_url": "https://example.com/images/vegetarian_lasagna.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Salmon Teriyaki Bowl",
        "price": 6.0,
        "type": "entrees",
        "description": "Grilled salmon with teriyaki sauce on steamed rice.",
        "img_url": "https://example.com/images/salmon_teriyaki.jpg",
        "cautions": "Contains soy.",
    },

    # Sides
    {
        "name": "All Beef Meatballs",
        "price": 2.0,
        "type": "sides",
        "description": "Juicy beef meatballs served with marinara sauce.",
        "img_url": "https://example.com/images/beef_meatballs.jpg",
        "cautions": "Contains soy.",
    },
    {
        "name": "Grilled Veggies",
        "price": 2.5,
        "type": "sides",
        "description": "A mix of zucchini, bell peppers, and carrots.",
        "img_url": "https://example.com/images/grilled_veggies.jpg",
        "cautions": "None.",
    },
    {
        "name": "Garlic Bread",
        "price": 1.5,
        "type": "sides",
        "description": "Crispy bread topped with garlic butter.",
        "img_url": "https://example.com/images/garlic_bread.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "French Fries",
        "price": 2.0,
        "type": "sides",
        "description": "Golden and crispy potato fries.",
        "img_url": "https://example.com/images/french_fries.jpg",
        "cautions": "None.",
    },
    {
        "name": "Mashed Potatoes",
        "price": 2.0,
        "type": "sides",
        "description": "Creamy mashed potatoes with butter.",
        "img_url": "https://example.com/images/mashed_potatoes.jpg",
        "cautions": "Contains dairy.",
    },

    # Produce
    {
        "name": "Locally Grown Apple Slices",
        "price": 1.0,
        "type": "produce",
        "description": "Fresh and crisp apple slices from local farms.",
        "img_url": "https://example.com/images/apple_slices.jpg",
        "cautions": "None.",
    },
    {
        "name": "Carrot Sticks",
        "price": 1.2,
        "type": "produce",
        "description": "Crunchy and fresh carrot sticks.",
        "img_url": "https://example.com/images/carrot_sticks.jpg",
        "cautions": "None.",
    },
    {
        "name": "Cucumber Slices",
        "price": 1.0,
        "type": "produce",
        "description": "Cool and refreshing cucumber slices.",
        "img_url": "https://example.com/images/cucumber_slices.jpg",
        "cautions": "None.",
    },
    {
        "name": "Grapes",
        "price": 1.5,
        "type": "produce",
        "description": "A bunch of sweet, seedless grapes.",
        "img_url": "https://example.com/images/grapes.jpg",
        "cautions": "None.",
    },
    {
        "name": "Cherry Tomatoes",
        "price": 1.5,
        "type": "produce",
        "description": "Sweet and juicy cherry tomatoes.",
        "img_url": "https://example.com/images/cherry_tomatoes.jpg",
        "cautions": "None.",
    },

    # Desserts
    {
        "name": "Sugar Cookie",
        "price": 1.5,
        "type": "desserts",
        "description": "Soft and sweet sugar cookie.",
        "img_url": "https://example.com/images/sugar_cookie.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Brownie",
        "price": 2.0,
        "type": "desserts",
        "description": "Rich and chocolaty brownie.",
        "img_url": "https://example.com/images/brownie.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Cheesecake Slice",
        "price": 2.5,
        "type": "desserts",
        "description": "Creamy cheesecake with a graham cracker crust.",
        "img_url": "https://example.com/images/cheesecake.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Fruit Tart",
        "price": 2.8,
        "type": "desserts",
        "description": "Tart crust filled with custard and topped with fruit.",
        "img_url": "https://example.com/images/fruit_tart.jpg",
        "cautions": "Contains gluten and dairy.",
    },
    {
        "name": "Ice Cream Cup",
        "price": 2.0,
        "type": "desserts",
        "description": "Creamy vanilla ice cream in a cup.",
        "img_url": "https://example.com/images/ice_cream.jpg",
        "cautions": "Contains dairy.",
    },

    # Drinks
    {
        "name": "No Drink",
        "price": 0.0,
        "type": "drinks",
        "description": "No drink selected.",
        "img_url": None,
        "cautions": None,
    },
    {
        "name": "No Entree",
        "price": 0.0,
        "type": "entrees",
        "description": "No entree selected.",
        "img_url": None,
        "cautions": None,
    },
    {
        "name": "No Desserts",
        "price": 0.0,
        "type": "desserts",
        "description": "No dessert selected.",
        "img_url": None,
        "cautions": None,
    },
    {
        "name": "No Produce",
        "price": 0.0,
        "type": "produce",
        "description": "No Produce selected.",
        "img_url": None,
        "cautions": None,
    },
    {
        "name": "No Sides",
        "price": 0.0,
        "type": "sides",
        "description": "No side selected.",
        "img_url": None,
        "cautions": None,
    },
    {
        "name": "Orange Juice",
        "price": 1.5,
        "type": "drinks",
        "description": "Freshly squeezed orange juice.",
        "img_url": "https://example.com/images/orange_juice.jpg",
        "cautions": "None.",
    },
    {
        "name": "Bottled Water",
        "price": 1.0,
        "type": "drinks",
        "description": "Cool and refreshing bottled water.",
        "img_url": "https://example.com/images/water.jpg",
        "cautions": "None.",
    },
    {
        "name": "Cola",
        "price": 1.5,
        "type": "drinks",
        "description": "Classic cola soda.",
        "img_url": "https://example.com/images/cola.jpg",
        "cautions": "Contains caffeine.",
    },
    {
        "name": "Iced Tea",
        "price": 1.5,
        "type": "drinks",
        "description": "Sweetened iced tea.",
        "img_url": "https://example.com/images/iced_tea.jpg",
        "cautions": "Contains caffeine.",
    },
]

def seed_menu_items():
    """Seed the database with menu items."""
    with create_app().app_context():
        db.create_all()

        parent = Parent(
            email="admin@admin.com",
            first_name="Admin",
            last_name="Admin",
            address="123 Admin St",
            state="CA",
            city="Adminville",
            zip_code="12345",
            home_phone="123-456-7890",
            cell_phone="123-456-7890",
            work_phone="123-456-7890",
            is_admin=True,
        )
        parent.set_password("admin")
        db.session.add(parent)
        db.session.commit()
        school = School(
            name="Test School",
            address="123 School St",
            phone_number="123-456-7890",
            contact_name="Principal Test",
            contact_email="principal@gmail.com",
            special_instructions="None",
        )
        db.session.add(school)
        db.session.commit()
        for item in menu_items:
            # Check if item already exists
            existing_item = MenuItem.query.filter_by(name=item["name"]).first()
            if existing_item:
                print(f"Skipping {item['name']}, already exists.")
                continue

            # Add new item
            new_item = MenuItem(
                name=item["name"],
                price=item["price"],
                type=item["type"],
                description=item["description"],
                img_url=item["img_url"],
                cautions=item["cautions"],
            )
            db.session.add(new_item)
            print(f"Added {item['name']} to the database.")

        # Commit changes
        db.session.commit()
        print("Database seeding complete.")

if __name__ == "__main__":
    seed_menu_items()