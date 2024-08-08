import os
import subprocess

from flask import Flask, render_template, request, redirect, session
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.sql.functions import user

import database
import models
from models import Reservation, FitnessCenter, Trainer, Service, Review
from send_mail import send_mail
from utils import SQLiteDatabase, check_credentials, calc_slots

app = Flask(__name__)
app.secret_key = b'_343435#y2L"F4Q8z\n\xec]/'


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        results = func(*args, **kwargs)
        return results

    return wrapper






@app.route("/", methods=["GET", "POST"])
def index():
    #send_mail('vasylenkodmytrii@gmail.com', 'sudo', 'some text')
    return render_template("index.html",)



@app.route('/register', methods=['GET', 'POST'])
def get_register():
    if request.method == 'POST':
            form_data = request.form
            database.init_db()
            user1 = models.User(login=form_data['login'],
                                password=form_data['password'],
                                birth_date=form_data['birth_date'],
                                phone=form_data['phone']
                                )
            database.db_session.add(user1)
            database.db_session.commit()
            user1.add_funds(10)
            database.db_session.add(user1)
            database.db_session.commit()

            return "User registered"
    else:
        return render_template('register.html')




@login_required
@app.route('/user', methods=['GET', "POST"])
def get_users():
    if "user_id" not in session:
        return redirect('/login')
    if request.method == 'POST':
        form_data = request.form
        database.init_db()
        user1 = models.User(login=form_data['login'],
                            password=form_data['password'],
                            birth_date=form_data['birth_date'],
                            phone=form_data['phone'])
        database.db_session.add(user1)
        database.db_session.commit()

    return render_template('user_dashboard.html')
# не відображаються тренери з бд

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_details(user_id):
    database.init_db()
    if request.method == 'POST':
        form_data = request.form
        user = database.db_session.query(models.User).filter_by(id=user_id).first()
        if user:
            user.login = form_data['login']
            user.password = form_data['password']
            user.birth_date = form_data['birth_date']
            user.phone = form_data['phone']
            database.db_session.commit()
        return redirect(f'/user/{user_id}')
    user = database.db_session.query(models.User).filter_by(id=user_id).first()
    return render_template('user_detail.html', user=user)


@login_required
@app.route('/user/reservation', methods=['GET', 'POST'])
def user_reservations():
    if request.method == 'GET':
        user_id = session.get('user_id')
        if not user_id:
            return redirect('/login')

        reservations = database.db_session.query(Reservation).filter_by(user_id=user_id).all()

        return render_template('reservations.html', user_reservations=reservations)

    elif request.method == 'POST':
        form_dict = request.form
        service_id = form_dict['service_id']
        trainer_id = form_dict['trainer_id']
        slot_id = form_dict['slot_id']
        result: calc_slots(service_id, trainer_id, slot_id)
        send_mail.delay('vasylenkodmytrii@gmail.com', 'Confirmation reservation', 'Your reservation has been created')

        return "create user reservation"











@app.route('/user/reservations/<int:reservation_id>', methods=['GET', 'POST'])
def user_reservation(reservation_id):
    if request.method == 'POST':
        new_date = request.form.get('new_date')
        new_time = request.form.get('new_time')

        if not new_date or not new_time:
            return 'New date and time are required'

        try:
            reservation = database.db_session.query(Reservation).filter_by(id=reservation_id).first()
            if reservation:
                reservation.date = new_date
                reservation.time = new_time
                database.db_session.commit()
            else:
                return 'Reservation not found', 404
        except IntegrityError:
            database.db_session.rollback()
            return 'Error updating reservation', 500

        return redirect(('user_reservation'))

    reservation = database.db_session.query(Reservation).filter_by(id=reservation_id).first()

    return render_template('reservation_detail.html', reservation=reservation)

@login_required
@app.route('/user/reservations/<reservation_id>/delete', methods=['POST'])
def delete_reservation(reservation_id):
    query = 'DELETE FROM reservations WHERE id=?'
    with SQLiteDatabase('db.db') as db:
        db.execute_query(query, (reservation_id,))
    return redirect('user_reservations')


@app.route('/login', methods=['GET', 'POST'])
def get_login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = check_credentials(login, password)
        if user:
            session['user_id'] = user.id
            return redirect('/user')
        else:
            return 'Invalid login or password'

    return render_template('login.html')


@login_required
@app.route('/logout', methods=['GET'])
def logout():
    session.pop("user_id", None)
    return redirect('/login')

@login_required
@app.route('/select_trainer_service', methods=['GET', 'POST'])
def select_trainer_service():
    if request.method == 'POST':
        trainer_id = request.form['trainer']
        service_id = request.form['service']
        desired_date = request.form['date']

        return redirect('/choose_trainer_date', 'trainer_id=trainer_id', 'service_id=service_id', 'desired_date=desired_date')
#отримуємо списки тренерів
    trainers = database.db_session.query(Trainer).all()
    services = database.db_session.query(Service).all()
    return render_template('select_trainer_service.html', trainer=trainers, service=services)


@app.route('/choose_service_date', methods=['POST'])
def choose_service_date():
    trainer_id = request.form['trainer'],
    service_id = request.form['service'],
    desired_date = request.form['date']
    time_slots = calc_slots(trainer_id, service_id, desired_date)
    return render_template('pre_reservation.html', form_info={
        "trainer": trainer_id,
        "service": service_id,
        "desired_date": desired_date,
        "time_slots": time_slots
    })

