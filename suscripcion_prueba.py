SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuarios'

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
        archivo.close() #Cerrar el archivo al finaliza
        
        for i in datos:
            print("usuarios/"+str(i[0]))
    def __str__(self):
        return str(self.DATO_CUALQUIERA)
    def __repr__(self):
        return self.__str__

configuraciones.salas(SALAS_FILENAME)
configuraciones.usuarios(USER_FILENAME)