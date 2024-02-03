from mininet.topo import Topo
from mininet.node import Node
from mininet.net import Mininet
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import threading
import time
import random
import os
from queue import Queue

class MyTopo(Topo):
    def build(self, **_opts):
        h1 = self.addHost('h1', ip='192.168.0.1/24')
        h2 = self.addHost('h2', ip='192.168.0.2/24')
        h3 = self.addHost('h3', ip='192.168.0.3/24')
        h4 = self.addHost('h4', ip='192.168.0.4/24')
        s1 = self.addSwitch("s1")
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)
        self.addLink(h4, s1)

def request_file(host, access_queue, coordinator_lock):
    while True:
        time.sleep(random.uniform(1, 5))  # Solicitações aleatórias
        print(f"{host.name} solicita acesso ao arquivo")

        # Adiciona o host à fila de solicitações
        access_queue.put(host)

        # Imprime a fila
        print("Fila:", list(access_queue.queue))

        # Aguarda até que seja a vez do host acessar o arquivo
        while access_queue.queue[0] != host:
            time.sleep(1)

        access_file(host, coordinator_lock)

        # Remove o host da fila após acessar o arquivo
        access_queue.get()

def access_file(host, coordinator_lock):
    global current_coordinator
    with coordinator_lock:
        # Algoritmo de eleição do anel
        if current_coordinator is None or host.name < current_coordinator:
            current_coordinator = host.name
            print(f"{host.name} se tornou o coordenador (ID: {host.name})")

        # Imprime a mensagem de acesso ao arquivo
        print(f"{host.name} acessou o arquivo")

        # Lista todos os arquivos na pasta compartilhada
        file_path = "./shared/"
        files = os.listdir(file_path)

        # Renomeia o primeiro arquivo encontrado na pasta compartilhada
        if files:
            selected_file = files[0]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            new_file_name = f"{host.name}_{timestamp}.txt"

            # Renomeia mantendo o conteúdo
            os.rename(f"{file_path}/{selected_file}", f"{file_path}/{new_file_name}")

            print(f"{host.name} renomeou o arquivo para {new_file_name}")

        # Aguarda um pouco antes de liberar o recurso
        time.sleep(random.uniform(1, 5))

def run():
    topo = MyTopo()
    net = Mininet(topo=topo)
    net.start()

    # Inicializando variáveis compartilhadas
    global current_coordinator
    current_coordinator = None
    coordinator_lock = threading.Lock()
    access_queue = Queue()

    # Criando um diretório compartilhado
    net.hosts[0].cmd('mkdir -p ./shared')
    # Criando um arquivo inicial na pasta compartilhada
    # net.hosts[0].cmd('echo "Conteúdo inicial do arquivo" > ./shared/initial_file.txt')

    # Inicializando threads para cada host para solicitações
    request_threads = []
    for host in net.hosts:
        thread = threading.Thread(target=request_file, args=(host, access_queue, coordinator_lock))
        request_threads.append(thread)
        thread.start()

    info("Starting\n")
    CLI(net)

    # Aguarda a conclusão de todas as threads antes de encerrar a rede
    for thread in request_threads:
        thread.join()

    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()

