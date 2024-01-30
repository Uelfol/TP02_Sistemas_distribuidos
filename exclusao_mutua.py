import socket
import sys
import time
from threading import Lock, Thread, Condition
from eleicao_anel import iniciar_eleicao_anel

class ExclusaoMutua:
    def __init__(self, host, leader_socket):
        self.host = host
        self.leader_socket = leader_socket
        self.mutex = Lock()
        self.condition = Condition(self.mutex)
        self.queue = []
        self.diretorio_compartilhado = "/tmp"

    def entrar_fila(self):
        with self.mutex:
            self.queue.append(self.host)
            print(f'{self.host} - Adicionado à fila de exclusão mútua: {self.queue}')

    def sair_fila(self):
        with self.mutex:
            if self.queue:
                self.queue.pop(0)
            print(f'{self.host} - Removido da fila de exclusão mútua: {self.queue}')
            self.condition.notify()

    def aguardar_vez(self):
        with self.condition:
            while self.queue and self.queue[0] != self.host:
                self.condition.wait()

    def exclusao_mutua(self):
        while True:
            self.entrar_fila()
            self.aguardar_vez()

            with self.mutex:
                print(f'{self.host} - Acessando a seção crítica...')

                # Seção crítica (área de acesso ao recurso compartilhado)
                with open(f'{self.diretorio_compartilhado}/arquivo_compartilhado.txt', 'a') as file:
                    file.write(f'{self.host} - Timestamp: {time.time()}\n')

                time.sleep(1)

            self.sair_fila()
            time.sleep(1)

    def monitorar_lider(self):
        while True:
            try:
                self.leader_socket.send(b'ping')
            except socket.error:
                print(f'{self.host} - Líder desconectado! Iniciando eleição...')
                self.leader_socket.close()
                self.leader_socket = iniciar_eleicao_anel(self.host)


if __name__ == '__main__':
    current_host = sys.argv[1] if len(sys.argv) > 1 else None

    if not current_host:
        print("Erro: Identificação do host não fornecida.")
        sys.exit(1)

    leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    leader_socket.connect(('127.0.0.1', 12345))  # Substitua pelo IP e porta do líder

    exclusao_mutua_obj = ExclusaoMutua(current_host, leader_socket)

    # Iniciar thread para monitorar o líder
    monitor_thread = Thread(target=exclusao_mutua_obj.monitorar_lider)
    monitor_thread.start()

    # Executar o algoritmo de exclusão mútua
    exclusao_mutua_obj.exclusao_mutua()
