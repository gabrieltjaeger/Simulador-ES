from classes.device import Device
from classes.os import OperatingSystem
from classes.process import Process


def main():
    devices = []
    processes = []
    cpu_fraction = 0

    with open("./entrada/entrada_es.txt", "r") as file:
        cpu_fraction, qnt_devices = file.readline().strip().split("|")
        cpu_fraction = int(cpu_fraction)
        qnt_devices = int(qnt_devices)

        for i in range(qnt_devices):
            name, simultaneous_access, operating_time = file.readline().strip().split("|")
            devices.append(
                Device(name, int(simultaneous_access),
                       int(operating_time))
            )
            
        for line in file:
            PID, operating_time, probability_of_executing_a_device = line.strip().split("|")
            processes.append(
                Process(PID, int(operating_time),
                        int(probability_of_executing_a_device))
            )

    os = OperatingSystem(processes, devices, cpu_fraction)
    os.run()


if __name__ == "__main__":
    main()
