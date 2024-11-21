from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db,Child,Order,OrderItem,Parent,School,MenuItem,Coupons

admin = Blueprint('admin', __name__)

@admin.route('/admin-dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    orders = Order.query.filter_by(status='Paid').all()
    total_revenue = sum(order.total_cost for order in orders)
    return render_template('admin_dashboard.html', orders=orders ,total_revenue=total_revenue)

@admin.route('/customers', methods=['GET'])
@login_required
def customers():
    parents = Parent.query.options(db.joinedload(Parent.children)).all()
    return render_template('customers.html' ,parents=parents)

@admin.route('/childern/<int:id>', methods=['GET'])
@login_required
def childern(id):
    parent = Parent.query.get(id)
    childern = Child.query.filter_by(parent_id=id).all()
    return render_template('childern.html', children=childern, parent=parent)

@admin.route('/delete-parent/<int:id>', methods=['DELETE'])
@login_required
def delete_parent(id):
    parent = Parent.query.get(id)
    if not parent:
        return jsonify({"error": "Parent not found"}), 404
    db.session.delete(parent)
    db.session.commit()
    return jsonify({"message": "Parent deleted successfully"})

@admin.route('/edit-parent/<int:id>', methods=['GET'])
@login_required
def edit_parent(id):
    parent = Parent.query.get(id)
    return render_template('edit_parent.html', user=parent)

@admin.route('/edit-parent/<int:id>', methods=['POST'])
@login_required
def edit_parent_post(id):
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
    schools = School.query.all()
    return render_template('schools.html', schools=schools)

@admin.route('/add-school', methods=['GET'])
@login_required
def add_school():
    return render_template('add_school.html')

@admin.route('/add-school', methods=['POST'])
@login_required
def add_school_post():
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
    school = School.query.get(id)
    return render_template('edit_school.html', school=school)

@admin.route('/edit-school/<int:id>', methods=['POST'])
@login_required
def edit_school_post(id):
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
    school = School.query.get(id)
    db.session.delete(school)
    db.session.commit()
    flash('School deleted successfully')
    return redirect('/schools')


@admin.route('/view-menus', methods=['GET'])
@login_required
def view_menus():
    menus = MenuItem.query.all()
    return render_template('menu.html' ,menus=menus)

@admin.route('/add-menu', methods=['GET'])
@login_required
def add_menu():
    return render_template('add-menu-item.html')

@admin.route('/add-menu', methods=['POST'])
@login_required
def add_menu_post():
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
    menu = MenuItem.query.get(id)
    return render_template('edit-menu-item.html', menu=menu)

@admin.route('/edit-menu/<int:id>', methods=['POST'])
@login_required
def edit_menu_post(id):
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
    menu = MenuItem.query.get(id)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu item deleted successfully')
    return redirect('/view-menus')

@admin.route('/coupons', methods=['GET'])
@login_required
def coupons():
    coupons = Coupons.query.all()
    return render_template('coupons.html', coupons=coupons)

@admin.route('/add-coupon', methods=['GET'])
@login_required
def add_coupon_page():
    return render_template('add-coupon.html')

@admin.route('/save_coupon', methods=['POST'])
@login_required
def add_coupon():
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
    coupon = Coupons.query.get(id)
    db.session.delete(coupon)
    db.session.commit()
    flash('Coupon deleted successfully')
    return redirect('/coupons')

@admin.route('/edit-coupon/<int:id>', methods=['GET'])
@login_required
def edit_coupon(id):
    coupon = Coupons.query.get(id)
    return render_template('edit-coupon.html', coupon=coupon)

@admin.route('/edit-coupon/<int:id>', methods=['POST'])
@login_required
def edit_coupon_post(id):
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


