from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask import Blueprint, jsonify, request, render_template
from app.models import db, Parent,Child

api_bp = Blueprint('dashboard', __name__)

@api_bp.route('/', methods=['GET'])
def get_users():
    return render_template('dashboard.html')

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    print(data)

    parent = Parent(
        email=data['parent[user_attributes][email]'],
        first_name=data['parent[first_name]'],
        last_name=data['parent[last_name]'],
        address=data['parent[address_attributes][address_line]'],
        state=data['parent[address_attributes][state]'],
        city=data['parent[city]'],
        zip_code=data['parent[zip]'],
        home_phone=data['parent[home_phone]'],
        cell_phone=data['parent[cell_phone]'],
        work_phone=data['parent[work_phone]']
    )
    parent.set_password(data['parent[user_attributes][password]'])
    db.session.add(parent)
    db.session.commit()

    return jsonify(data)

@api_bp.route('/get/<int:id>', methods=['GET'])
def get_user(id):
    parent = Parent.query.get(id)
    children = Child.query.filter_by(parent_id=id).all()
    return jsonify({
        "email": parent.email,
        "first_name": parent.first_name,
        "last_name": parent.last_name,
        "address": parent.address,
        "state": parent.state,
        "city": parent.city,
        "zip_code": parent.zip_code,
        "home_phone": parent.home_phone,
        "cell_phone": parent.cell_phone,
        "work_phone": parent.work_phone,
        "children": [{
            "first_name": child.first_name,
            "last_name": child.last_name,
            "state": child.state,
            "county": child.county,
            "school": child.school,
            "grade": child.grade,
            "allergies": child.allergies
        } for child in children]
    })


@api_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():

    return jsonify({"message": "Successfully logged out"}), 200


@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    parent = Parent.query.filter_by(email=email).first()

    if not parent or not parent.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    # Create a token
    access_token = create_access_token(identity=parent.id)
    return jsonify({"access_token": access_token, "parent":{
        'id': parent.id,
        "email": parent.email,
        "first_name": parent.first_name,
        "last_name": parent.last_name,
        "address": parent.address,
        "state": parent.state,
        "city": parent.city,
        "zip_code": parent.zip_code,
        "home_phone": parent.home_phone,
        "cell_phone": parent.cell_phone,
        "work_phone": parent.work_phone
    }}), 200

@api_bp.route('/add-child', methods=['GET'])
def add_child():
    return render_template('add_child.html')

@api_bp.route('/add-child', methods=['POST'])
@jwt_required()
def add_child_post():
    parent_id = get_jwt_identity()
    parent = Parent.query.get(parent_id)

    data = request.json

    child = Child(
        first_name=data['first_name'],
        last_name=data['last_name'],
        state=data['state'],
        county=data['county'],
        school=data['school'],
        grade=data['grade'],
        allergies=data['allergies'],
        parent_id=parent.id
    )

    db.session.add(child)
    db.session.commit()

    return jsonify(data)

@api_bp.route('/get-children', methods=['GET'])
def get_children():
    children = Child.query.all()
    return jsonify([{
        "first_name": child.first_name,
        "last_name": child.last_name,
        "state": child.state,
        "county": child.county,
        "school": child.school,
        "grade": child.grade,
        "allergies": child.allergies,
        "parent_id": child.parent_id
    } for child in children])