@login_required
@app.route('/choose_trainer_date', methods=['POST'])
def choose_trainer_date():
    trainer_id = request.form['trainer']
    service_id = request.form['service']
    desired_date = request.form['date']

    time_slots = calc_slots(trainer_id, service_id, desired_date)

    return render_template('pre_reservation.html', form_info={
        "trainer": trainer_id,
        "service": service_id,
        "desired_date": desired_date,
        "time_slots": time_slots
    })

@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    trainer_id = request.form['trainer']
    service_id = request.form['service']
    desired_date = request.form['desired_date']
    selected_time = request.form['time']

    with SQLiteDatabase('db.db') as db:
        db.execute_query('INSERT INTO reservation (trainer_id, service_id, date, time, user_id) VALUES (?, ?, ?, ?, ?)',
                         (trainer_id, service_id, desired_date, selected_time, session['user_id']))

    return redirect('/user')


@login_required
@app.route('/fitness_center/<int:gym_id>/trainer/<int:trainer_id>/rating', methods=['GET', 'POST'])
def trainer_rating(gym_id, trainer_id):
    user_id = session.get('user_id')

    if request.method == 'POST':
        rating = request.form.get('rating')
        review_text = request.form.get('review')

        new_review = Review(
            trainer_id=trainer_id,
            gym_id=gym_id,
            user_id=user_id,
            rating=rating,
            review=review_text
        )
        database.db_session.add(new_review)
        database.db_session.commit()
        return redirect(f'/fitness_center/{gym_id}/trainer/{trainer_id}/rating')

#opinia
    reviews = database.db_session.query(Review, Trainer.name.label('trainer_name'), FitnessCenter.name.label('gym_name'),
                                        models.User.login.label('user_login')) \
        .join(Trainer, Trainer.id == Review.trainer_id) \
        .join(FitnessCenter, FitnessCenter.id == Review.gym_id) \
        .join(models.User, models.User.id == Review.user_id) \
        .filter(Review.trainer_id == trainer_id, Review.gym_id == gym_id) \
        .all()

    return render_template('trainer_rating.html', reviews=reviews, gym_id=gym_id, trainer_id=trainer_id)


@login_required
@app.route('/fitness_center', methods=["GET", "POST"])
def fitness_center():
    if request.method == 'POST':
        form_data = request.form
        user1 = models.User(name=form_data["name"], adress=form_data['adress'], contacts=form_data['contacts'])
        database.db_session.add(user1)
        database.db_session.commit()

    return render_template('fitness_center.html')

@app.route('/fitness_center/<int:gym_id>', methods=['GET'])
def get_fitness_center(gym_id):
    try:
        center = database.db_session.query(FitnessCenter).filter(FitnessCenter.id == gym_id).one()
        return render_template('fitness_center_id.html', fitness_center=center)
    except NoResultFound:
        return "Fitness center not found"

@login_required
@app.route('/fitness_center/<int:gym_id>/trainer', methods=['GET'])
def get_trainers(gym_id):
    try:
        trainers = database.db_session.query(Trainer).filter(Trainer.gym_id == gym_id).all()
        return render_template('trainer.html', trainers=trainers, gym_id=gym_id)
    except NoResultFound:
        return "No trainers found for this gym"

@app.route('/fitness_center/<int:gym_id>/services', methods=['GET'])
def get_services(gym_id):
    try:
        services = database.db_session.query(Service).filter(Service.gym_id == gym_id).all()
        return render_template('service.html', services=services)
    except NoResultFound:
        return "No services found for this gym"

@app.route('/fitness_center/<int:gym_id>/services/<int:service_id>', methods=['GET'])
def get_service_info(gym_id, service_id):
    try:
        service = database.db_session.query(Service).filter(Service.gym_id == gym_id, Service.id == service_id).one()
        return render_template('service_info.html', service=service)
    except NoResultFound:
        return "Service not found"







@app.route('/checkout', methods=['GET', "POST"])
def user_checkout_info():
    return render_template('checkout.html')


@login_required
@app.route('/shedule', methods=['GET'])
def shedule():
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT id, date, trainer, start_time, end_time FROM shedule')
    return render_template('shedule.html', shedule=res)


@login_required
@app.route('/shedule/add', methods=['GET', 'POST'])
def add_shedule():
    if request.method == 'POST':
        date = request.form.get('date')
        trainer = request.form.get('trainer')
        start_time = request.form.get('start_time')

        with SQLiteDatabase("db.db") as db:
            db.execute_query(
                'INSERT INTO shedule (date, trainer, start_time, end_time) VALUES (?, ?, ?)',
                (date, trainer, start_time)
            )

        return redirect('shedule')

    return render_template('add_shedule.html')


@login_required
@app.route('/pre_reservation', methods=['POST'])
def pre_reservation():
    trainer = request.form["trainer"]
    service = request.form["service"]
    desired_date = request.form["desired_date"]
    time_slots = calc_slots(trainer, service, desired_date)
    return render_template('pre_reservation.html', form_info={"trainer": trainer,
                                                              "service": service,
                                                              "desired_date": desired_date,
                                                              "time_slots": time_slots})


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5001)
app.secret_key = os.environ.get('SESSION_SECRET_KEY')
