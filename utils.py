import datetime

from datetime import datetime

import sqlite3


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


def check_credentials(login: object, password: object) -> object:
    query = 'SELECT * FROM user WHERE login = ? AND password = ?'
    with SQLiteDatabase(login) as db:
        user = db.execute_query(query, (login, password))
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


def clac_slots(trainer_id, service_id, desired_date):
    with SQLiteDatabase('db.db') as db:
        booked_time = db.select_method("reservation", {"trainer": "trainer_id", "date": "31.05.2024"},
                                       join={"service": "service.id=reservation.service_id}"}, fetch_all=True)
        trainer_schedule = db.select_method("trainer_schedule", {"trainer_id": "trainer_id", "date": "31.05.2024"},
                                            fetch_all=False)
        trainer_capacity = db.select_method('trainer_services',
                                            {'trainer_id': 'trainer_id', "service_id": 'service_id'},
                                            fetch_all=False)
        service_info = db.select_method("service", {"service_id": "service_id"}, fetch_all=False)
        start_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["start_time"],
                                              "%d-%m-%y %H:%M")
        end_dt = datetime.datetime.strptime(trainer_schedule["date"] + ' ' + trainer_schedule["end_time"],
                                            "%d-%m-%y %H:%M")
        curr_dt = start_dt
        trainer_schedule = {}
        date_times = {}
        while curr_dt < end_dt:
            date_times[curr_dt] = trainer_capacity['capacity']
            curr_dt += datetime.timedelta(minutes=15)
        for one_booking in booked_time:
            booking_date = one_booking["date"]
            booking_time = one_booking["time"]
            booking_duration = one_booking["duration"]
            one_booking_start = datetime.datetime.strptime("booking_date + " " + booking_time", "%d-%m-%y %H:%M")
            booking_end = one_booking_start + datetime.timedelta(minutes=booking_duration)
            curr_dt = one_booking_start
            while curr_dt < end_dt:
                date_times[curr_dt] += 1
                curr_dt += datetime.timedelta(minutes=15)
        result_times = []
        service_duration = service_info['duration']
        service_start_time = start_dt
        while service_start_time <= end_dt - datetime.timedelta(service_duration):
            service_end_time = service_start_time + datetime.timedelta(minutes=service_duration)
            everything_is_free = True
            iter_start_time = service_start_time
            while iter_start_time <= service_end_time:
                if trainer_schedule[iter_start_time] == 0 or service_end_time > end_dt:
                    everything_is_free = False
                    break
                iter_start_time += datetime.timedelta(minutes=15)

            if everything_is_free:
                result_times.append(service_start_time)

            service_start_time += datetime.timedelta(minutes=15)
            final_result = [datetime.datetime.strptime(el, '%H:%M') for el in result_times]
            return final_result
    clac_slots(1, 2, 3)
