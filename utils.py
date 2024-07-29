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
        booked_time = db.fetch_all(
            "SELECT * FROM reservation JOIN service ON service.id = reservation.service_id WHERE trainer_id = ?",
            (trainer_id,))
        trainer_schedule = db.fetch_one("SELECT * FROM trainer_schedule WHERE trainer_id = ? AND date = ?",
                                        (trainer_id, desired_date))
        trainer_capacity = db.fetch_one('SELECT * FROM trainer_services WHERE trainer_id = ? AND service_id = ?',
                                        (trainer_id, service_id))
        service_info = db.fetch_one("SELECT * FROM service WHERE id = ?", (service_id,))

    if not (trainer_schedule and trainer_capacity and service_info):
        return []

    start_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["start_time"],
                                          "%Y-%m-%d %H:%M")
    end_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["end_time"], '%Y-%m-%d %H:%M')
    curr_dt = start_dt
    date_times = {}
    while curr_dt < end_dt:
        date_times[curr_dt] = trainer_capacity['capacity']
        curr_dt += datetime.timedelta(minutes=15)

    for one_booking in booked_time:
        booking_start = datetime.datetime.strptime(one_booking["date"] + ' ' + one_booking["time"], "%Y-%m-%d %H:%M")
        booking_end = booking_start + datetime.timedelta(minutes=one_booking["duration"])
        curr_dt = booking_start
        while curr_dt < booking_end:
            date_times[curr_dt] -= 1
            curr_dt += datetime.timedelta(minutes=15)

    result_times = []
    service_duration = service_info['duration']
    service_start_time = start_dt
    while service_start_time <= end_dt - datetime.timedelta(minutes=service_duration):
        service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
        everything_is_free = all(date_times.get(service_start_time + datetime.timedelta(minutes=15 * i), 0) > 0 for i in
                                 range(int(service_duration / 15)))
        if everything_is_free:
            result_times.append(service_start_time)
        service_start_time += datetime.timedelta(minutes=15)

    return [dt.strftime("%H:%M") for dt in result_times]
