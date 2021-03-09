from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import random as Radom
from time import sleep
import json
import threading
import random as Radom
from time import sleep


app = Flask(__name__)
app.config['SECRET_KEY'] = '248889'
socketio = SocketIO(app)
app_started = False
PHILOSOPHERS = []
checking = threading.Lock() # Mutex ogólny
N = 5

def ack():
    print('message received')

@socketio.on('philosophers')
def run_philosophers(data):
    emit('philosophers', callback=ack)

@socketio.on('connection')
def connected(json):
    global app_started
    if (not app_started) and True:
        print('working')
        app_started = False
        emit('initialize', {'data': 'tmp'})
    print(json['data'])

@socketio.on('philosphers')
def update(json):
    emit('update', json)

@app.route('/')
def philosophers():
    return render_template('index.html', context={'philosophers': PHILOSOPHERS})

class Philosopher(threading.Thread):

    def __init__(self, pid):
        super().__init__(target=self.foo)
        self.pid = pid
        self.dishes_eaten = 0
        self.status = "Thinking"
        self.condition = threading.Condition() # Zaweira Mutex wewnątrz
        print("Philosopher created!")

    def foo(self):
        self.condition.acquire()
        while True:
            self.hungry()
            while not self.__check_forks():
                self.condition.wait()
            self.eating()
            self.thinking()

    @socketio.on('update')
    def eating(self):
        self.status = 'Eating'
        checking.release()
        eating_time = Radom.uniform(2.5, 3.5)
        #print(f'Philosopher {self.pid} started eating')
        e_data = { 'Pid': self.pid, 
                'Dishes eaten': self.dishes_eaten,
                'Status': self.status,
                'Remaining time': eating_time}
        print(e_data)
        socketio.emit('update', e_data)
        sleep(eating_time)
        checking.acquire()
        self.dishes_eaten += 1
        
        if PHILOSOPHERS[(self.pid + 1) % N].status == "Hungry":
            PHILOSOPHERS[(self.pid + 1) % N].condition.acquire()
            PHILOSOPHERS[(self.pid + 1) % N].condition.notify()
            PHILOSOPHERS[(self.pid + 1) % N].condition.release()
        if PHILOSOPHERS[(self.pid - 1) % N].status == "Hungry":
            PHILOSOPHERS[(self.pid - 1) % N].condition.acquire()
            PHILOSOPHERS[(self.pid - 1) % N].condition.notify()
            PHILOSOPHERS[(self.pid - 1) % N].condition.release()

    @socketio.on('update')
    def thinking(self):
        self.status = 'Thinking'
        checking.release()
        thinking_time = Radom.uniform(2.5, 3.5)
        t_data = { 'pid': self.pid, 
                'pishes eaten': self.dishes_eaten,
                'status': self.status,
                'remaining time': thinking_time}
        
        socketio.emit('update', t_data)
        print(t_data)

        # print({ 'Pid': self.pid, 
        #         'Dishes eaten': self.dishes_eaten,
        #         'Status': self.status,
        #         'Remaining time': thinking_time})
        #print(f'Philosopher {self.pid} started thinking')
        sleep(thinking_time)

    def hungry(self):
        checking.acquire()
        self.status = 'Hungry'
        h_data = { 'pid': self.pid, 
                'dishes eaten': self.dishes_eaten,
                'status': self.status,
                'remaining time': 0}
        socketio.emit('update', h_data)
        checking.release()

    def __check_forks(self):
        checking.acquire()
        if PHILOSOPHERS[(self.pid + 1) % N].status == "Eating" or \
             PHILOSOPHERS[(self.pid - 1) % N].status == "Eating":
             checking.release()
             return False
        
        if PHILOSOPHERS[(self.pid + 1) % N].status == "Hungry" and \
            PHILOSOPHERS[(self.pid + 1) % N].dishes_eaten < self.dishes_eaten:
            PHILOSOPHERS[(self.pid + 1) % N].condition.acquire()
            PHILOSOPHERS[(self.pid + 1) % N].condition.notify()
            PHILOSOPHERS[(self.pid + 1) % N].condition.release()
            checking.release()
            return False

        if PHILOSOPHERS[(self.pid - 1) % N].status == "Hungry" and \
            PHILOSOPHERS[(self.pid - 1) % N].dishes_eaten < self.dishes_eaten:
            PHILOSOPHERS[(self.pid - 1) % N].condition.acquire()
            PHILOSOPHERS[(self.pid - 1) % N].condition.notify()
            PHILOSOPHERS[(self.pid - 1) % N].condition.release()
            checking.release()
            return False

        return True

@socketio.on('run')
def initilizer():
    print('stared main')
    global PHILOSOPHERS, N
    PHILOSOPHERS  = [Philosopher(i) for i in range(N)]

    for x in PHILOSOPHERS:
        x.start()



if __name__ == '__main__':
    socketio.run(app)
