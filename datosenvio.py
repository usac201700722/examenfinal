class comandosServidor(object):
    def __init__(self, comando):
        self.comando= str(comando)
    def __str__(self):
        return str(self.separa())
    def __repr__(self): 
        return self.__str__()
    def __len__(self):
        return len(self.comando)

    def separa(self):
        lista = []
        separados=[]
        lista = self.comando.split("b'\\x")
        union = str(lista[1])
        separados = union.split("$")
        return separados

datosrecibidos = b'\x03$14S01$4048'
datorecibido = b'\x03$201700722$201700376$4048'
envio = comandosServidor(str(datosrecibidos))
enviar = comandosServidor(str(datorecibido))
print(envio)
print(enviar)