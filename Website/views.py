from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Credentials, Bookings, Notifications, Rooms
from .auth import check_password_hash, generate_password_hash
import datetime
from datetime import datetime

views = Blueprint('views', __name__)

@views.route('/', methods = ['GET', 'POST'])
@login_required
def home():
    username = current_user.username
    priv = current_user.priv
    rooms = Rooms.query.all()
    date_confirmed = False
    time_slots = [9, 10, 11, 12, 13, 14, 15, 16, 17]
    if request.method == 'POST':
        room_type = request.form.get('room_type')
        date = request.form.get('date')
        time_slot = request.form.get('time_slot')
        confirmed_room_type = request.form.get('confirmed_room_type')
        confirmed_date = request.form.get('confirmed_date')
        submit = request.form.get('submit')

        check = Bookings.query.filter(Bookings.date==date,
                                      Bookings.room_type==room_type,
                                      Bookings.approve_status=='approved').all()

        for n in check:
            remove = ""
            for i in n.time_slot:
                if i == ":":
                    break
                else:
                    remove += i
            remove = int(remove)
            time_slots.remove(remove)

        date_confirmed = True
        if date_confirmed == True:
            if submit == "book":
                new_booking = Bookings(date=confirmed_date,
                                       time_slot=time_slot,
                                       approve_status='pending',
                                       booked_by=username,
                                       approved_declined_by='pending',
                                       room_type=confirmed_room_type
                                       )
                db.session.add(new_booking)
                db.session.commit()
                flash('Your booking is now pending for approval.', category='success')
                return redirect(url_for('views.home'))
            else:
                return render_template("home.html",
                                       user=current_user,
                                       username=username,
                                       priv=priv,
                                       rooms=rooms,
                                       date_confirmed=date_confirmed,
                                       confirmed_date=date,
                                       confirmed_room_type=room_type,
                                       time_slots=time_slots
                                       )
    return render_template("home.html",
                           user=current_user,
                           username=username,
                           priv=priv,
                           rooms=rooms,
                           date_confirmed=date_confirmed
                           )

@views.route('/room_management', methods = ['GET', 'POST'])
@login_required
def room_management():
    received = request.form
    print(received)
    username = current_user.username
    priv = current_user.priv
    data = Rooms.query.all()
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        abbr = request.form.get('abbr')
        quantity = request.form.get('quantity')
        room_name_check = Rooms.query.filter_by(room_type=room_name).first()
        abbr_check = Rooms.query.filter_by(abbr=abbr).first()
        if room_name_check:
            flash('Room name already exist.', category='error')
        if abbr_check:
            flash('Room Abbreviation already exist.', category='error')
        else:
            new_room = Rooms(room_type=room_name,abbr=abbr,quantity=quantity)
            db.session.add(new_room)
            db.session.commit()
            flash('New Room Added Successfully.', category='success')
            return redirect(url_for('views.room_management'))
    return render_template('room_management.html',
                           rooms=data,
                           user=current_user,
                           username=username,
                           priv=priv)

@views.route('/my_appointments', methods = ['GET', 'POST'])
@login_required
def my_appointments():
    data = Bookings.query.filter(Bookings.booked_by==current_user.username).all()
    return render_template('my_appointments.html',
                           appointments=reversed(data),
                           user=current_user,
                           username=current_user.username,
                           priv=current_user.priv)

@views.route('/manage_appointments', methods = ['GET', 'POST'])
@login_required
def manage_appointments():
    data = Bookings.query.all()
    return render_template('manage_appointments.html',
                           bookings=reversed(data),
                           user=current_user,
                           username=current_user.username,
                           priv=current_user.priv)

@views.route('/cancel/<int:num_log>', methods = ['GET', 'POST'])
@login_required
def cancel(num_log):
    clicked_booking = Bookings.query.filter_by(num_log=num_log).first()
    clicked_booking.approve_status = "canceled"
    db.session.commit()
    return redirect(url_for('views.my_appointments'))

@views.route('/approve/<int:num_log>', methods=['GET','POST'])
@login_required
def approve(num_log):
    clicked_booking = Bookings.query.filter_by(num_log=num_log).first()
    clicked_booking.approve_status = "approved"
    clicked_booking.approved_declined_by = current_user.username
    db.session.commit()
    message = "Appointment Number " + str(clicked_booking.num_log) + " has been approved."
    flash(message, category='success')
    return redirect(url_for('views.manage_appointments'))

@views.route('/decline/<int:num_log>', methods=['GET','POST'])
@login_required
def decline(num_log):
    clicked_booking = Bookings.query.filter_by(num_log=num_log).first()
    clicked_booking.approve_status = "declined"
    clicked_booking.approved_declined_by = current_user.username
    db.session.commit()
    message = "Appointment Number " + str(clicked_booking.num_log) + " has been declined."
    flash(message, category='success')
    return redirect(url_for('views.manage_appointments'))

@views.route('/modify_room/<int:id>', methods=['GET','POST'])
@login_required
def modify_room(id):
    clicked_room = Rooms.query.filter_by(id=id).first()
    if request.method == "POST":
        new_room_type = request.form.get('room_type')
        new_abbr = request.form.get('abbreviation')
        new_quantity = request.form.get('quantity')
        clicked_room.room_type = new_room_type
        clicked_room.abbr = new_abbr
        clicked_room.quantity = new_quantity
        db.session.commit()
        flash("All changes have been saved successfully.", category='success')
        return redirect(url_for('views.modify_room', id=id))
    return render_template('modify_room.html',
                           user=current_user,
                           username=current_user.username,
                           priv=current_user.priv,
                           data=clicked_room)

@views.route('/delete_room/<int:id>', methods=['GET','POST'])
@login_required
def delete_room(id):
    clicked_room = Rooms.query.filter_by(id=id).first()
    db.session.delete(clicked_room)
    db.session.commit()
    message = clicked_room.room_type + " has been deleted successfully."
    flash(message, category='success')
    return redirect(url_for('views.room_management'))


@views.route('/account_settings', methods = ['GET', 'POST'])
@login_required
def account_settings():
    username = current_user.username
    name = current_user.name
    email = current_user.email
    password = current_user.password
    return render_template('account_settings.html', user=current_user, username=username, name=name, email=email, password=password, priv=current_user.priv)

@views.route('/change_password', methods = ['GET', 'POST'])
@login_required
def change_password():
    username = current_user.username
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')
        userpasswordhash = current_user.password
        if not check_password_hash(userpasswordhash, current_password):
            flash('Password Incorrect',category='error')
        elif len(new_password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif new_password1 != new_password2:
            flash("New passwords don't match.",category='error')
        else:
            current_user.password = generate_password_hash(new_password1,method='SHA256')
            db.session.commit()
            flash("Successfully changed password.",category='success')
            return redirect(url_for('views.account_settings'))
    return render_template('change_password.html', user=current_user, username=username)

