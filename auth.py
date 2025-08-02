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

    # Get employees without user accounts
    from models import Department, Location, Employee
    employees_without_users = Employee.query.filter_by(user_id=None, is_active=True).all()
    locations = Location.query.filter_by(is_active=True).all()

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        employee_id = request.form.get('employee_id')
        warehouse_id = request.form.get('warehouse_id')

        # Check for duplicates
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()

        if existing_user:
            flash('Username already exists.', 'error')
        elif existing_email:
            flash('Email already exists.', 'error')
        elif not employee_id:
            flash('Please select an employee.', 'error')
        else:
            # Get the selected employee
            employee = Employee.query.get(int(employee_id))
            if not employee:
                flash('Selected employee not found.', 'error')
            elif employee.user_id:
                flash('Selected employee already has a user account.', 'error')
            else:
                # Create user
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role
                )
                db.session.add(user)
                db.session.flush()  # Get the user ID

                # Link employee to user and update warehouse
                employee.user_id = user.id
                if warehouse_id:
                    employee.warehouse_id = int(warehouse_id)

                db.session.commit()

                flash(f'User account created and assigned to employee {employee.emp_id} - {employee.name}.', 'success')
                return redirect(url_for('main.dashboard'))

    # Get existing users for display
    existing_users = User.query.all()

    return render_template('create_user.html', 
                         employees=employees_without_users,
                         locations=locations,
                         existing_users=existing_users)