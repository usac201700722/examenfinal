import os
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

def Encriptar(key,filename):
    BUFFER_SIZE = 64* 1025
    outfile = "(C)"+filename
    filesize = str(os.path.getsize(filename)).zfill(16)
    IV = Random.new().read(16)

    encryptor = AES.new(key, AES.MODE_CBC,IV)

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

def Desencriptar(key,filename):
    BUFFER_SIZE = 64*1024
    outputfile = "(D)"+filename         #filename[11:]

    with open(filename, 'rb') as infile:
        filesize =int(infile.read(16))
        IV = infile.read(16)

        descryptor = AES.new(key, AES.MODE_CBC,IV)

        with open(outputfile, 'wb') as outfile:
            while True:
                BUFFER = infile.read(BUFFER_SIZE)

                if len(BUFFER)==0:
                    break
                
                outfile.write(descryptor.decrypt(BUFFER))
            outfile.truncate(filesize)


def getkey(password):
    hasher = SHA256.new(password.encode('utf-8'))
    return hasher.digest()

def Main():
    choice = input('Que quiere hacer? (D) o (E): ')

    if choice=='E':
        filename = input("file to encript: ")
        password = input("password: ")
        Encriptar(getkey(password),filename)
        print("DOne")
    elif choice=='D':
        filename = input("file to encript: ")
        password = input("password: ")
        Desencriptar(getkey(password),filename)
        print("DOne")
    else:
        print("No selecciono nada... cerrando")

if __name__ == "__main__":
    Main()



                   