import random
import sys
import threading
from copy import copy
from time import time

from .consts import OUTPUT_CYCLE_SEPARATOR
from .device import Device
from .process import Process


class OperatingSystem:
    def __init__(self, processes: list, devices: list, cpu_fraction: int) -> None:
        self.ready_processes = processes
        self.devices = devices
        self.cpu_fraction = cpu_fraction
        self.finished_processes = {}
        self.blocked_processes = {}
        self.lock = threading.Lock()
        self.semaphore = threading.Semaphore(1)
        self._cpu_clock = 0
        self.last_clock_update = 0
        self.kill = False

    def all_processes_ended(self) -> bool:
        self.semaphore.acquire()
        ended = len(self.ready_processes) == 0 and len(
            self.blocked_processes) == 0
        self.semaphore.release()
        return ended

    def check_blocked_processes(self) -> None:
        while not self.kill:
            process: Process
            for process, time in copy(self.blocked_processes).items():
                if (self.cpu_clock >= time):
                    self.unblock_process(process)
                    break
        sys.exit()

    @property
    def cpu_clock(self) -> int:
        self.semaphore.acquire()
        clock = self._cpu_clock
        self.semaphore.release()
        return clock

    @cpu_clock.setter
    def cpu_clock(self, value: int) -> None:
        self.lock.acquire()
        self._cpu_clock = value
        self.last_clock_update = time()
        self.lock.release()

    def update_clock(self, time: int) -> None:
        for _ in range(time):
            self.cpu_clock += 1

    def block_process(self, process: Process, time: int, device: Device) -> None:
        self.blocked_processes[process] = self.cpu_clock + time
        device.semaphore.acquire()
        device.add_request(process)
        process.update_using_device(device)

    def unblock_process(self, process: Process) -> None:
        self.lock.acquire()
        self.blocked_processes.pop(process)
        self.ready_processes.append(process)
        process.using_device.semaphore.release()
        process.update_using_device()
        self.lock.release()

    def output_ready_processes(self) -> str:
        output = "\nReady processes:" + "\n"
        self.lock.acquire()
        process: Process
        for process in self.ready_processes:
            output += f" - {process.PID}, Remaining time: {process.operating_time} u.t." + "\n"
        if len(self.ready_processes) == 0:
            output += " - None" + "\n"
        self.lock.release()
        return output

    def output_blocked_processes(self) -> str:
        output = "\nBlocked processes:" + "\n"
        self.lock.acquire()
        blocked_processes = copy(self.blocked_processes)
        process: Process
        for process, time_of_unblocking in blocked_processes.items():
            process.lock.acquire()
            output += f" - {process.PID}, Remaining time: {process.operating_time} u.t., Unblocking time: {time_of_unblocking}{f', Device in use: {process.using_device.name}' if type(process.using_device) == Device else ''}" + "\n"
            process.lock.release()
        if len(blocked_processes) == 0:
            output += " - None" + "\n"
        self.lock.release()
        return output

    def output_running_process(self) -> str:
        process: Process = self.ready_processes[0]
        return f"\nRunning process {process.PID}\nRemaining time: {process.operating_time} u.t.\n"

    def output_devices(self) -> str:
        output = "\nDevices:" + "\n"
        device: Device
        self.lock.acquire()
        for device in self.devices:
            output += f" - {device.name}, Requests: {len(device.processes_using)}/{device.quantity}" + "\n"
            if len(device.requests) > 0:
                request: Process
                for request in device.requests:
                    output += f"    - {request.PID}, Unblocking time: {self.blocked_processes[request]}" + "\n"
        self.lock.release()
        return output.rstrip()
    
    def scheduler(self) -> None:
        while not self.kill:
            if self.ready_processes:
                cycle_output: str = f"CPU Clock: {self.cpu_clock} u.t." + "\n"

                cycle_output += self.output_ready_processes()
                cycle_output += self.output_blocked_processes()
                cycle_output += self.output_running_process()

                process: Process = self.ready_processes.pop(0) # Chosen process is the first one in the list
                
                if process.will_use_device():
                    chosen_device: Device = random.choice(self.devices)
                    time_of_fraction_to_use_device = random.randint(1, self.cpu_fraction)
                    self.update_clock(process.reduce_operating_time(time_of_fraction_to_use_device-1))
                    if not process.ended():
                        self.block_process(process, chosen_device.operating_time, chosen_device)
                else:
                    self.update_clock(process.reduce_operating_time(self.cpu_fraction))

                cycle_output += f"\nCPU Clock: {self.cpu_clock} u.t." + "\n"

                if process.ended():
                    self.finished_processes[process] = self.cpu_clock
                else:
                    if process not in self.blocked_processes:
                        self.lock.acquire()
                        self.ready_processes.append(process)
                        self.lock.release()

                cycle_output += self.output_devices()

                print(cycle_output)
                print(OUTPUT_CYCLE_SEPARATOR)
                continue
            if (time() - self.last_clock_update) > .5:
                if self.all_processes_ended():
                    self.disconnect_devices()
                    self.kill = True
                self.update_clock(1)
        sys.exit()

    def disconnect_devices(self) -> None:
        device: Device
        for device in self.devices:
            device.disconnect()

    def run(self) -> None:
        threads = []

        device: Device
        for device in self.devices:
            threads.append(threading.Thread(target=device.run))

        thread = threading.Thread(target=self.check_blocked_processes)
        threads.append(thread)

        thread = threading.Thread(target=self.scheduler)
        threads.append(thread)

        print(OUTPUT_CYCLE_SEPARATOR)

        thread: threading.Thread
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        process: Process
        for process, time_when_finished in self.finished_processes.items():
            print(f"{process.PID} finished at {time_when_finished} u.t.")

        print(OUTPUT_CYCLE_SEPARATOR)
