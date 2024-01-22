import time
from random import randint
from threading import Thread

from numpy import False_

#Classe processo
class Processos():
    def __init__(self,id):
        self.id =id
        self.tag = f'Processo {id}:'
        self.coodernador = None
        self.isAtivo =True
        Thread(target=self.rum_p).start()

    def rum_p(self):
        print(f'{self.tag} Inicializando!')
        while self.isAtivo:
            self.consumir_recurso()
            time.sleep(randint(10, 25))
    def set_coordenador(self, coordenador):
        self.coodernador = coordenador

    def set_ativo(self, ativo):
        self.isAtivo = ativo   

    def stop(self):
        del self

    def __repr__(self):
        return str(self.__dict__)
# adicionaca chamada do algoritimo do anel
    def consumir_recurso(self):
        coordenador = self.coordernador
        if coordenador is None:
            Processos().gera_novo_coodenador()
        elif coordenador is not None and self.id != self.coordenador.id:
            print('\n') 
            print(f'{self.tag} Solicita acesso do recurso ao coordenador {coordenador.id}!')
            if coordenador.isRecursoHabilitado == False:
                self.processa_recurso()
            else:
                coordenador.fila.append(self)
                print(f'******Fila do coordenador = {self.fila_coordenador(coordenador)}') 
                valida = True
                while valida:
                    if coordenador.isRecursoHabilitado == False and coordenador.fila[0].id == self.id:
                         self.processa_recurso()
                         valida = False
        def processa_recurso(self):
            coodenador =  self.coodenador
            if coordenador is not None:
                print(f'****** Coordenador {coodenador.id}concede acesso ao processo{self.id}')
                print(f'{self.tag}Iniciando processo do recurso!')
                coordenador.isRecursoHabilitado = True
                sleep =  randint(5, 15)
                time.sleep(sleep)
                print(f'{self.tag} Recurso processado em {sleep}s!')
                print( f'****** O processo {self.id} informa ao coordeandor que o recurso foi liberado')
                print('\n')
                coodenador.isRecursoHabilitado = False
                self.remover_fila(coodenador)
    
    def remover_fila(self, coodenador):
        for f in coodenador.fila:
            if f.id == self.id:
                coodenador.fila.remove(self)

    def fila_coordenador(self, coodenador):
        s =[]
        for f in coodenador.fila:
            s.append(f.id)
        return s
class Coodenador:
        def __init__(self, id):
            self.id = id
            self.isRecursoHabilitado = False
            self.fila =[]


        def stop(self):
            del self

        def __repr__(self):
            return str(self.__dict__)

class Singleton:
        processos = []

        def gera_processo(self):
            while (True):
                valida = False
                while valida == False:
                    ran_id = randint(0, 2048)
                    valida = self.verifica_id_existente(ran_id)
                processo = Processos(ran_id)
                processo.set_coordenador(self.get_coordenador())
                self.processos.append(processo)
                time.sleep(40)
        
        def inativa_coordenador(self):
            while(True):
                time.sleep(60)
                if len(self.processos) > 0:
                    coodenador = self.processos[0].coodenador
                    if coodenador is not None:
                        id = coodenador.id
                        processo = self.retorna_processo(coodenador.id)
                        processo.set_ativo(False)
                        self.remove_coordenador()
                        self.processos.remove(processo)
                        coodenador.stop()
                        processo.stop()
                        print(f'******* Coordenador inativo {id}')
        
        def get_coordenador(self):
            if(len(self.processos) > 0):
                return self.processos[0].coodenador
            return None
        
        def gere_novo_coordenador(self):
            if len(self.processos):
                print('\n')
                print(f'******Elegendo um novo coordenador randomico')
                print(f'****Processos ativos: {self.processos_ativos()}')
                processo = self.processos[randint(0,  len(self.processos) -1 )]
                coodenador = Coodenador(processo.id)
                print(f'{processo.tag} Novo coordenador!')
                self.adicionar_coordenador_processos(coodenador)
        def adicionar_coordenador_processos(self, coodenador):
            print(f'****Notificando processos d novo coordendor')
            for p in self.processos:
                p.set_coordenador(coodenador)
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


if __name__== '__main__':
            Processos(4).run()