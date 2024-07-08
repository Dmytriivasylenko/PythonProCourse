import os

from flask import Flask, render_template, request, redirect, session

import utils
from utils import SQLiteDatabase

app = Flask(__name__)
app.secret_key = b'_343435#y2L"F4Q8z\n\xec]/'


def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        results = func(*args, **kwargs)
        return results

    return wrapper

@app.route("/", methods=["GET", "POST", "PUT"])
def index():
    return "current method:" + str(request.method)

@app.route('/register', methods=['GET', 'POST'])
def get_register():
    if request.method == 'POST':
        form_data = request.form
        query = 'INSERT INTO user (login, password, birth_date, phone) VALUES (?, ?, ?, ?)'
        with SQLiteDatabase("db.db") as db:
            db.execute_query(query, (form_data["login"], form_data["password"],
                                     form_data["birth_date"], form_data["phone"]))
        return redirect('/login')
    return render_template('register.html')





@login_required
@app.route('/user', methods=['GET'])
def get_users():
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT * FROM user')
    return render_template('user.html', users=res)

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def user_details(user_id):
    if request.method == 'POST':
        form_data = request.form
        query = 'UPDATE user SET login = ?, phone = ?, birth_date = ? WHERE id = ?'
        with SQLiteDatabase("db.db") as db:
            res = db.execute_query(query, (["login", form_data], form_data["phone"], form_data["birth_date"], user_id))
        return redirect('get_users', user_id=res)

    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT login, phone, birth_date FROM user WHERE id = ?', (user_id,))
    return render_template('user_detail.html', user=res)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login= request.form['login']
        password = request.form['password']
        if utils.check_credentials(login, password):
            with SQLiteDatabase("db.db") as db:
                user = db.execute_query('SELECT * FROM user WHERE login = ?', ('login',), fetch_one=True)
            if user:
                session['user_id'] = user['id']
                return redirect('/user')
            else:
                return 'User not found'
        else:
            return 'Invalid login or password'
    return render_template('login.html')
@app.route('/user')
def user_dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return f"Welcome user with ID {session['user_id']}"

@login_required
@app.route('/logout', methods=['GET'])
def logout():
    session.pop("user_id", None)
    return redirect('/login')

@app.route('/user/<user_id>', methods=['GET', 'POST'])
def get_user(user_id):
    if request.method == 'POST':
        form_data = request.form
        query = 'UPDATE user SET login = ?, phone = ?, birth_date = ? WHERE id = ?'
        with SQLiteDatabase("db.db") as db:
            db.execute_query(query, (form_data["login"], form_data["phone"], form_data["birth_date"], user_id))
        return 'User data modified'
    elif request.method == 'GET':
        with SQLiteDatabase("db.db") as db:
            res = db.fetch_one('SELECT login, phone, birth_date FROM user WHERE id = ?', (user_id,))
        return res


@login_required
@app.route('/user/reservations', methods=['GET', 'POST'])
def user_reservations():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        if not user_id:
            return redirect('login')

        with SQLiteDatabase('db.db') as db:
            reservations = db.execute_query(
                'reservations',
                condition={'user_id': user_id},
                columns=['id', 'details'],
                fetch_all=True
            )
        return render_template('reservations.html', user_reservation=reservations)

    elif request.method == 'POST':
        form_dict = request.form
        service_id = form_dict['service_id']
        trainer_id = form_dict['trainer_id']
        slot_id = form_dict['slot_id']
        result = utils.clac_slots(service_id, trainer_id, slot_id)
        return "create user reservation"

@login_required
@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST'])
def user_reservation(reservation_id):
    if request.method == 'POST':
        new_date = request.form.get('new_date')
        new_time = request.form.get('new_time')

        if not new_date or not new_time:
            return 'New date and time are required'

        query = 'UPDATE reservations SET date=?, time=? WHERE id=?'
        with SQLiteDatabase('db.db') as db:
            db.execute_query(query, (new_date, new_time, reservation_id))

        return redirect('user_reservations')

    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT * FROM reservations WHERE id = ?', (reservation_id,))
    return render_template('reservation_detail.html', reservation=res)

