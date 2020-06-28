import string

alfabeto = list(string.ascii_lowercase)

def cifrado_cesar(alfabeto,n,texto):
    texto_cifrado = ""
    for letra in texto:
        if letra in alfabeto:
            indice_actual = alfabeto.index(letra)
            indice_cesar = indice_actual + n
            if indice_cesar > 25:
                indice_cesar -= 25
            texto_cifrado += alfabeto[indice_cesar]
        else:
            texto_cifrado += letra
    return texto_cifrado


def decodificar(alfabeto,n,texto):
    texto_decodificado = ""
    for letra in texto:
        if letra in alfabeto:
            indice_cesar = alfabeto.index(letra)
            indice_original = indice_cesar - n
            if indice_original <0 :
                indice_original += 25
            texto_decodificado += alfabeto[indice_original]
        else:
            texto_decodificado += letra
    return texto_decodificado

#frase = "hola a todos, bienvenidos al curso de python 3 desde cero orientado por la cartilla"
#frase_cifrada = cifrado_cesar(alfabeto,3,frase)
#frase_decodificada = decodificar(alfabeto,3,frase_cifrada)
#print(frase_cifrada)
#print(frase_decodificada)