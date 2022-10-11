from time import sleep
from threading import Thread
from classes.processo import Processo

# ========================================================================= #
#                                                                           #
#     Constantes que podem ser ajustadas manualmente, caso necessário       #
#                                                                           #
# ========================================================================= #
DELAY = 0.0005  # Tempo de delay entre cada iteração do algoritmo de escalona-
# mento, para que haja tempo do usuário introduzir novos processos enquanto
# o algoritmo de escalonamento executa.

# ========================================================================= #
#                                                                           #
#          Variáveis globais que serão manipuladas pelas funções            #
#                                                                           #
# ========================================================================= #
arquivo_entrada = ''  # Guarda o nome do arquivo de entrada para ser usado na
# criação do nome do arquivo de log.
algoritmo_escalonamento = ''  # Armazena o nome do algoritmo de escalonamento
# dado pelo arquivo de entrada.
estrutura_de_dados = []  # Lista que armazenará os processos a serem escalona-
# dos e que receberá novos processos introduzidos pela thread_teclado.
processos_concluidos = 0  # Contador de processos concluídos.
fracao_cpu = 0  # Fração de "tempo" de CPU que o processo terá para executar.
# É dada pelo arquivo de entrada.
iteracoes = 0  # Contador de iterações que será utilizado para o log de execu-
# ção dos processos e que será incrementado a cada iteração do loop principal
# do algoritmo de escalonamento (ou seja, enquanto houverem processos a serem
# executados).
escalonador_acabou = False  # Servirá para saber até quando poderão ser adicio-
# nados novos processos na estrutura_de_dados, enquanto algum algoritmo de es-
# calonamento estiver sendo executado.


# ========================================================================= #
#                                                                           #
#     Algoritmo de escalonamento de processos por alternância circular      #
#                                                                           #
# ========================================================================= #
def alternanciaCircular():
    global estrutura_de_dados
    global fracao_cpu
    global processos_concluidos
    global iteracoes
    global arquivo_entrada
    with open(f'log-{arquivo_entrada}.txt', 'w') as log:
        while len(estrutura_de_dados) > 0:
            iteracoes += 1
            processo = estrutura_de_dados.pop(0)
            processo.reduz_tempo_execucao(fracao_cpu)
            if processo.tempo_execucao > 0:
                estrutura_de_dados.append(processo)
            else:
                log.write(
                    f"processo {processo.nome} finalizado em " +
                    f"{tempo_executado(processo.tempo_execucao)} " +
                    f"microssegundos.\n")
                processos_concluidos += 1
            sleep(DELAY)
    return


def tempo_executado(tempo_execucao: int) -> int:
    """
    Calcula o tempo de execução de um processo.
    """
    global iteracoes
    global fracao_cpu
    return (iteracoes * fracao_cpu) + tempo_execucao

# ========================================================================= #
#                                                                           #
#     Escalonador de processos, que recebe o arquivo de entrada,            #
#     seta algumas variáveis globais e chama a função de escalonamento      #
#     apropriada, conforme estabelecido no arquivo. (Também é a thread      #
#     principal).                                                           #
#                                                                           #
# ========================================================================= #


def escalonar(nome_arquivo: str):
    global escalonador_acabou
    global algoritmo_escalonamento
    global estrutura_de_dados
    global fracao_cpu
    global processos_concluidos
    try:
        with open(nome_arquivo, 'r') as arquivo:
            cabecalho = arquivo.readline().split('|')
            algoritmo_escalonamento = str(cabecalho[0])
            fracao_cpu = int(cabecalho[1])
            while linha := arquivo.readline():
                linha = linha.strip()
                linha = linha.split('|')
                estrutura_de_dados.append(
                    Processo(
                        nome=linha[0],
                        PID=int(linha[1]),
                        tempo_execucao=int(linha[2]),
                        prioridade=int(linha[3]),
                        UID=int(linha[4]),
                        quantidade_de_memoria=int(linha[5])
                    )
                )
            match algoritmo_escalonamento:
                case 'alternanciaCircular':
                    alternanciaCircular()
                case _:
                    print('Algoritmo de escalonamento não reconhecido.')
                    main()
    except FileNotFoundError:
        print("ERRO: arquivo de texto não encontrado.")
        escalonador_acabou = True
        quit
    print(f'Foram concluídos {processos_concluidos} processos.')
    print("Digite qualquer coisa para finalizar a execução do programa!")
    escalonador_acabou = True
    return


# ========================================================================= #
#                                                                           #
#     Função principal que ativa as threads e faz a leitura do arquivo      #
#     de processos a serem escalonados.                                     #
#                                                                           #
# ========================================================================= #
def main():
    thread_principal = None

    print("Bem vindo! Escreva qual função e qual arquivo você quer escalonar.\n" +
          "Escreva 'escalonar' e o nome do arquivo.")
    entrada = input().split(' ')
    if ((comando := entrada[0] == 'escalonar') and
            (nome_arquivo := entrada[1]).endswith('.txt')):
        global arquivo_entrada
        arquivo_entrada = nome_arquivo[:-4]
        thread_principal = Thread(target=escalonar, args=(nome_arquivo,))
    else:
        print('Comando não reconhecido')
        return -1

    thread_principal.start()
    thread_principal.join()


if __name__ == '__main__':
    main()
