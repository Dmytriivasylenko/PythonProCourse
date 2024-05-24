from flask import Flask

app = Flask(__name__)

@app.post('/register')
def new_user_register():
    return 'new  user registered'

@app.get('/register')
def registered_form ():
    return ' please sign in to register user'


@app.post('/login')
def user_login ():
    return ' please sign in to login'
@app.get('/login')
def user_login_form ():
    return 'please enter login'


@app.post('/user')
def add_user_info ():
    return 'user data were modified'
@app.get('/user')
def user_info():
    return 'user information '
@app.put('/user')
def user_update():
    return 'user was successfully updated '


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
def user_select():  # put application's code here
    return 'please find a fitness center'

@app.get('/fitness_center/<gym_id>')
def user_reservation(gym_id):  # put application's code here
    return f' fitness center {gym_id} please select a fitness center'


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
