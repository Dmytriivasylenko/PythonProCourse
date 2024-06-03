import cursor
from flask import Flask, request
import sqlite3

con = sqlite3.connect('dp.db')
cur = con.cursor()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_from_db(query, many=True ):
    con = sqlite3.connect("dp.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)
    if many:
        res = cur.fetchall()
    else:
        res = cur.fetchone()
    con.close()
    return res


def insert_to_db(query):
    con = sqlite3.connect("dp.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()
app = Flask(__name__)



@app.get('/register')
def registered_form():
    return f"""
  <form action="/register" method="post">"
  <label for="login">login:</label><br>
  <input type="text" id="login" name="login"><br>
  <label for="password">password:</label><br>
  <input type="password" id="password" name="password"><br>
  <label for="birth_date">birth_date:</label><br>
  <input type="date" id="birth_date" name="birth_date"><br>
  <label for="phone">phone:</label><br>
  <input type="text" id="phone" name="phone"><br>
  <input type="submit" value="Submit">
</form>"""

@app.post('/register')
def new_user_register():
    form_data = request.form
    insert_to_db(
        f'INSERT INTO user (login, password, birth_date, phone) '
        f'VALUES ({form_data["login"]},{form_data["password"]},{form_data["birth_date"]},{form_data["phone"]}')
    return f'user registered'

@app.post('/login')
def user_login():
    return 'please sign in to login'
@app.get('/login')
def user_login_form():
    return 'please enter login'


@app.get('/user')
def add_user_info():
    res = get_from_db(f'SELECT login, phone, birth_date FROM user WHERE id=1')
    return res

@app.post('/user')
def user_info():
    return f'user information '
@app.put('/user')
def user_update():
    return f'user was successfully updated '


@app.post('/funds')
def add_funds():
    return 'user account was funded'
@app.get('/funds')
def user_deposit():
    return 'user deposit value'


@app.post('/reservations')
def user_reservation_info():
    return 'user reservation info'

@app.get('/reservations')
def user_reservation_added():
    return 'user reservations was added'


@app.get('/user/reservations/<reservation_id>')
def reservation_info(reservation_id):  # put application's code here
    return f' user reservations {reservation_id} '
@app.put('/user/reservations/<reservation_id>/')
def reservation_add(reservation_id):  # put application's code here
    return f'user reservations {reservation_id} added'
@app.delete('/user/reservations/<reservation_id>/')
def reservation_update(reservation_id):  # put application's code here
    return 'user reservations was updated {reservation_id}'


@app.get('/checkout')
def user_checkout_info():  # put application's code here
    return 'user balance info '
@app.post('/checkout')
def user_checkout_added():  # put application's code here
    return 'user balance information added'
@app.put('/checkout')
def user_checkout_update():  # put application's code here
    return 'balance was updated'

@app.get('/fitness_center')
def user_select():
    res = get_from_db('select name, adress from fitness_center', many=True)
    return str(res)

@app.get('/fitness_center/<gym_id>')
def user_reservation(gym_id):
    res = get_from_db(f'select name, adress from fitness_center where id = {gym_id}', many=False)
    return str(res)
    # put application's code here


@app.get('/fitness_center/<gym_id>/trainer')
def get_trainers(gym_id):  # put application's code here
    return f'fitness center {gym_id} trainers list'
@app.get('/fitness_center/<gym_id>/trainer/<trainer_id>')
def get_trainers_info(gym_id, trainer_id):  # put application's code here
    return f'fitness center {gym_id} trainer {trainer_id} trainers list'


@app.get('/fitness_center/<gym_id>/trainer/<trainer_id>/rating ')
def get_coach_rating(gym_id, trainer_id):  # put application's code here
    return f'fitness center {gym_id} rating {trainer_id} '
@app.post('/fitness_center/<gym_id>/trainer/<trainer_id>/rating ')
def set_coach_rating(gym_id, trainer_id):  # put application's code here
    return f'fitness center {gym_id} rating {trainer_id} rating was added'
@app.put('/fitness_center/<gym_id>/trainer/<trainer_id>/rating ')
def update_coach_score(gym_id, trainer_id):  # put application's code here
    return f'fitness center {gym_id} rating {trainer_id} was updated'



@app.get('/fitness_center/<gym_id>/services')
def get_service(gym_id):  # put application's code here
    return f'fitness center {gym_id} service list'






@app.get('/fitness_center/<gym_id>/services/<service_id> ')
def get_service_info(gym_id, service_id):  # put application's code here
    return f'fitness center {gym_id} service {service_id} service list'







@app.get('/fitness_center/<gym_id>/loyality_programs  ')
def user_information_program(gym_id):  # put application's code here
    return f'fitness center {gym_id} loyalty program list'


if __name__ == '__main__':
    app.run()
