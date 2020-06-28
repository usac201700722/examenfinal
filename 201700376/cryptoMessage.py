import Crypto
import binascii
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

random_generator = Crypto.Random.new().read

private_key = RSA.generate(1024, random_generator)
public_key = private_key.publickey()

private_key= private_key.exportKey(format='DER')
public_key= public_key.exportKey(format='DER')

private_key = binascii.hexlify(private_key).decode('utf8')
public_key = binascii.hexlify(public_key).decode('utf8')

#Proceso inverso

private_key=RSA.importKey(binascii.unhexlify(private_key))
public_key=RSA.importKey(binascii.unhexlify(public_key))

def encriptarMensaje(message):
    #message = "Hola perros"
    message = message.encode()
    cipher = PKCS1_OAEP.new(public_key)
    encripted_message = cipher.encrypt(message)
    print(encripted_message)
    return encripted_message

def desencriptarMensaje(encripted_message):
    cipher=PKCS1_OAEP.new(private_key)
    message=cipher.decrypt(encripted_message)
    print(message)
    return message

'''
encriptado=encriptarMensaje("Hola amigos")
desencriptarMensaje(encriptado)
'''