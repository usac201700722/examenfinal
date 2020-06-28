#Este programa fue inspirado de un canal de youtube que tiene un curso de 
#python, nos guiamos de un video porque en el curso no se enseño la encriptacion
#por el corto tiempo del mismo, por esa razon nos guiamos de la documentacion
#que tuvimos a nuestro alcance, en este caso fue un video.

import os       #SALU libreria para el manejo de comandos bash
from Crypto.Cipher import AES   #SALU Librerias de PYcrypto
from Crypto.Hash import SHA256  #SALU Librerias de Pycrypto
from Crypto import Random       #SALU Librerias de pycripto

'''
Comentario y metodo hecho por: SALU
Este metodo se encarga de encriptar un archivo de audio
para esto recibe dos parametros uno es la llave, que sera la contraseña
con la que encriptara el audio y la otra es el nombre del archivo
a encriptar.
'''
def Encriptar(key,filename):
    BUFFER_SIZE = 64* 1025
    outfile = "Encriptado_"+filename    #SALU nombre del archiv de salida
    filesize = str(os.path.getsize(filename)).zfill(16)
    IV = Random.new().read(16)
    encryptor = AES.new(key, AES.MODE_CBC,IV)

    #Abrimos el archivo de audio para encriptarlo
    with open(filename,'rb') as infile:
        with open(outfile,'wb') as outfile:
            outfile.write(filesize.encode('utf-8'))
            outfile.write(IV)

            while True:
                BUFFER = infile.read(BUFFER_SIZE)
                if len(BUFFER)==0:
                    break
                elif len(BUFFER)%16 != 0:
                    BUFFER += b' '*(16-(len(BUFFER)%16))                
                outfile.write(encryptor.encrypt(BUFFER))

'''
Comentario y metodo hecho por: SALU
Este metodo se encarga de desencriptar un archivo de audio
para esto recibe dos parametros uno es la llave, que sera la contraseña
con la que desencriptara el audio y la otra es el nombre del archivo
a encriptar.
'''
def Desencriptar(key,filename):
    BUFFER_SIZE = 64*1024
    outputfile = "Desencriptado_"+filename  #SALU nombre del archivo de salida

    with open(filename, 'rb') as infile:    #SALU se abre el archivo para encriptarlo
        filesize =int(infile.read(16))
        IV = infile.read(16)
        descryptor = AES.new(key, AES.MODE_CBC,IV)

        with open(outputfile, 'wb') as outfile: #SALU comienza el proceso de desencriptacion
            while True:
                BUFFER = infile.read(BUFFER_SIZE)
                if len(BUFFER)==0:
                    break
                
                outfile.write(descryptor.decrypt(BUFFER))
            outfile.truncate(filesize)

#SALU metodo que crea un HASH en base a la contraseña de des/encriptado
#Esto permite que nuestra contraseña sea mas segura
def getkey(password):
    hasher = SHA256.new(password.encode('utf-8'))
    return hasher.digest()                   