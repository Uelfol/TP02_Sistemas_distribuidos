from mininet.topo import Topo
from mininet.node import Node
from mininet.net import Mininet
from mininet.log import setLogLevel, info
import threading
import time
import random
import os
from queue import Queue

first_iteration = True  # Variável global para controlar a primeira iteração

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

def request_file(host, access_queue, coordinator_lock, coordinator_timer):
    global first_iteration

    while True:
        time.sleep(random.uniform(1, 5))  # Solicitações aleatórias

        # Verifica se o host ainda está conectado à rede
        if host not in connected_hosts:
            continue

        print(f"{host.name} solicita acesso ao arquivo")

        # Adiciona o host à fila de solicitações
        access_queue.put(host)

        # Imprime a fila
        print("Fila:", list(access_queue.queue))

        # Aguarda até que seja a vez do host acessar o arquivo
        while access_queue.queue[0] != host:
            time.sleep(1)

        # Verifica se o host ainda está conectado à rede
        if host not in connected_hosts:
            access_queue.get()  # Remove da fila se desconectado
            continue

        access_file(host, coordinator_lock, coordinator_timer)
        first_iteration = False

        # Remove o host da fila após acessar o arquivo
        access_queue.get()

def access_file(host, coordinator_lock, coordinator_timer):
    global current_coordinator
    global first_iteration

    with coordinator_lock:
        if first_iteration:
            print("Iniciando eleição de coordenador.")
            choose_new_coordinator()

        # Verifica se o coordenador ainda está conectado
        if current_coordinator not in connected_hosts:
            print(f"Coordenador {current_coordinator.name} caiu. Iniciando escolha de novo coordenador.")
            choose_new_coordinator()

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

        # Inicia o temporizador para desconectar o coordenador após 15 segundos
        coordinator_timer = threading.Timer(15, disconnect_coordinator, args=(current_coordinator, coordinator_lock))
        coordinator_timer.start()

def disconnect_coordinator(host, coordinator_lock):
    global connected_hosts
    with coordinator_lock:
        if host in connected_hosts:
            connected_hosts.remove(host)
            print(f"{host.name} foi desconectado da rede.")

def choose_new_coordinator():
    global current_coordinator
    new_coordinator = min(connected_hosts, key=lambda h: h.name)
    print(f"{new_coordinator.name} se tornou o novo coordenador.")
    current_coordinator = new_coordinator

def run():
    topo = MyTopo()
    net = Mininet(topo=topo)
    net.start()

    # Inicializando variáveis compartilhadas
    global current_coordinator
    global connected_hosts
    global first_iteration
    current_coordinator = None
    coordinator_lock = threading.Lock()
    access_queue = Queue()
    coordinator_timer = None
    connected_hosts = set(net.hosts)

    # Criando threads para solicitação de arquivo
    request_threads = []
    for host in net.hosts:
        thread = threading.Thread(target=request_file, args=(host, access_queue, coordinator_lock, coordinator_timer))
        thread.start()
        request_threads.append(thread)

    # Aguarda as threads terminarem
    for thread in request_threads:
        thread.join()

if __name__ == '__main__':
    setLogLevel('info')
    run()

