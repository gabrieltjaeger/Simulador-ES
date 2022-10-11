# le arquivo
# quantos dispositivos vai ter 
# associar threads com dispositivos
# criar os dispositivos

# threads que representam os dispositivos
# cada dispositivo tem uma fila de requisições
# semaforo para cada dispositivo para controlar o acesso a fila
# while True: (thread de cada dispositivo)
#    espera que tenha requisicao
#    chegou algo na fila, executa a requisicao pela fatia de tempo
#    mudar o processo para a lista de processos prontos
#

# tabela de processos
# estado inicial dos processos pronto
# lista de processos bloqueados e lista de processos prontos
# escalonador roda os prontos

# escalonar()
#    pega processo da lista de prontos
#    verifica se tem requisicao de uso de dispositivo
#    se tiver, sorteia um dispositivo
#       ver em qual momento do tempo de execucao do processo sera usado o dispositivo (sorteio)
#       fazer operacao de entrada/saida
#    se nao tiver, executa o processo
#    
# executa

# relogio global da cpu
# thread que fica analisando os processos com o tempo do relógio para saber quais desbloquear


import threading

class Process:
    def __init__(self, PID: str, operating_time: int, probability_of_execution: int):
        self.PID = PID
        self.operating_time = operating_time
        self.probability_of_execution = probability_of_execution
        
    def __str__(self):
        return f"{self.PID} has {self.operating_time} of operating time left. It has a probability of executing a device of {self.probability_of_execution}."

    def __repr__(self):
        return self.__str__()

    def reduce_operating_time(self, cpu_fraction: int):
        self.operating_time -= cpu_fraction

    def ended(self):
        return self.operating_time <= 0


class Device:
    def __init__(self, name, quantity, operating_time):
        self.name = name
        self.quantity = quantity
        self.operating_time = operating_time # controls wether the calling process will be blocked or ready to run
        self.requests = []
        self.semaphore = threading.Semaphore(quantity)

    def __str__(self):
        return f"{self.name} can be used {self.quantity} times simultaneously and has {self.operating_time} of operating time."

    def __repr__(self):
        return self.__str__()

    def add_request(self, request: Process):
        self.requests.append(request)

    def run(self): # sera executado em uma thread
        while True:
            self.semaphore.acquire()
            if len(self.requests) > 0:
                request = self.requests.pop(0)
                print(f"Executing {request} on device {self.name}")
                self.semaphore.release()
            else:
                self.semaphore.release()



def main():
    devices = []
    processes = []
    cpu_fraction = 0
    '''
    Exemplo de entrada
    10|4
    device-0|1|3
    device-1|2|5
    device-2|2|2
    device-3|1|6
    processo-0|4|32
    processo-1|24|12
    processo-2|32|88
    processo-3|16|23
    processo-4|4|50
    '''
    with open("./entrada/entrada_es.txt", "r") as file:
        cpu_fraction, qnt_devices = file.readline().strip().split("|")
        cpu_fraction = int(cpu_fraction)
        qnt_devices = int(qnt_devices)
        for i in range(qnt_devices):
            name, simultaneous_access, operating_time = file.readline().strip().split("|")
            devices.append(Device(name, int(simultaneous_access), int(operating_time)))
        for line in file:
            PID, operating_time, probability_of_execution = line.strip().split("|")
            processes.append(Process(PID, int(operating_time), int(probability_of_execution)))

    for device in devices:
        print(device)

    for process in processes:
        print(process)
        
    print(cpu_fraction)

if __name__ == "__main__":
    main()