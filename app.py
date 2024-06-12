from flask import Flask, request
import sqlite3

app = Flask(__name__)

# Функція для перетворення рядка результату в словник
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Функція для виконання запитів до бази даних та отримання результатів
def get_from_db(query, many=True):
    con = sqlite3.connect("db.db")
    con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query)
    if many:
        res = cur.fetchall()
    else:
        res = cur.fetchone()
    con.close()
    return res

# Функція для виконання запитів INSERT, UPDATE, DELETE до бази даних
def insert_to_db(query):
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    con.close()

# Маршрут та обробник для відображення форми реєстрації
@app.route('/register', methods=['GET'])
def registered_form():
    return """
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
    </form>
    """

# Маршрут та обробник для обробки даних форми реєстрації
@app.route('/register', methods=['POST'])
def new_user_register():
    form_data = request.form
    insert_to_db(f'INSERT INTO user (login, password, birth_date, phone) VALUES '
                 f'("{form_data["login"]}", "{form_data["password"]}", "{form_data["birth_date"]}", "{form_data["phone"]}")')
    return f'user registered'


@app.get('/register')
def get_register():
    return f'get register'

@app.post('/register')
def post_register():
    return f'user registered'

@app.get('/user')
def get_user():
    return f'get user'

@app.post('/user')
def post_user():
    return f'post user'

@app.put('/user')
def put_user():
    return f'put user'



@app.post('/login')
def user_login():
    return 'please sign in to login'
@app.get('/login')
def user_login_form():
    return 'please enter login'

@app.get("/user/funds")
def get_user_funds():
    return f'get user funds'

@app.post("/user/funds")
def post_user_funds():
    return f'post user funds'


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