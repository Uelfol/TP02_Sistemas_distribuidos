from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController
from threading import Thread
from exclusao_mutua import ExclusaoMutua, iniciar_eleicao_anel
import socket
import time

class CustomTopology(Topo):
    def build(self):
        # Adicione quatro hosts
        h1 = self.addHost('h1')
        h2 = this.addHost('h2')
        h3 = this.addHost('h3')
        h4 = this.addHost('h4')

        # Adicione dois switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Conecte os hosts aos switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

        # Conecte os switches entre si
        self.addLink(s1, s2)

if __name__ == '__main__':
    topo = CustomTopology()
    net = Mininet(topo=topo, controller=lambda name: RemoteController(name, ip='127.0.0.1'))
    net.start()

    # Escolha um líder inicial (h1) e salve sua identificação em um arquivo compartilhado
    initial_leader = net.get('h1')
    leader_id_file = '/tmp/leader_id.txt'
    with open(leader_id_file, 'w') as file:
        file.write(initial_leader.name)

    # Associe os scripts Python aos hosts
    for host in net.hosts:
        leader_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        leader_socket.connect(('127.0.0.1', 12345))  # Substitua pelo IP e porta do líder

        exclusao_mutua_obj = ExclusaoMutua(host.name, leader_socket)

        # Iniciar thread para monitorar o líder
        monitor_thread = Thread(target=exclusao_mutua_obj.monitorar_lider)
        monitor_thread.start()

        # Executar o algoritmo de exclusão mútua
        host.cmd(f'python exclusao_mutua.py {host.name} &')

    # Inicie o algoritmo de eleição do anel no líder
    initial_leader.cmd(f'python eleicao_anel.py {initial_leader.name} &')

    CLI(net)
    net.stop()
