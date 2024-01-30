import socket
import sys
from mininet.node import Host
from mininet.net import Mininet

def iniciar_eleicao_anel(host):
    # Implementação do algoritmo de eleição do anel
    local_ip = socket.gethostbyname(host)
    local_port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((local_ip, local_port))
        server_socket.listen()

        print(f'{host} - Aguardando conexão para eleição...')

        try:
            # Tenta aceitar conexões de outros hosts
            with server_socket.accept()[0] as client_socket:
                print(f'{host} - Iniciando eleição...')

                # Obtenha dinamicamente os IDs dos hosts na rede Mininet
                all_hosts = [h.name for h in Mininet().hosts]
                host_ids = [int(h[1:]) for h in all_hosts]

                # Realize a eleição aqui (por exemplo, baseado em IDs)
                elected_leader = max([host] + all_hosts, key=lambda h: int(h[1:]))

                print(f'{host} - Novo líder: {elected_leader}')

                # Informa aos outros hosts sobre o novo líder
                client_socket.sendall(elected_leader.encode())
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    current_host = sys.argv[1] if len(sys.argv) > 1 else None

    if not current_host:
        print("Erro: Identificação do host não fornecida.")
        sys.exit(1)

    print(f'{current_host} - Iniciando eleição do anel...')
    iniciar_eleicao_anel(current_host)
