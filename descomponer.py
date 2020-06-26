datorecibido = '\x032017007224048'
#Si el dato es directamente un tipo string no puedo acceder al \x03
#pero si el dato accede como tipo input osea como si estubieras pidendo el dato 
#si puedo acceder a el
datosrecibidos = input("ingresas el numero como si ")
#Usas cualquiera de las dos funciones ya que va a depender de como es que lo va a recibir
#En el servidor o en el cliente, si no era eso pues no entendi entonces jajaja xd
def partir(dato):
    lista =[]
    comando=''
    destinatario = ''
    tamaño=''
    for i in range(len(dato)):
        if i<1:
            a = a + dato[i]
        elif i>0 and i < 10:
            b = b + dato[i]
        else:
            c = c+dato[i]
    lista.append(comando)
    lista.append(destinatario)
    lista.append(tamaño)
    return lista

def partirlos(dato):
    lista =[]
    comando=''
    destina = ''
    c=''
    for i in range(len(dato)):
        if i>1 and i<4:
            a = a + dato[i]
        elif i>3 and i < 13:
            b = b + dato[i]
        elif i>12 and i<len(dato):
            c = c+dato[i]
    lista.append(a)
    lista.append(b)
    lista.append(c)
    return lista

print(partir(datorecibido))
print(partirlos(datosrecibidos))
