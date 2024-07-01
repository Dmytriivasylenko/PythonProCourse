import datetime
import sqlite3
import json
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

def check_credentials(login, password):
    query = 'SELECT * FROM user WHERE login = ? AND password = ?'
    with SQLiteDatabase('db.db') as db:
        user = db.execute_query(query, (login, password), fetch_one=True)
        return user is not None

def select_method(self, table, condition=None, columns=None, fetch_all=True, join=None):
    query = 'SELECT'
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


def clac_slots(user_id, trainer_id, service_id):
    query = f"""SELECT * FROM reservation,
    join service on service.id = reservation.service_id,
    where trainer_id = {trainer_id}
"""
with SQLiteDatabase('db.db') as db:
    booked_time = db.select_method("reservation", {"trainer": "trainer_id", "date": "31.05.2024"}, join={"service": "service_id=reservation.service_id}"}, fetch_all=True)
    trainer_schedule = db.select_method("trainer_schedule", {"trainer": "trainer_id", "date": "31.05.2024"}, fetch_all=False)
    trainer_capacity = db.select_method('trainer_services', {'trainer_id':'trainer_id', "service_id": 'service_id'}, fetch_all=False)
    start_dt = datetime.datetime.strptime(trainer_schedule["date"]+' '+trainer_schedule["start_time"], "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.datetime.strptime(trainer_schedule["date"]+' '+trainer_schedule["end_time"], "%Y-%m-%d %H:%M:%S")
    curr_dt = start_dt
    date_times = {}
    while curr_dt < end_dt:
        date_times[curr_dt] = trainer_capacity
        curr_dt += datetime.timedelta(minutes=15)
    for one_booking in booked_time:
        booking_date = one_booking["date"]
        booking_time = one_booking["time"]
        booking_duration = one_booking["duration"]
        one_booking_start = datetime.datetime.strptime("booking_date + "" + booking_time", "%Y-%m-%d %H:%M:%S")
        booking_end = one_booking_start + datetime.timedelta(minutes=booking_duration)
        curr_dt = one_booking_start
        while curr_dt < end_dt:
            date_times[curr_dt] += 1
            curr_dt += datetime.timedelta(minutes=15)

print('')

clac_slots(1, 1, 2)