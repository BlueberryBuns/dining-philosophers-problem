import threading
import random as Radom
from time import sleep

# AVALIABLE_STATES = ['Thinking','Hungry','Eating']
PHILOSOPHERS = []
checking = threading.Lock() # Mutex ogólny
N = 5

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
            self.__hungry()
            while not self.__check_forks():
                self.condition.wait()
            self.__eating()
            self.__thinking()

    def __eating(self):
        self.status = 'Eating'
        checking.release()
        print(f'Philosopher {self.pid} started eating')
        sleep(Radom.uniform(2.5, 3.5))
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
        print(f'Philosopher {self.pid} started thinking')
        sleep(Radom.uniform(2.5, 3.5))

    def __hungry(self):
        checking.acquire()
        self.status = 'Hungry'
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


def main():
    global PHILOSOPHERS, N
    PHILOSOPHERS  = [Philosopher(i) for i in range(N)]

    for x in PHILOSOPHERS:
        x.start()

if __name__ == '__main__':
    main()