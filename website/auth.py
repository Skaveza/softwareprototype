from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash(f'Logged in successfully as {user.role}', 'success')
            if user.role == 'doctor':
                return redirect(url_for('views.doctor_dashboard'))
            elif user.role == 'admin':
                return redirect(url_for('views.admin_dashboard'))
            else:
                return redirect(url_for('views.home'))
        else:
            flash('Login unsuccessful. Check email and password.', 'error')
    
    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not email or not username or not password or not role:
            flash('Please fill out all fields.', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
        elif role not in ['doctor', 'admin']:
            flash('Invalid role selected.', 'error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(password, method='sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(f'Account created successfully as {role}!', 'success')
            if role == 'doctor':
                return redirect(url_for('views.doctor_dashboard'))
            elif role == 'admin':
                return redirect(url_for('views.admin_dashboard'))
    
    return render_template('signup.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
