from flask import Blueprint, render_template, request, jsonify,flash,redirect
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import db,Child,Order,OrderItem,Parent,School

admin = Blueprint('admin', __name__)

@admin.route('/admin-dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    orders = Order.query.all()
    return render_template('admin_dashboard.html', orders=orders)

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
    orders = Order.query.all()
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
    return render_template('menu.html')

@admin.route('/add-menu', methods=['GET'])
@login_required
def add_menu():
    return render_template('add-menu-item.html')
