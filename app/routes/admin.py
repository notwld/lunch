from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db,Child,Order,OrderItem,Parent,School,MenuItem,Coupons

admin = Blueprint('admin', __name__)

@admin.route('/admin-dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    # Total Revenue
    if not current_user.is_admin:
        return redirect('/')
    total_revenue = db.session.query(db.func.sum(Order.total_cost)).scalar() or 0

    # Top Paying Parents
    top_parents = (
        db.session.query(
            Parent.id,
            Parent.first_name,
            Parent.last_name,
            db.func.sum(Order.total_cost).label('total_spent')
        )
        .join(Order, Parent.id == Order.parent_id)
        .group_by(Parent.id)
        .order_by(db.desc('total_spent'))
        .limit(5)
        .all()
    )
    top_parents_data = [
        {"name": f"{p.first_name} {p.last_name}", "total_spent": round(p.total_spent, 2)}
        for p in top_parents
    ]

    # Top Selling Meals
    top_meals = (
        db.session.query(
            OrderItem.entree_name,
            db.func.count(OrderItem.id).label('order_count')
        )
        .group_by(OrderItem.entree_name)
        .order_by(db.desc('order_count'))
        .limit(5)
        .all()
    )
    top_meals_data = [{"name": meal.entree_name, "order_count": meal.order_count} for meal in top_meals]
    revenue_by_month = (
        db.session.query(
            db.func.strftime('%Y-%m', Order.order_date).label('month'),  # For SQLite
            db.func.sum(Order.total_cost).label('total_revenue')
        )
        .group_by('month')
        .order_by('month')
        .all()
    )
    revenue_data = [
        {
            "month": datetime.strptime(r.month, '%Y-%m').strftime('%b-%Y'),
            "total_revenue": round(r.total_revenue, 2)
        }
        for r in revenue_by_month
    ]
    # Render Template with Metrics
    # 5 recent orders
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    return render_template(
        'admin_dashboard.html',
        total_revenue=round(total_revenue, 2),
        top_parents=top_parents_data,
        top_meals=top_meals_data,
        current_user=current_user,
        revenue_data=revenue_data,
        recent_orders=recent_orders
    )

@admin.route('/customers', methods=['GET'])
@login_required
def customers():
    parents = Parent.query.options(db.joinedload(Parent.children)).all()
    if not current_user.is_admin:
        return redirect('/')
    return render_template('customers.html' ,parents=parents)

@admin.route('/childern/<int:id>', methods=['GET'])
@login_required
def childern(id):
    parent = Parent.query.get(id)
    childern = Child.query.filter_by(parent_id=id).all()
    if not current_user.is_admin:
        return redirect('/')
    return render_template('childern.html', children=childern, parent=parent)

@admin.route('/delete-parent/<int:id>', methods=['DELETE'])
@login_required
def delete_parent(id):
    if not current_user.is_admin:
        return redirect('/')
    parent = Parent.query.get(id)
    if not parent:
        return jsonify({"error": "Parent not found"}), 404
    db.session.delete(parent)
    db.session.commit()
    return jsonify({"message": "Parent deleted successfully"})

@admin.route('/edit-parent/<int:id>', methods=['GET'])
@login_required
def edit_parent(id):
    if not current_user.is_admin:
        return redirect('/')
    parent = Parent.query.get(id)
    return render_template('edit_parent.html', user=parent)

@admin.route('/edit-parent/<int:id>', methods=['POST'])
@login_required
def edit_parent_post(id):
    if not current_user.is_admin:
        return redirect('/')
    data = request.form
    parent = Parent.query.get(id)
    parent.first_name = data['first_name']
    parent.last_name = data['last_name']
    parent.address = data['address']
    parent.state = data['state']
    parent.city = data['city']
    parent.zip_code = data['zip_code']
    parent.home_phone = data['home_phone']
    parent.cell_phone = data['cell_phone']
    parent.work_phone = data['work_phone']
    db.session.commit()
    flash('Parent updated successfully')
    return redirect('/customers')


@admin.route('/all-orders', methods=['GET'])
@login_required
def all_orders():
    if not current_user.is_admin:
        return redirect('/')
    # Get filter parameters from the request
    status_filter = request.args.get('status')
    date_filter = request.args.get('date')
    email_filter = request.args.get('email')

    # Build the query with the necessary filters
    query = Order.query

    if status_filter:
        query = query.filter(Order.status == status_filter)
    if date_filter:
        query = query.filter(Order.order_date == date_filter)
    if email_filter:
        query = query.filter(Order.parent.email == email_filter)

    orders = query.all()
    return render_template('all_orders.html', orders=orders)

@admin.route('/schools', methods=['GET'])
@login_required
def schools():
    if not current_user.is_admin:
        return redirect('/')
    schools = School.query.all()
    return render_template('schools.html', schools=schools)

@admin.route('/add-school', methods=['GET'])
@login_required
def add_school():
    if not current_user.is_admin:
        return redirect('/')
    return render_template('add_school.html')

@admin.route('/add-school', methods=['POST'])
@login_required
def add_school_post():
    if not current_user.is_admin:
        return redirect('/')
    name = request.form.get('school_name')
    address = request.form.get('address')
    phone_number = request.form.get('phone_number')
    contact_name = request.form.get('contact_name')
    contact_email = request.form.get('contact_email')
    special_instructions = request.form.get('special_instructions', '')

    # Validate required fields
    if not name or not address or not phone_number or not contact_name or not contact_email:
        flash("All fields except special instructions are required", "error")
        return redirect('/add-school')  # Redirect back to the form page

    # Check if a school with the same name already exists
    existing_school = School.query.filter_by(name=name).first()
    if existing_school:
        flash("A school with this name already exists", "error")
        return redirect('/add-school')

    try:
        # Create a new school entry
        new_school = School(
            name=name,
            address=address,
            phone_number=phone_number,
            contact_name=contact_name,
            contact_email=contact_email,
            special_instructions=special_instructions,
            total_students=0
        )

        # Add and commit the new school to the database
        db.session.add(new_school)
        db.session.commit()

        flash("School added successfully", "success")
        return redirect('/schools')  # Redirect to the list of schools

    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while adding the school: {str(e)}", "error")
        return redirect('/add-school')

@admin.route('/edit-school/<int:id>', methods=['GET'])
@login_required
def edit_school(id):
    if not current_user.is_admin:
        return redirect('/')
    school = School.query.get(id)
    return render_template('edit_school.html', school=school)

@admin.route('/edit-school/<int:id>', methods=['POST'])
@login_required
def edit_school_post(id):
    if not current_user.is_admin:
        return redirect('/')
    school = School.query.get(id)
    data = request.form

    school.name = data['school_name']
    school.address = data['address']
    school.phone_number = data['phone_number']
    school.contact_name = data['contact_name']
    school.contact_email = data['contact_email']
    school.special_instructions = data['special_instructions']

    db.session.commit()
    flash('School updated successfully')
    return redirect('/schools')

@admin.route('/delete-school/<int:id>', methods=['DELETE'])
@login_required
def delete_school(id):
    if not current_user.is_admin:
        return redirect('/')
    school = School.query.get(id)
    db.session.delete(school)
    db.session.commit()
    flash('School deleted successfully')
    return redirect('/schools')


@admin.route('/view-menus', methods=['GET'])
@login_required
def view_menus():
    menus = MenuItem.query.all()
    return render_template('menu.html' ,menus=menus,current_user=current_user)

@admin.route('/add-menu', methods=['GET'])
@login_required
def add_menu():
    if not current_user.is_admin:
        return redirect('/')
    return render_template('add-menu-item.html')

@admin.route('/add-menu', methods=['POST'])
@login_required
def add_menu_post():
    if not current_user.is_admin:
        return redirect('/')
    data = request.form
    if not data['name'] or not data['price'] or not data['type'] or not data['cautions'] or not data['description']:
        flash('All fields are required')
        return redirect('/add-menu')
    menu_item = MenuItem(
        name=data['name'],
        price=data['price'],
        type=data['type'],
        cautions=data['cautions'],
        description=data['description'],
        img_url=data['img_url'] or ""
    )
    db.session.add(menu_item)
    db.session.commit()
    flash('Menu item added successfully')
    return redirect('/view-menus')


@admin.route('/edit-menu/<int:id>', methods=['GET'])
@login_required
def edit_menu(id):
    if not current_user.is_admin:
        return redirect('/')
    menu = MenuItem.query.get(id)
    return render_template('edit-menu-item.html', menu=menu)

@admin.route('/edit-menu/<int:id>', methods=['POST'])
@login_required
def edit_menu_post(id):
    if not current_user.is_admin:
        return redirect('/')
    data = request.form
    menu = MenuItem.query.get(id)
    menu.name = data['name']
    menu.price = data['price']
    menu.type = data['type']
    menu.cautions = data['cautions']
    menu.description = data['description']
    menu.img_url = data['img_url']
    db.session.commit()
    flash('Menu item updated successfully')
    return redirect('/view-menus')

@admin.route('/delete-menu/<int:id>', methods=['DELETE'])
@login_required
def delete_menu(id):
    if not current_user.is_admin:
        return redirect('/')
    menu = MenuItem.query.get(id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu item deleted successfully')
    return redirect('/view-menus')

@admin.route('/coupons', methods=['GET'])
@login_required
def coupons():
    if not current_user.is_admin:
        return redirect('/')
    coupons = Coupons.query.all()
    return render_template('coupons.html', coupons=coupons)

@admin.route('/add-coupon', methods=['GET'])
@login_required
def add_coupon_page():
    if not current_user.is_admin:
        return redirect('/')
    return render_template('add-coupon.html')

@admin.route('/save_coupon', methods=['POST'])
@login_required
def add_coupon():
    if not current_user.is_admin:
        return redirect('/')
    data = request.form
    coupon = Coupons(
        code=data['code'],
        discount=data['discount'],
expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%dT%H:%M'),
        status=data.get('status', 'Active')    )
    db.session.add(coupon)
    db.session.commit()
    flash('Coupon added successfully')
    return redirect('/coupons')

@admin.route('/delete-coupon/<int:id>', methods=['DELETE'])
@login_required
def delete_coupon(id):
    if not current_user.is_admin:
        return redirect('/')
    coupon = Coupons.query.get(id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Coupon deleted successfully')
    return redirect('/coupons')

@admin.route('/edit-coupon/<int:id>', methods=['GET'])
@login_required
def edit_coupon(id):
    if not current_user.is_admin:
        return redirect('/')
    coupon = Coupons.query.get(id)
    return render_template('edit-coupon.html', coupon=coupon)

@admin.route('/edit-coupon/<int:id>', methods=['POST'])
@login_required
def edit_coupon_post(id):
    if not current_user.is_admin:
        return redirect('/')
    data = request.form
    coupon = Coupons.query.get(id)
    coupon.code = data['code']
    coupon.discount = data['discount']
    coupon.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%dT%H:%M')
    coupon.status = data.get('status', 'Active')

    db.session.commit()
    flash('Coupon updated successfully')
    return redirect('/coupons')

# validate coupon
@admin.route('/validate-coupon', methods=['POST'])
@login_required
def validate_coupon():
    data = request.json
    coupon = Coupons.query.filter_by(code=data['code']).first()
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404
    now_date = datetime.strptime(str(date.today()), '%Y-%m-%d')
    if coupon.expiration_date < now_date:
        return jsonify({"error": "Coupon has expired"}), 400
    return jsonify({"discount": coupon.discount})


