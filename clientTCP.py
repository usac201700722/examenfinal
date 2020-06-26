import socket

SERVER_IP   = '167.71.243.238'
SERVER_PORT = 9808
BUFFER_SIZE = 64 * 1024

# Se crea socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Se conecta al puerto donde el servidor se encuentra a la escucha
server_address = (SERVER_IP, SERVER_PORT)
print('Conectando a {} en el puerto {}'.format(*server_address))
sock.connect(server_address)

archivo = open('ultimoAudio.wav','rb')
print("Enviando...")
l=archivo.read(BUFFER_SIZE)
while l:
    print("Sending...")
    sock.send(l)
    l=archivo.read(BUFFER_SIZE)
archivo.close()
print("DOne sending")
sock.close()
