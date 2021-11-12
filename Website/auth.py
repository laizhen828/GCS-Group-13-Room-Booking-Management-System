from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Credentials
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)



@auth.route('/login', methods=['GET', 'POST'])
def login():
    data = request.form
    print(data)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Credentials.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in Successful as ' + username, category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect Password.', category='error')
        else:
            flash('Username does not exist.', category='error')


    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    flash('Successfully logged out.',category='success')
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods = ['GET', 'POST'])
def sign_up():
    data = request.form
    current_username = current_user.username
    priv = current_user.priv
    print(data)
    if priv != "admin":
        flash('Permission Denied to view the page.', category='error')
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = Credentials.query.filter_by(username=username).first()
        useremail = Credentials.query.filter_by(email=email).first()
        if user:
            flash('Username already exist.', category='error')
        elif useremail:
            flash('Email already exist.', category='error')
        elif len(username) < 6:
            flash('Username must be greater than 5 characters.', category='error')
        elif len(name) < 1:
            flash('Username must be at least 1 character.', category='error')
        elif len(email) < 3:
            flash('Email must be at least 3 characters.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.",category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = Credentials(username=username, name=name, email=email, priv='student',password=generate_password_hash(password1,method='SHA256'))
            db.session.add(new_user)
            db.session.commit()
            #logout_user() not needed because is student, not admin
            flash('Registered Sucessfully!', category='success')
            return redirect(url_for('auth.sign_up'))
    return render_template("sign_up.html", user=current_user, username=current_username, priv=priv)