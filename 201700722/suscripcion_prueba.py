SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuario'
class configuraciones (object):
    def __init__(self, DATO_CUALQUIERA):
        self.DATO_CUALQUIERA = DATO_CUALQUIERA

    def salas(self, fileName = 'salas'):
        datos = []
        archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        print(len(datos))
        for i in datos:
            print("salas/"+str(i[0])+"/S"+str(i[1]))

    def usuarios(self, fileName = 'usuarios'):
        datos = []
        archivo = open(fileName,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split(',')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        
        for i in datos:
            print("usuarios/"+str(i[0]))

    def subComandos(self, filename = 'usuario'):
        datos = []
        archivo = open(filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            print("comandos/"+str(i))
            #client.subscribe(("comandos/"+str(i[0]), qos))
            #logging.debug("comandos/"+str(i[0]))

configuraciones.subComandos(USER_FILENAME)