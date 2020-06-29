import time
import threading

global SALIDA=False

class contadorClasse(object):
    def __init__(self, contador):
        self.contador=contador
        self.hiloContador=threading.Thread(name = 'COntador',
                        target = contadorClasse.counter,
                        args = (self,),
                        daemon = False
                        )
    def counter(self):
        contador = 0
        while contador < self.contador:
            contador += 1
            time.sleep(1)
            print(contador)
            if contador== 20:
                SALIDA = False
                print(SALIDA)

objeto = contadorClasse(20)
objeto.hiloContador.start()