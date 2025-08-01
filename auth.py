from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import User
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash('You do not have permission to create users.', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Get departments and locations for dropdowns
    from models import Department, Location, Employee
    departments = Department.query.filter_by(is_active=True).all()
    locations = Location.query.filter_by(is_active=True).all()
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        emp_id = request.form.get('emp_id')
        employee_name = request.form.get('employee_name')
        department_id = request.form.get('department_id')
        warehouse_id = request.form.get('warehouse_id')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        existing_emp = Employee.query.filter_by(emp_id=emp_id).first()
        
        if existing_user:
            flash('Username already exists.', 'error')
        elif existing_email:
            flash('Email already exists.', 'error')
        elif existing_emp:
            flash('Employee ID already exists.', 'error')
        else:
            # Create user account
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash(password),
                role=role
            )
            db.session.add(user)
            db.session.flush()  # Get the user ID
            
            # Create employee record
            employee = Employee(
                emp_id=emp_id,
                name=employee_name,
                department_id=int(department_id),
                warehouse_id=int(warehouse_id) if warehouse_id else None,
                user_id=user.id
            )
            db.session.add(employee)
            db.session.commit()
            
            flash('User and Employee record created successfully.', 'success')
            return redirect(url_for('main.dashboard'))
    
    # Get existing users for display
    existing_users = User.query.all()
    
    return render_template('create_user.html', 
                         departments=departments, 
                         locations=locations,
                         existing_users=existing_users)
