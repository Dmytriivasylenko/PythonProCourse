import datetime
import sqlite3
from datetime import datetime
from sqlalchemy.orm import joinedload
import database
import models

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class SQLiteDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row  #повертати рядки як словники
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor

    def fetch_all(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=None):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()



def check_credentials(username, password):
    database.init_db()
    user = database.db_session.query(models.User).options(joinedload('*')).filter_by(login=username, password=password).first()
    return user



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



def calc_slots(trainer_id, service_id, desired_date):
    with SQLiteDatabase('db.db') as db:
        # Query to get the booked times for the specific trainer
        booked_time = db.fetch_all(
            "SELECT * FROM reservation WHERE trainer_id = ?", (trainer_id,)
        )

        # Query to get the trainer's schedule for a specific date
        trainer_schedule = db.fetch_one(
            "SELECT * FROM trainer_schedule WHERE trainer_id = ? AND date = ?",
            (trainer_id, desired_date)
        )

        # Query to get the service details (adjust based on actual schema)
        service_info = db.fetch_one(
            'SELECT * FROM service WHERE id = ?',
            (service_id,)
        )

        # Ensure the necessary data exists
        if not (trainer_schedule and service_info):
            return []

        # Initialize start and end times
        start_dt = datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["start_time"], "%Y-%m-%d %H:%M")
        end_dt = datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["end_time"], '%Y-%m-%d %H:%M')

        curr_dt = start_dt
        date_times = {}

        # Fill time slots based on capacity (assuming capacity is part of another query)
        while curr_dt < end_dt:
            date_times[curr_dt] = 1  # Adjust capacity if necessary
            curr_dt += datetime(minutes=15)

        # Subtract booked times from available slots
        for booking in booked_time:
            booking_start = datetime.strptime(booking["date"] + ' ' + booking["time"], "%Y-%m-%d %H:%M")
            booking_end = booking_start + datetime(minutes=booking["duration"])
            curr_dt = booking_start
            while curr_dt < booking_end:
                date_times[curr_dt] -= 1
                curr_dt += datetime(minutes=15)

        # Find available time slots
        result_times = []
        service_duration = service_info['duration']
        service_start_time = start_dt

        while service_start_time <= end_dt - datetime(minutes=service_duration):
            service_end_time = service_start_time + datetime(minutes=service_duration)

            everything_is_free = all(
                date_times.get(service_start_time + datetime(minutes=15 * i), 0) > 0
                for i in range(int(service_duration / 15))
            )

            if everything_is_free:
                result_times.append(service_start_time)

            service_start_time += datetime(minutes=15)

        return [dt.strftime("%H:%M") for dt in result_times]
