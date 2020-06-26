import socket

# Crea un socket TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

IP_ADDR = '167.71.243.238' #La IP donde desea levantarse el server
IP_ADDR_ALL = '' #En caso que se quiera escuchar en todas las interfaces de red
IP_PORT = 9808 #Puerto al que deben conectarse los clientes

BUFFER_SIZE = 64 * 1024 #Bloques de 64 KB

# Bind the socket to the port
serverAddress = (IP_ADDR_ALL, IP_PORT) #Escucha en todas las interfaces
print('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
sock.bind(serverAddress) #Levanta servidor con parametros especificados

# Habilita la escucha del servidor en las interfaces configuradas
sock.listen(10) #El argumento indica la cantidad de conexiones en cola
bandera = True
while bandera==True:
    # Esperando conexion
    print('Esperando conexion remota')
    connection, clientAddress = sock.accept()
    try:
        print('Conexion establecida desde', clientAddress)
        archivo = open('recibido.wav','wb')
        while True:
            data = connection.recv(BUFFER_SIZE)  
            while data: #Si se reciben datos (o sea, no ha finalizado la transmision del cliente)
                print("Recibiendo...")
                archivo.write(data)
                data = connection.recv(BUFFER_SIZE)         
            archivo.close()
            print('Transmision finalizada desde el cliente ', clientAddress)
            sock.close()
            connection.close()
            bandera = False
            break
    
    except KeyboardInterrupt:
        sock.close()

    finally:
        # Se baja el servidor para dejar libre el puerto para otras aplicaciones o instancias de la aplicacion
        connection.close()