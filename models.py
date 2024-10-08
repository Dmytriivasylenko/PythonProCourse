from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class FitnessCenter(Base):
    __tablename__ = 'fitness_center'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    adress = Column(String(255), nullable=False)
    contacts = Column(String(100), nullable=False)

    def __repr__(self):
        return f'<FitnessCenter {self.name!r}>'

class Gym(Base):
    __tablename__ = 'gym'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    contacts = Column(Integer, nullable=False)
    adress = Column(String(100), nullable=False)

    def __init__(self, id, name, contacts, adress):
        self.id = id
        self.name = name
        self.contacts = contacts
        self.adress = adress

    def __repr__(self):
        return f'<Gym {self.id!r}>'


#
class Reservation(Base):
    __tablename__ = 'reservation'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey('fitness_center.id'))
    service_id = Column(Integer, ForeignKey('fitness_center.id'))
    date = Column(DateTime, nullable=False)
    time = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey('fitness_center.id'))

    def __init__(self, trainer_id, service_id, date, time):
        self.trainer_id = trainer_id
        self.service_id = service_id
        self.date = date
        self.time = time
        self.user_id = trainer_id
        self.service_id = service_id

    def __repr__(self):
        return f'<Reservation {self.trainer_id!r}>'


class Review(Base):
    __tablename__ = 'review'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    trainer_id = Column(Integer, ForeignKey('fitness_center.id'))
    gym_id = Column(Integer, ForeignKey('fitness_center.id'))
    user_id = Column(Integer, ForeignKey('fitness_center.id'))
    rating = Column(Integer, nullable=False)
    def __init__(self, trainer_id, gym_id, user_id, rating):
        self.trainer_id = trainer_id
        self.gym_id = gym_id
        self.user_id = user_id
        self.rating = rating
        self.rating = rating

    def __repr__(self):
        return f'<Review {self.trainer_id!r}>'


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    fitness_center = Column(Integer, ForeignKey('fitness_center.id'))
    max_atte = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(String(50), nullable=False)
    service_id = Column(Integer, ForeignKey('fitness_center.id'))

    def __init__(self, name, fitness_center, max_attendance, duration, price, description):
        self.id = id
        self.name = name
        self.fitness_center = fitness_center
        self.max_atte = max_attendance
        self.duration = duration
        self.price = price
        self.description = description

    def __repr__(self):
        return f'<Service {self.name!r}>'


class Trainer(Base):
    __tablename__ = 'trainer'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    gym_id = Column(Integer, ForeignKey('fitness_center.id'))
    fitness_center = relationship("FitnessCenter")

    def __init__(self, id, name, gym_id):
        self.id = id
        self.name = name
        self.gym_id = gym_id

    def __repr__(self):
        return f'<Trainer {self.id!r}>'



class Schedule(Base):
    __tablename__ = 'trainer_schedule'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    trainer_id = Column(Integer, ForeignKey('fitness_center.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)


    def __init__(self, date, trainer_id, start_time, end_time):
        self.date = date
        self.trainer_id = trainer_id
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return f'<Schedule {self.trainer_id!r}>'


class TrainerServices(Base):
    __tablename__ = 'trainer_services'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    gym_id = Column(Integer, ForeignKey('fitness_center.id'))
    name = Column(String(50), nullable=False)
    description = Column(String(100), nullable=False)
    trainer_id = Column(Integer, ForeignKey('fitness_center.id'))

    def __init__(self, name, description, gym_id):
        self.name = name
        self.description = description
        self.gym_id = gym_id

    def __repr__(self):
        return f'TrainerServices {self.gym_id!r}>'



class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    login = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    birth_date = Column(String, default=datetime(1940, 1, 1), nullable=False)
    phone = Column(String(50), nullable=False)
    funds = Column(Integer, default=0, nullable=False)
    #profile_image = Column(String(150), nullable=True)
    #email = Column(String(150), nullable=True)

    def __init__(self, login, password, birth_date, phone):
        self.login = login
        self.password = password
        self.birth_date = birth_date
        self.phone = phone

    def add_funds(self, amount):
        if amount is not None and amount > 0:
            self.funds += amount

    def withdraw(self, amount):
        if amount is not None and amount > 0:
            new_funds = self.funds - amount
            self.funds = max(new_funds, 0)

    def __repr__(self):
        return f'<User {self.login!r}>'

