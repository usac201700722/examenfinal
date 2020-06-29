#SALU
#La clase comandosCLiente sirve para realizar las tramas de la negociacion
#entre cliente y servidor, a pesar que se llame comandosCLiente, no esta limitado
#solo a cliente, sino que el servidor tambien podra hacer uso de esta clase.
class comandosCliente(object):
    def __init__(self,Dest):
        self.Dest=Dest
        self.SEP= b'$'

    def fileTransfer(self, enviador, File_size=0):  #SALU Trama para FTR
        FTR=b'\x03'
        Destino = self.Dest
        Destino=Destino.encode()
        topic_enviador = str(enviador)
        topic_enviador=topic_enviador.encode()      
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama= FTR+self.SEP+Destino+self.SEP+topic_enviador+self.SEP+tamArchivo
        return trama
    def alive(self, extra=0):        #SALU Trama para ALIVE
        ALIVE=b'\x04'
        Destino = self.Dest
        Destino=Destino.encode()
        extra_1 = str(extra)
        extra_1=extra_1.encode()
        trama= ALIVE+self.SEP+Destino+self.SEP+extra_1
        return trama
        
    def fileReceive(self, File_size=0):     #SALU Trama para FRR
        FRR=b'\x02'
        Destino = self.Dest
        Destino=Destino.encode()
        tamArchivo=str(File_size)
        tamArchivo=tamArchivo.encode()
        trama = FRR+self.SEP+Destino+self.SEP+tamArchivo
        return trama
    def ack(self):                          #SALU Trama para ACK
        ACK=b'\x05'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= ACK+self.SEP+Destino
        return trama

    def OK(self):                           #SALU Trama para OK
        OKEY=b'\x06'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= OKEY+self.SEP+Destino
        return trama

    def NO(self):                           #SALU Trama para NO
        NEL=b'\x07'
        Destino = self.Dest
        Destino=Destino.encode()
        trama= NEL+self.SEP+Destino
        return trama

    def __str__(self):
        return "Destino: "+str(self.Dest)+" Tamaño de archivo: "#+str(self.File_size)
    def __repr__(self):
        return self.__str__

#Comentario y clase hecho por: HANC
#La clase comandosServidor sirve para obtener la trama recibida del cliente y 
#separar cada dato como "comando", "ID O SALA" y/o "Tamaño del archivo",
#aunque la clase se llame comandosServidor no esta limitada solo al servidor
#Para este caso el cliente tambien hara uso de ella.

class comandosServidor(object):
    #HANC Metodo constructor de la clase coomandosServidor
    def __init__(self, comando):
        self.comando= str(comando)
    def __str__(self):
        return str(self.separa())
    def __repr__(self): 
        return self.__str__()
    def __len__(self):
        return len(self.comando)
    #HANC Metodo que separa los comandos hechos por el usuario para enviarlos al servidor
    def separa(self):
        lista = []
        separados=[]
        lista = self.comando.split("b'\\x")
        union = str(lista[1])
        separados = union.split("$")
        return separados
