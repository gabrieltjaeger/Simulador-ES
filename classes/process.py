import threading
from time import sleep

from .consts import DELAY
from .device import Device


class Process:
    def __init__(self, PID: str, operating_time: int, probability_of_executing_a_device: int) -> None:
        self.PID = PID
        self.operating_time = operating_time
        self.probability_of_executing_a_device = probability_of_executing_a_device
        self.lock = threading.Lock()
        self.using_device: Device = None

    def update_using_device(self, device: Device = None) -> None:
        self.lock.acquire()
        if device is None:
            self.using_device.lock.acquire()
            self.using_device.processes_using.remove(self)
            self.using_device.lock.release()
        self.using_device = device
        self.lock.release()

    def __str__(self) -> str:
        return f"{self.PID}|{self.operating_time}|{self.probability_of_executing_a_device}"

    def __repr__(self) -> str:
        return self.__str__()

    def reduce_operating_time(self, cpu_fraction: int) -> int:
        used_time = 0
        while cpu_fraction > 0 and not self.ended():
            self.operating_time -= 1
            cpu_fraction -= 1
            used_time += 1
            sleep(DELAY)
        return used_time

    def ended(self) -> bool:
        return self.operating_time <= 0
