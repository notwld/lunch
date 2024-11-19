from flask import Blueprint, jsonify, request, render_template,redirect,flash,url_for
from app.models import db, Parent,Child
from flask_login import login_user,logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET'])
def login_form():
    return render_template('dashboard.html')

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.form
        email = data['email']
        password = data['password']
        

        parent = Parent.query.filter_by(email=email).first()

        if not parent or not parent.check_password(password):
            flash('Invalid email or password')
            return redirect('/')
        login_user(user=parent)

        return redirect('/')
    except KeyError as e:
        flash(f"Missing field: {str(e)}")
        return redirect('/')
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
        return redirect('/')
    
    
@auth.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/')

@auth.route('/register', methods=['GET'])
def register_form():
    return render_template('register.html')

@auth.route('/register', methods=['POST'])
def register():
    # Extract form data from the request
    data = request.form

    # Create a new Parent instance
    try:
        parent = Parent(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            address=data['address'],
            state=data['state'],
            city=data['city'],
            zip_code=data['zip_code'],
            home_phone=data.get('home_phone'),  # Optional field
            cell_phone=data['cell_phone'],  # Required field
            work_phone=data.get('work_phone')  # Optional field
        )

        # Set hashed password
        parent.set_password(data['password'])

        # Add the new parent to the database
        db.session.add(parent)
        db.session.commit()

        return redirect('/login')

    except KeyError as e:
        # Handle missing fields
        flash(f"Missing field: {str(e)}")
        return redirect('/register')
    except Exception as e:
        # Handle other errors
        flash(f"An error occurred: {str(e)}")
        return redirect('/register')

