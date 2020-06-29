'''
Comentario y aclaracion hecho por: SALU
Para el encriptado del mensaje de texto enviado por MQTT se utilizo
el algoritmo de encriptado cesar, este algoritmo permite sustituir
cada caracter por otro 'aleatorio' (No es aleatorio, pero eso se pretende).
Utilizamos este algortimo porque era el que mas se adecuaba a las necesidades
del proyecto del curso, especialmente porque es informacion poco sensible.
'''
import string #HANC Se importa la libreria string para la manipulacion de cadenas de texto
letras = list(string.ascii_lowercase)#HANC Crea una lista con caracteres ASCII de las letras minusculas del alfabeto

#HANC Funcion utilizada para la encriptacion del mensaje a enviar por el usuario
def crypt_cesar(letras,n,cifrado):
    encrypt = "" 
    for caracter in cifrado: #HANC Se obtiene cada uno de los caracteres del texto a cifrar
        if caracter in letras: #HANC Verifica si el caracter esta dentro de la lista letras
            index_now = letras.index(caracter) #HANC Se obtiene la posicion del caracter de la lista
            index_cesar = index_now + n #HANC A esa posicion se le agrega un valor entero para asi crifrar el texto
            if index_cesar > 25: 
                index_cesar -= 25 #HANC Para que los valores queden dentro del rango de la lista
            encrypt += letras[index_cesar] #HANC Agrega el valor str al texto cirfrado "encrypt"
        else:
            encrypt += caracter #HANC Si no se encuentra el caracter simplemente lo agrega
    return encrypt

#HANC Funcion para desencriptar
def decrypt(letras,n,cifrado):
    text_decrypt = ""
    for caracter in cifrado: #HANC Se obtienen los caracteres del texto
        if caracter in letras: #HANC Verifica si el caracter esta dentro de la lista letras
            index_cesar = letras.index(caracter) #HANC Se obtiene el indice de la lista
            index_origi = index_cesar - n #HANC Se obtiene la posicicion original del caracter
            if index_origi <0 :
                index_origi += 25 #HANC Para que los valores queden dentro del rango de la lista
            text_decrypt += letras[index_origi] #HANC Agrega el valor str al texto "decrypt" 
        else:
            text_decrypt += caracter #HANC Si no se encuentra el caracter simplemente lo agrega
    return text_decrypt
