from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request, render_template,redirect,flash,url_for
from app.models import db, Parent,Child,Order,School
from flask_login import login_user,current_user,login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET'])
@login_required
def get_users():
    #list all childern of current user
    children = Child.query.filter_by(parent_id=current_user.id).all()
    orders = Order.query.filter_by(parent_id=current_user.id).all()
    
    
    return render_template('dashboard.html', current_user=current_user ,children=children ,orders=orders)



@dashboard.route('/add-child', methods=['GET'])
@login_required
def add_child():
    schools = School.query.all()
    return render_template('add_child.html', schools=schools)

@dashboard.route('/add-child', methods=['POST'])
@login_required
def add_child_post():
    data = request.form
    child = Child(
        first_name=data['first_name'],
        last_name=data['last_name'],
        state=data['state'],
        county=data['county'],
        grade=data['grade'],
        allergies=data.get('allergies'),
        parent_id=current_user.id,
        school_id=data['school_id']
    )
    db.session.add(child)
    db.session.commit()
    flash('Child added successfully')
    return redirect('/')
@dashboard.route('/edit-profile', methods=['GET'])
@login_required
def edit_profile():
    return render_template('edit_profile.html', user=current_user)

@dashboard.route('/edit-profile', methods=['POST'])
@login_required
def edit_profile_post():
    data = request.form
    current_user.first_name = data['first_name']
    current_user.last_name = data['last_name']
    current_user.address = data['address']
    current_user.state = data['state']
    current_user.city = data['city']
    current_user.zip_code = data['zip_code']
    current_user.home_phone = data['home_phone']
    current_user.cell_phone = data['cell_phone']
    current_user.work_phone = data['work_phone']
    db.session.commit()
    flash('Profile updated successfully')
    return redirect('/')

@dashboard.route('/delete-child/<int:id>', methods=['DELETE'])
@login_required
def delete_child(id):
    child = Child.query.get(id)
    db.session.delete(child)
    db.session.commit()
    flash('Child deleted successfully')
    return redirect('/')

@dashboard.route('/edit-child/<int:id>', methods=['GET'])
@login_required
def edit_child(id):
    child = Child.query.get(id)
    schools = School.query.all()
    return render_template('edit_child.html', child=child, schools=schools)

@dashboard.route('/edit-child/<int:id>', methods=['POST'])
@login_required
def edit_child_post(id):
    data = request.form
    child = Child.query.get(id)
    child.first_name = data['first_name']
    child.last_name = data['last_name']
    child.state = data['state']
    child.county = data['county']
    child.school_id = data['school_id']
    child.grade = data['grade']
    child.allergies = data.get('allergies')
    db.session.commit()
    flash('Child updated successfully')
    return redirect('/')


