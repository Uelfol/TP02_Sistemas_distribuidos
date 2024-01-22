import time
from random import randint
from threading import Thread

class Processos():
    def __init__(self, id):
        self.id = id
        self.tag = f'Processo {id}:'
        self.coordenador = None
        self.isAtivo = True
        Thread(target=self.rum_p).start()

    def rum_p(self):
        print(f'{self.tag} Inicializando!')
        while self.isAtivo:
            self.consumir_recurso()
            time.sleep(randint(10, 25))

    def set_coordenador(self, coordenador):
        self.coordenador = coordenador

    def set_ativo(self, ativo):
        self.isAtivo = ativo

    def stop(self):
        self.isAtivo = False

    def __repr__(self):
        return str(self.__dict__)

    def consumir_recurso(self):
        coordenador = self.coordenador
        if coordenador is None:
            Singleton().gere_novo_coordenador()
        elif coordenador is not None and self.id != coordenador.id:
            print('\n')
            print(f'{self.tag} Solicita acesso do recurso ao coordenador {coordenador.id}!')
            if not coordenador.isRecursoHabilitado:
                self.processa_recurso()
            else:
                coordenador.fila.append(self)
                print(f'******Fila do coordenador = {self.fila_coordenador(coordenador)}')
                valida = True
                while valida:
                    if not coordenador.isRecursoHabilitado and coordenador.fila[0].id == self.id:
                        self.processa_recurso()
                        valida = False

    def processa_recurso(self):
        coordenador = self.coordenador
        if coordenador is not None:
            print(f'****** Coordenador {coordenador.id} concede acesso ao processo {self.id}')
            print(f'{self.tag} Iniciando processo do recurso!')
            coordenador.isRecursoHabilitado = True
            sleep = randint(5, 15)
            time.sleep(sleep)
            print(f'{self.tag} Recurso processado em {sleep}s!')
            print(f'****** O processo {self.id} informa ao coordenador que o recurso foi liberado')
            print('\n')
            coordenador.isRecursoHabilitado = False
            self.remover_fila(coordenador)

    def remover_fila(self, coordenador):
        for f in coordenador.fila:
            if f.id == self.id:
                coordenador.fila.remove(self)

    def fila_coordenador(self, coordenador):
        s = []
        for f in coordenador.fila:
            s.append(f.id)
        return s


class Coordenador:
    def __init__(self, id):
        self.id = id
        self.isRecursoHabilitado = False
        self.fila = []

    def stop(self):
        del self

    def __repr__(self):
        return str(self.__dict__)


class Singleton:
    processos = []

    def gera_processo(self):
        while True:
            valida = False
            while not valida:
                ran_id = randint(0, 2048)
                valida = self.verifica_id_existente(ran_id)
            processo = Processos(ran_id)
            processo.set_coordenador(self.get_coordenador())
            self.processos.append(processo)
            time.sleep(40)

    def inativa_coordenador(self):
        while True:
            time.sleep(60)
            if len(self.processos) > 0:
                coordenador = self.processos[0].coordenador
                if coordenador is not None:
                    id = coordenador.id
                    processo = self.retorna_processo(coordenador.id)
                    processo.set_ativo(False)
                    self.remove_coordenador()
                    self.processos.remove(processo)
                    coordenador.stop()
                    processo.stop()
                    print(f'******* Coordenador inativo {id}')

    def get_coordenador(self):
        if len(self.processos) > 0:
            return self.processos[0].coordenador
        return None

    def gere_novo_coordenador(self):
        if len(self.processos):
            print('\n')
            print(f'******Elegendo um novo coordenador randomico')
            print(f'****Processos ativos: {self.processos_ativos()}')
            processo = self.processos[randint(0, len(self.processos) - 1)]
            coordenador = Coordenador(processo.id)
            print(f'{processo.tag} Novo coordenador!')
            self.adicionar_coordenador_processos(coordenador)

    def adicionar_coordenador_processos(self, coordenador):
        print(f'****Notificando processos do novo coordenador')
        for p in self.processos:
            p.set_coordenador(coordenador)
        print('\n')

    def processos_ativos(self):
        s = []
        for p in self.processos:
            s.append(p.id)
        return s

    def retorna_processo(self, id):
        for p in self.processos:
            if p.id == id:
                return p

    def remove_coordenador(self):
        for p in self.processos:
            p.set_coordenador(None)

    def verifica_id_existente(self, id):
        for i in self.processos:
            if i.id == id:
                return False
        return True

    def run(self):
        Thread(target=self.gera_processo).start()
        Thread(target=self.inativa_coordenador).start()


if __name__ == '__main__':
    Singleton().run()
