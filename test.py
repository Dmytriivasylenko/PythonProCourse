from flask import Flask, render_template, request, redirect, session, json
import sqlite3

app = Flask(__name__)
app.secret_key = b'_343435#y2L"F4Q8z\n\xec]/'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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

    def execute_query(self, query, params=(), fetch_one=False, fetch_all=True):
        cur = self.connection.cursor()
        cur.execute(query, params)
        if fetch_one:
            result = cur.fetchone()
        elif fetch_all:
            result = cur.fetchall()
        else:
            result = None
        self.connection.commit()
        return result
#DODALEM
    def commit(self):
        try:
            self.connection.commit()
            print("Changes committed successfully.")
        except sqlite3.Error as e:
            print(f"Error committing changes: {e}")

def check_credentials(login, password):
    query = 'SELECT * FROM user WHERE login = ? AND password = ?'
    with SQLiteDatabase('db.db') as db:
        user = db.execute_query(query, (login, password), fetch_one=True)
        return user is not None

def select_method(self, table, condition=None, columns=None, fetch_all=True, join=None):
    query = 'SELECT '
    if columns:
        query += ', '.join(columns)
    else:
        query += '* '
    query += f'FROM {table} '

    if join:
        for join_table, join_condition in join.items():
            query += f'JOIN {join_table} ON {join_condition} '

    if condition:
        conditions = []
        for key, value in condition.items():
            conditions.append(f'{key} = ?')
        query += 'WHERE ' + ' AND '.join(conditions)

    cursor = self.connection.cursor()
    cursor.execute(query, tuple(condition.values()) if condition else ())

    if fetch_all:
        result = cursor.fetchall()
    else:
        result = cursor.fetchone()

    return result if result else None

def login_required(func):
    def wrapper(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        results = func(*args, **kwargs)
        return results

    return wrapper



@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')

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
            res = db.execute_query(query, (form_data["login"], form_data["phone"], form_data["birth_date"], user_id))
        return redirect('get_users', user_id=res)

    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT login, phone, birth_date FROM user WHERE id = ?', (user_id,))
    return render_template('user_detail.html', user=res)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if check_credentials(login, password):
            with SQLiteDatabase("db.db") as db:
                user = db.execute_query('SELECT * FROM user WHERE login = ?', (login,), fetch_one=True)
            session['user_id'] = user['id'] if user else None
            return redirect('/user')
        else:
            return 'Invalid login or password'
    return render_template('login.html')

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
        return json(res)


@app.route('/user/reservations', methods=['GET', 'POST'])
@login_required
def user_reservations():
    user_id = session.get('user_id')
    if request.method == 'POST':
        details = request.form.get('details')
        query = 'INSERT INTO reservations (user_id, details) VALUES (?, ?)'
        with SQLiteDatabase('db.db') as db:
            db.execute_query(query, (user_id, details))
        return redirect('user_reservations')

    with SQLiteDatabase('db.db') as db:
        reservations = db.select_method(
            'reservations',
            condition={'user_id': user_id},
            columns=['id', 'details'],
            fetch_all=True
        )
    return render_template('reservations.html', user_reservation=reservations)

@app.route('/user/reservations/<reservation_id>', methods=['GET', 'POST', 'DELETE'])
def handle_reservation(reservation_id):
    if request.method == 'POST':
        new_date = request.form.get('new_date')
        new_time = request.form.get('new_time')

        if not new_date or not new_time:
            return 'New date and time are required'

        query = 'UPDATE reservations SET date=?, time=? WHERE id=?'
        with SQLiteDatabase('db.db') as db:
            db.execute_query(query, (new_date, new_time, reservation_id))

        return redirect('user_reservations')

    elif request.method == 'DELETE':
        query = 'DELETE FROM reservations WHERE id=?'
        with SQLiteDatabase('db.db') as db:
            db.execute_query(query, (reservation_id,))
        return f'Reservation {reservation_id} deleted successfully'

    with SQLiteDatabase("db.db") as db:
        res = db.fetch_one('SELECT * FROM reservations WHERE id = ?', (reservation_id,))
    return render_template('reservation_detail.html', reservation=res)

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

    with SQLiteDatabase("db.db") as db:
        reviews = db.select_method(
            'review',
            join={'trainer': 'review.trainer_id = trainer.id', 'gym': 'review.gym_id = gym.id', 'user': 'review.user_id = user.id'},
            columns=['review.review AS review_text', 'review.rating AS review_rating', 'user.login AS user_login', 'trainer_id AS trainer_id'],
            condition={'review.trainer_id': trainer_id, 'review.gym_id': gym_id},
            fetch_all=True
        )
    return render_template('trainer_rating.html', reviews=reviews, gym_id=gym_id, trainer_id=trainer_id)

@app.route('/fitness_center', methods=['GET'])
def fitness_centers():
    with SQLiteDatabase("db.db") as db:
        centers = db.fetch_all('SELECT id, name, address, contacts FROM fitness_center')
    return render_template('fitness_center.html', fitness_centers=centers)

@app.route('/fitness_center/<gym_id>', methods=['GET'])
def get_fitness_center(gym_id):
    with SQLiteDatabase("db.db") as db:
        center = db.fetch_one('SELECT id, name, address FROM fitness_center WHERE id = ?', (gym_id,))
    return render_template('fitness_center_id.html', fitness_center=center)

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
    return render_template('service_detail.html', service=service)

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



if __name__ == '__main__':
    app.run()



def commit(self, table, data):
    keys = list(data.keys())
    values = list(data.values())
    placeholders = ','.join(['?' for _ in values])
    query = f'INSERT INTO {table} ({", ".join(keys)}) VALUES ({placeholders})'
    try:
        cursor = self.connection.cursor()
        cursor.execute(query, values)
        self.connection.commit()
        print(f"Inserted data into {table} successfully.")
    except sqlite3.Error as e:
        print(f"Error inserting data into {table}: {e}")
    finally:
            cursor.close()