@login_required
@app.route('/user/reservations/<reservation_id>/delete', methods=['POST'])
def delete_reservation(reservation_id):
    query = 'DELETE FROM reservations WHERE id=?'
    with SQLiteDatabase('db.db') as db:
        db.execute_query(query, (reservation_id,))
    return redirect('user_reservations')

@login_required
@app.route('/fitness_center/<gym_id>/trainer/<trainer_id>/rating', methods=['GET', 'POST'])
def trainer_rating(gym_id, trainer_id):
    user_id = session.get('user_id')
    if request.method == 'POST':
        rating = request.form.get('rating')
        review_text = request.form.get('review')
        with SQLiteDatabase("db.db") as db:
            db.execute_query(
                "INSERT INTO review (trainer_id, gym_id, user_id, rating, review) VALUES (?, ?, ?, ?, ?)",
                (trainer_id, gym_id, user_id, rating, review_text)
            )
        return redirect('trainer_rating', gym_id=gym_id, trainer_id=trainer_id)

    #отримати відгук який дав користувач і заповни ім форму додатковий запит на відгук користувача
    with SQLiteDatabase("db.db") as db:
        reviews = db.select_method(
            'review',
            join={'trainer': 'review.trainer_id = trainer.id', 'gym': 'review.gym_id = gym.id', 'user':
                'review.user_id = user.id'},
            columns=['review.review AS review_text', 'review.rating AS review_rating', 'user.login AS user_login',
                     'trainer_id AS trainer_id'],
            condition={'review.trainer_id': trainer_id, 'review.gym_id': gym_id},
            fetch_all=True
        )
    return render_template('trainer_rating.html', reviews=reviews, gym_id=gym_id, trainer_id=trainer_id)
@login_required
@app.route('/fitness_center', methods=['GET'])
def fitness_center():
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT id, name, adress, contacts FROM fitness_center')
    return render_template('fitness_center.html', fitness_center=res)

@app.route('/fitness_center/<gym_id>', methods=['GET'])
def get_fitness_center(gym_id):
    with SQLiteDatabase("db.db") as db:
        center = db.fetch_one('SELECT id, name, address FROM fitness_center WHERE id = ?', (gym_id,))
    return render_template('fitness_center_id.html', fitness_center=center)
@login_required
@app.route('/fitness_center/<gym_id>/trainer', methods=['GET'])
def get_trainers(gym_id):
    with SQLiteDatabase("db.db") as db:
        trainers = db.fetch_all('SELECT id, name FROM trainer WHERE gym_id = ?', (gym_id,))
    return render_template('trainers.html', trainers=trainers, gym_id=gym_id)

@app.route('/fitness_center/<int:gym_id>/services', methods=['GET'])
def get_services(gym_id):
    with SQLiteDatabase("db.db") as db:
        services = db.fetch_all('SELECT * FROM services WHERE gym_id = ?', (gym_id,))
    return render_template('services.html', services=services)

@app.route('/fitness_center/<int:gym_id>/services/<int:service_id>', methods=['GET'])
def get_service_info(gym_id, service_id):
    with SQLiteDatabase("db.db") as db:
        service = db.fetch_one('SELECT * FROM services WHERE gym_id = ? AND id = ?', (gym_id, service_id))
    return render_template('services.html', service=service)


@app.route('/fitness_center/<gym_id>/loyalty_programs', methods=['GET'])
def get_loyalty_programs(gym_id):
    with SQLiteDatabase("db.db") as db:
        programs = db.fetch_all('SELECT * FROM loyalty_programs WHERE gym_id = ?', (gym_id,))
    return render_template('loyalty_programs.html', loyalty_programs=programs)

@app.route('/checkout', methods=['GET'])
def user_checkout_info():
    return render_template('checkout.html')

@app.route('/checkout', methods=['POST'])
def user_checkout_added():
    return 'User balance information added'

@app.route('/checkout', methods=['PUT'])
def user_checkout_update():
    return 'Balance was updated'

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

        utils.clac_slots(trainer, service, desired_date)
        return render_template('pre_reservation.html', form_info = {"trainer":trainer,
                                                                    "service": service,
                                                                    "desired_date": desired_date,
                                                                    "time_slots": time_slots})


if __name__ == '__main__':
    app.run(debug=True)
app.secret_key = os.environ.get('SESSION_SECRET_KEY')
