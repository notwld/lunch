from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request, render_template,redirect,flash,url_for
from app.models import db, Parent,Child
from flask_login import login_user,current_user,login_required

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/', methods=['GET'])
@login_required
def get_users():
    #list all childern of current user
    children = Child.query.filter_by(parent_id=current_user.id).all()
    
    
    return render_template('dashboard.html', current_user=current_user ,children=children)



@dashboard.route('/add-child', methods=['GET'])
@login_required
def add_child():
    return render_template('add_child.html')

@dashboard.route('/add-child', methods=['POST'])
@login_required
def add_child_post():
    data = request.form
    child = Child(
        first_name=data['first_name'],
        last_name=data['last_name'],
        state=data['state'],
        county=data['county'],
        school=data['school'],
        grade=data['grade'],
        allergies=data.get('allergies'),
        parent_id=current_user.id
    )
    db.session.add(child)
    db.session.commit()
    flash('Child added successfully')
    return redirect('/')

