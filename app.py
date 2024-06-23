from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)

# Функція для перетворення рядка результату в словник
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

# Клас для роботи z SQLite
class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = dict_factory
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

    def fetch_all(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        res = cursor.fetchall()
        return res if res else []

    def fetch_one(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        res = cursor.fetchone()
        return res if res else None

    def execute_query(self, query, params=()):
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()

@app.route("/")
def hello():
    return render_template('index.html')

@app.route('/register', methods=['GET'])
def registered_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def new_user_register():
    form_data = request.form
    query = 'INSERT INTO user (login, password, birth_date, phone) VALUES (?, ?, ?, ?)'
    with SQLiteDatabase("db.db") as db:
        db.execute_query(query, (form_data["login"], form_data["password"], form_data["birth_date"], form_data["phone"]))
    return 'User registered'

@app.route('/user/<user_id>', methods=['GET', 'POST', 'PUT'])
def get_user(user_id):
    if request.method == 'POST':
        form_data = request.form
        query = 'UPDATE user SET login = ?, phone = ?, birth_date = ? WHERE id = ?'
        with SQLiteDatabase("db.db") as db:
            db.execute_query(query, (form_data["login"], form_data["phone"], form_data["birth_date"], user_id))
        return 'User data modified'
    elif request.method == 'PUT':
        form_data = request.form
        query = 'UPDATE user SET login = ?, phone = ?, birth_date = ? WHERE id = ?'
        with SQLiteDatabase("db.db") as db:
            db.execute_query(query, (form_data["login"], form_data["phone"], form_data["birth_date"], user_id))
        return 'User info updated'
    else:
        with SQLiteDatabase("db.db") as db:
            res = db.fetch_one('SELECT login, phone, birth_date FROM user WHERE id = ?', (user_id,))
        return jsonify(res)

@app.route('/user', methods=['GET'])
def get_users():
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT * FROM user')
    return render_template('user.html', user=res)

@app.post('/login')
def user_login():
    return 'Please sign in to login'

@app.get('/login')
def get_login():
    res = get_from_db('SELECT * FROM user')
    return res

@app.route('/reservations', methods=['POST'])
def user_reservation_info():
    return 'User reservation info'

@app.route('/reservations', methods=['GET'])
def user_reservation_added():
    return 'User reservations was added'

@app.route('/user/reservations/<reservation_id>', methods=['GET'])
def reservation_info(reservation_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT * FROM reservations WHERE id = ?', (reservation_id,))
    return jsonify(res)

@app.route('/user/reservations/<reservation_id>', methods=['PUT'])
def reservation_add(reservation_id):
    return f'User reservations {reservation_id} added'

@app.route('/user/reservations/<reservation_id>', methods=['DELETE'])
def reservation_update(reservation_id):
    return f'User reservations was updated {reservation_id}'

@app.route('/checkout', methods=['GET'])
def user_checkout_info():
    return render_template('checkout.html')

@app.route('/checkout', methods=['POST'])
def user_checkout_added():
    return 'User balance information added'

@app.route('/checkout', methods=['PUT'])
def user_checkout_update():
    return 'Balance was updated'

@app.route('/fitness_center', methods=['GET'])
def user_select():
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT name, address, contacts FROM fitness_center')
    return jsonify(res)

@app.route('/fitness_center/<gym_id>', methods=['GET'])
def get_fitness_center(gym_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT name, address FROM fitness_center WHERE id = ?', (gym_id,))
    return jsonify(res)


@app.route('/fitness_center/<gym_id>/trainer', methods=['GET'])
def get_trainers(gym_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT id, name FROM trainer WHERE gym_id = ?', (gym_id,))
    return render_template('trainer_review.html', trainers=res)

@app.route('/fitness_center/<gym_id>/trainer/<trainer_id>', methods=['GET'])
def get_trainers_info(gym_id, trainer_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT * FROM trainer WHERE gym_id = ? AND id = ?', (gym_id, trainer_id))
    return jsonify(res)

@app.route('/fitness_center/<gym_id>/trainer/<trainer_id>/rating', methods=['GET'])
def get_coach_rating(gym_id, trainer_id):
    return f'Fitness center {gym_id} rating {trainer_id}'

@app.route('/fitness_center/<gym_id>/trainer/<trainer_id>/rating', methods=['POST'])
def set_coach_rating(gym_id, trainer_id):
    return f'Fitness center {gym_id} rating {trainer_id} rating was added'

@app.route('/fitness_center/<gym_id>/trainer/<trainer_id>/rating', methods=['PUT'])
def update_coach_score(gym_id, trainer_id):
    return f'Fitness center {gym_id} rating {trainer_id} was updated'

@app.route('/fitness_center/<int:gym_id>/services', methods=['GET'])
def get_service(gym_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT * FROM services WHERE gym_id = ?', (gym_id,))
    return jsonify(res)

@app.route('/fitness_center/<int:gym_id>/services/<int:service_id>', methods=['GET'])
def get_service_info(gym_id, service_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT * FROM services WHERE gym_id = ? AND id = ?', (gym_id, service_id))
    return jsonify(res)

@app.route('/fitness_center/<gym_id>/loyality_programs', methods=['GET'])
def user_information_program(gym_id):
    with SQLiteDatabase("db.db") as db:
        res = db.fetch_all('SELECT * FROM loyalty_programs WHERE gym_id = ?', (gym_id,))
    return jsonify(res)

if __name__ == '__main__':
    app.run()
