from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import threading
import random as Radom
from time import sleep
import json
import numpy as np
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = '248889'
socketio = SocketIO(app)
app_started = False
PHILOSOPHERS = []
FORKS = []
checking = threading.Lock()
N = 5


class Waiter():
    def __init__(self):
        pass

    def ask(self, philosopher):
        if PHILOSOPHERS[(philosopher.pid + 1) % N].status == "Hungry" and \
            PHILOSOPHERS[(philosopher.pid + 1) % N].dishes_eaten < philosopher.dishes_eaten:
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.acquire()
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.notify()
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.release()
            checking.release()
            return False

        if PHILOSOPHERS[(philosopher.pid - 1) % N].status == "Hungry" and \
            PHILOSOPHERS[(philosopher.pid - 1) % N].dishes_eaten < philosopher.dishes_eaten:
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.acquire()
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.notify()
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.release()
            checking.release()
            return False

        return True

    def inform(self, philosopher):
        if PHILOSOPHERS[(philosopher.pid + 1) % N].status == "Hungry":
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.acquire()
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.notify()
            PHILOSOPHERS[(philosopher.pid + 1) % N].condition.release()
        if PHILOSOPHERS[(philosopher.pid- 1) % N].status == "Hungry":
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.acquire()
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.notify()
            PHILOSOPHERS[(philosopher.pid - 1) % N].condition.release()


waiter = Waiter()


class Fork():
    def __init__(self, philosopher):
        self.number = philosopher.pid
        self.current_owner = None
        self.state = "free"
        self.forkstatus = "Free"

    def take(self, philosopher):
        self.current_owner = philosopher
        self.state = "taken"
        self.forkstatus = f"Taken by philosopher {philosopher.pid}"

    def put_down(self):
        self.current_owner = None
        self.state = "free"
        self.forkstatus = "Free"


def ack():
    print('message received')

@socketio.on('philosophers')
def run_philosophers(data):
    emit('philosophers', callback=ack)

@socketio.on('connection')
def connected(json):
    global app_started, N
    if (not app_started) and True:
        print('working')
        app_started = True
        emit('initialize', {'data': N})
    print(json['data'])

@socketio.on('philosphers')
def update(json):
    emit('update', json)

@app.route('/')
def philosophers():
    return render_template('index.html', context={'philosophers': PHILOSOPHERS, 'forks': FORKS})

class Philosopher(threading.Thread):

    def __init__(self, pid):
        super().__init__(target=self.foo)
        self.pid = pid
        self.dishes_eaten = 0
        self.status = "Thinking"
        self.condition = threading.Condition()
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
        FORKS[self.pid].take(self)
        FORKS[(self.pid+1)%N].take(self)
        checking.release()
        eating_time = Radom.uniform(2.5, 3.5)
        #print(f'Philosopher {self.pid} started eating')
        e_data = { 'pid': self.pid, 
                'dishes': self.dishes_eaten,
                'status': self.status,
                'time': eating_time,
                'right': (self.pid+1)%N,
                'lefts': FORKS[self.pid].forkstatus,
                'rights': FORKS[(self.pid+1)%N].forkstatus,
                }
        print(e_data)
        socketio.emit('update', e_data)
        sleep(eating_time)
        checking.acquire()
        self.dishes_eaten += 1
        FORKS[(self.pid % N)].put_down()
        FORKS[(self.pid+1) % N].put_down()

        waiter.inform(self)
        
        # if PHILOSOPHERS[(self.pid + 1) % N].status == "Hungry":
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.acquire()
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.notify()
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.release()
        # if PHILOSOPHERS[(self.pid - 1) % N].status == "Hungry":
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.acquire()
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.notify()
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.release()

    @socketio.on('update')
    def thinking(self):
        self.status = 'Thinking'
        checking.release()
        thinking_time = Radom.uniform(2.5, 3.5)
        t_data = { 'pid': self.pid, 
                'dishes': self.dishes_eaten,
                'status': self.status,
                'time': thinking_time,
                'right': (self.pid+1)%N,
                'lefts': FORKS[self.pid].forkstatus,
                'rights': FORKS[(self.pid+1)%N].forkstatus,}
        
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
                'dishes': self.dishes_eaten,
                'status': self.status,
                'time': 0,
                'right': (self.pid+1)%N,
                'lefts': FORKS[self.pid].forkstatus,
                'rights': FORKS[(self.pid+1)%N].forkstatus
                }
        socketio.emit('update', h_data)
        checking.release()

    def __check_forks(self):
        checking.acquire()
        print(FORKS[self.pid].state)
        if FORKS[(self.pid) % N].state == "taken" or \
             FORKS[(self.pid + 1) % N].state == "taken":
             checking.release()
             return False
        
        return waiter.ask(self)
        # if PHILOSOPHERS[(self.pid + 1) % N].status == "Hungry" and \
        #     PHILOSOPHERS[(self.pid + 1) % N].dishes_eaten < self.dishes_eaten:
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.acquire()
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.notify()
        #     PHILOSOPHERS[(self.pid + 1) % N].condition.release()
        #     checking.release()
        #     return False

        # if PHILOSOPHERS[(self.pid - 1) % N].status == "Hungry" and \
        #     PHILOSOPHERS[(self.pid - 1) % N].dishes_eaten < self.dishes_eaten:
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.acquire()
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.notify()
        #     PHILOSOPHERS[(self.pid - 1) % N].condition.release()
        #     checking.release()
        #     return False

@socketio.on('run')
def initilizer():
    print('stared main')
    global PHILOSOPHERS, N, FORKS, waiter
    PHILOSOPHERS  = [Philosopher(i) for i in range(N)]
    FORKS = [Fork(i) for i in PHILOSOPHERS]

    for x in PHILOSOPHERS:
        x.start()

def main(a):
    global N
    N = (lambda x: int(x[1]) if len(x) > 1 else 5)(a)
    socketio.run(app)

if __name__ == '__main__':
    main(sys.argv)

