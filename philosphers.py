import threading
import random as Radom
from time import sleep
import sys
#from app import socketio

# AVALIABLE_STATES = ['Thinking','Hungry','Eating']
PHILOSOPHERS = []
checking = threading.Lock() # Mutex ogólny
N = 5 if sys.argv[0] else sys.argv[0]

class Philosopher(threading.Thread):

    def __init__(self, pid):
        super().__init__(target=self.foo)
        self.pid = pid
        self.dishes_eaten = 0
        self.status = "Thinking"
        self.condition = threading.Condition()
        print("Philosopher created!")
        
    def __str__(self):
        print({ 'Pid': self.pid, 
                'Dishes eaten': self.dishes_eaten,
                'Status': self.status})

    def foo(self):
        self.condition.acquire()
        while True:
            self.__hungry()
            while not self.__check_forks():
                self.condition.wait()
            self.__eating()
            self.__thinking()

    def __eating(self):
        self.status = 'Eating'
        checking.release()
        eating_time = Radom.uniform(2.5, 3.5)
        #print(f'Philosopher {self.pid} started eating')
        # print({ 'Pid': self.pid, 
        #         'Dishes eaten': self.dishes_eaten,
        #         'Status': self.status,
        #         'Remaining time': eating_time})
        print(self)
        #emit('update status', )
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

    def __thinking(self):
        self.status = 'Thinking'
        checking.release()
        thinking_time = Radom.uniform(2.5, 3.5)
        print(self.__str__())
        # print('update', { 'Pid': self.pid, 
        #         'Dishes eaten': self.dishes_eaten,
        #         'Status': self.status,
        #         'Remaining time': thinking_time})

        # print({ 'Pid': self.pid, 
        #         'Dishes eaten': self.dishes_eaten,
        #         'Status': self.status,
        #         'Remaining time': thinking_time})
        #print(f'Philosopher {self.pid} started thinking')
        sleep(thinking_time)

    def __hungry(self):
        checking.acquire()
        self.status = 'Hungry'
        print({ 'Pid': self.pid, 
                'Dishes eaten': self.dishes_eaten,
                'Status': self.status,
                'Remaining time': 0})
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


# class Display:
    
#     def __init__(self):
#         self.min_window_res=(160,90)
#         self.current_res = (160,90)
#         self.window = curses.initscr()

#     def get_window_resolution(self):
#         return self.window.getmaxyx()

#     def refresh_window(self):
#         while(True):
#             if (lambda x: )

#     def keyboard_listener(self):
#         ch = self.window.getch()
#         if ch == '\n':
#             return True
#         else:
#             return False

#     def display_window(self):
#         pass

# @socketio.on('run')
def main():
    print('stared main')
    global PHILOSOPHERS, N
    PHILOSOPHERS  = [Philosopher(i) for i in range(N)]

    for x in PHILOSOPHERS:
        x.start()
    
if __name__ == '__main__':
    main()