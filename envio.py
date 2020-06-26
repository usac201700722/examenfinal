import binascii

class comandosServidor(object):
    def __init__(self, comando):
        self.comando = comando

    def __len__(self):
        return len(self.comando)

    def separa(self):
        lista = []
        codi=''
        destinatario =''
        tamaño=''
        if(len(self) > 16):
            for i in range(len(self)):
                if i>3 and i<6:
                    codi = codi + self.comando[i]
                elif i>5 and i < 15:
                    destinatario = destinatario + self.comando[i]
                elif i >14 and i < len(self)-1:
                    tamaño = tamaño + self.comando[i]
            lista.append(codi)
            lista.append(destinatario)
            lista.append(tamaño)
            return lista
        else:
            for i in range(len(self)):
                if i>3 and i<6:
                    codi = codi + self.comando[i]
                elif i>5 and i < 11:
                    destinatario = destinatario + self.comando[i]
                elif i >10 and i < len(self)-1:
                    tamaño = tamaño + self.comando[i]
            lista.append(codi)
            lista.append(destinatario)
            lista.append(tamaño)
            return lista
    #def
    #sdef 
    def __str__(self):
        return str(self.separa())
    def __repr__(self): 
        return self.__str__()
#el \x03 no lo toma en cuenta solo el 3 como al final el comando es ese, o si es 4 y asi
#sucesivamente entonces ya lo deja separado, luego toma el carnet o la sala y deja de
#de ultimo el tamaño del archivo, no importando la cantidad de digitos
# y hay ifs porque uno es si es el cliente osea el carnet o es una sala
datorecibido = b'\x032017007224048'
datosrecibidos = b'\x0314S014048'
total = comandosServidor(str(datorecibido))
separados = comandosServidor(str(datosrecibidos))
print(total)
print(separados)

print(separados.separa()[0])
print(separados.separa()[1])
print(separados.separa()[2])