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
        ended = len(self.ready_processes) == 0 and len(self.blocked_processes) == 0
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
        self.lock.acquire()
        self.blocked_processes[process] = self.cpu_clock + time
        process.update_using_device(device)
        self.lock.release()

    def unblock_process(self, process: Process) -> None:
        self.lock.acquire()
        self.blocked_processes.pop(process)
        self.ready_processes.append(process)
        process.update_using_device()
        self.lock.release()

    def scheduler(self) -> None:
        while not self.kill:
            if len(self.ready_processes) > 0:
                cycle_output = ""
                cycle_output += OUTPUT_CYCLE_SEPARATOR + "\n"
                cycle_output += f"CPU Clock: {self.cpu_clock} u.t." + "\n"

                cycle_output += "\nReady processes:" + "\n"
                self.lock.acquire()
                for process in self.ready_processes:
                    cycle_output += f" - {process.PID}, Remaining time: {process.operating_time} u.t." + "\n"
                if len(self.ready_processes) == 0:
                    cycle_output += " - None" + "\n"
                self.lock.release()

                cycle_output += "\nBlocked processes:" + "\n"
                self.lock.acquire()
                for process, time_of_unblocking in copy(self.blocked_processes).items():
                    process.lock.acquire()
                    cycle_output += f" - {process.PID}, Remaining time: {process.operating_time} u.t., Unblocking time: {time_of_unblocking}{f', Device in use: {process.using_device.name}' if type(process.using_device) == Device else ''}" + "\n"
                    process.lock.release()
                if len(self.blocked_processes) == 0:
                    cycle_output += " - None" + "\n"
                self.lock.release()

                process: Process = self.ready_processes.pop(0)
                cycle_output += f"\nRunning process: {process.PID}" + "\n"
                cycle_output += f"Remaining time: {process.operating_time} u.t." + "\n"

                will_use_device = random.randint(0, 100) <= process.probability_of_executing_a_device
                chosen_device: Device = random.choice(self.devices) if will_use_device else None

                time_of_fraction_to_use_device = random.randint(1, self.cpu_fraction) if will_use_device else 0

                time_of_execution = time_of_fraction_to_use_device-1 if will_use_device else self.cpu_fraction

                time_of_its_fraction_used_by_the_process = process.reduce_operating_time(time_of_execution)
                self.update_clock(time_of_its_fraction_used_by_the_process)

                if will_use_device and not process.ended():
                    chosen_device.add_request(process)
                    self.block_process(process, chosen_device.operating_time, chosen_device)

                if process.ended():
                    self.finished_processes[process] = self.cpu_clock
                
                if process not in self.blocked_processes and not process.ended():    
                    self.lock.acquire()
                    self.ready_processes.append(process)
                    self.lock.release()

                cycle_output += "\nDevices:" + "\n"

                device: Device
                for device in self.devices:
                    cycle_output += f" - {device.name}, Requests: {len(device.requests)}" + "\n"
                    if len(device.requests) > 0:
                        request: Process
                        for request in device.requests:
                            cycle_output += f"    - {request.PID}, Unblocking time: {self.blocked_processes[request]}" + "\n"

                print(cycle_output.rstrip())
                
            else: # No ready processes, so we wait for a process to be unblocked
                if (time() - self.last_clock_update) > .5:
                    if self.all_processes_ended():
                        self.kill = True
                    self.update_clock(1)
        
        print(OUTPUT_CYCLE_SEPARATOR)
        for process, time_when_finished in self.finished_processes.items():
            print(f"{process.PID} finished at {time_when_finished} u.t.")
        print(OUTPUT_CYCLE_SEPARATOR)

        self.disconnect_devices()
        sys.exit()

    def disconnect_devices(self) -> None:
        device: Device
        for device in self.devices:
            device.disconnect()
        print("All devices disconnected.")

    def run(self) -> None:
        threads = []

        device: Device
        for device in self.devices:
            threads.append(threading.Thread(target=device.run))

        thread = threading.Thread(target=self.check_blocked_processes)
        threads.append(thread)

        thread = threading.Thread(target=self.scheduler)
        threads.append(thread)

        thread: threading.Thread
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()
