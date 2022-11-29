import sys
import threading


class Device:
    def __init__(self, name: str, quantity: int, operating_time: int) -> None:
        self.name = name
        self.quantity = quantity
        self.operating_time = operating_time
        self.requests = []
        self.processes_using = []
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(quantity)
        self.kill = False

    def __str__(self) -> str:
        return f"{self.name}|{self.quantity}|{self.operating_time}"

    def __repr__(self) -> str:
        return self.__str__()

    def add_request(self, request) -> None:
        self.lock.acquire()
        self.requests.append(request)
        self.lock.release()

    def get_request(self):
        self.lock.acquire()
        request = self.requests.pop(0)
        self.lock.release()
        return request

    def update_processes_using(self, process = None) -> None:
        self.lock.acquire()
        if process is None:
            self.processes_using.pop(0)
        else:
            self.processes_using.append(process)
        self.lock.release()

    def run(self) -> None:
        while not self.kill:
            self.lock.acquire()
            if len(self.processes_using) >= self.quantity:
                self.lock.release()
                continue
            self.lock.release()
            if len(self.requests) > 0:
                request = self.get_request()
                self.update_processes_using(request)
        sys.exit()

    def disconnect(self) -> None:
        self.kill = True
