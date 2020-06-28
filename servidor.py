import paho.mqtt.client as mqtt
import logging
import time
import os 
import socket
import threading #Concurrencia con hilos
from brokerdata import *
from comandos import * 


LOG_FILENAME = 'mqtt.log'
SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuarios'
dato=b''

class MQTTconfig(mqtt.Client):
    def on_connect(self, client, userdata, flags, rc):
        #SALU Handler en caso suceda la conexion con el broker MQTT
        connectionText = "CONNACK recibido del broker con codigo: " + str(rc)
        logging.debug(connectionText)
    def on_publish(self, client, userdata, mid): 
        #SALU Handler en caso se publique satisfactoriamente en el broker MQTT
        publishText = "Publicacion satisfactoria"
        logging.debug(publishText)
    def on_message(self, client, userdata, msg):	
        #SALU Callback que se ejecuta cuando llega un mensaje al topic suscrito
        #SALU msg contiene el topic y la info que llego
        #SALU Se muestra en pantalla informacion que ha llegado
        #Se muestra en pantalla informacion que ha llegado
        global dato 
        dato = msg.payload
        logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
        logging.info("El contenido del mensaje es: " + str(dato.decode('utf-8')))#que vino en el mss
            
    def on_subscribe(self, client, obj,mid, qos):
        #SALU Handler en caso se suscriba satisfactoriamente en el broker MQTT
        logging.debug("Suscripcion satisfactoria")

    def run(self):
        #SALU este metodo inicializa la conexion MQTT con las credenciales del broker
        self.username_pw_set(MQTT_USER, MQTT_PASS)
        self.connect(host=MQTT_HOST, port = MQTT_PORT)        
        rc = 0
        while rc==0:
            rc = self.loop_start()
        return rc

class configuracionesServidor(object):

    def __init__(self, filename='', qos=2):
        self.filename = filename
        self.qos = qos

    
    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') 
        for line in archivo:
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("comandos/"+str(i[0])+"/S"+str(i[1]), qos))
            logging.debug("comandos/"+str(i[0])+"/S"+str(i[1]))
    '''
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split(',')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar       
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            logging.debug("usuarios/08/"+str(i[0]))
    '''
    def subComandos(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split(',')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar       
        for i in datos:
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            logging.debug("comandos/08/"+str(i[0]))

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" Qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

class hiloTCP(object):
    def __init__(self,IP_ADDR):
        self.IP_ADDR=IP_ADDR
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.IP_ADDR),
                        daemon = False
                        )
        self.hiloEnviador=threading.Thread(name = 'Enviar nota de voz',
                        target = hiloTCP.conexionTCPenvio,
                        args = (self,self.IP_ADDR),
                        daemon = False
                        )

    def conexionTCP(self, IP_ADDR):
        # Crea un socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.IP_ADDR ='167.71.243.238' #La IP donde desea levantarse el server

        # Bind the socket to the port
        serverAddress = (IP_ADDR_ALL, IP_PORT) #Escucha en todas las interfaces
        print('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
        sock.bind(serverAddress) #Levanta servidor con parametros especificados

        # Habilita la escucha del servidor en las interfaces configuradas
        sock.listen(10) #El argumento indica la cantidad de conexiones en cola
        
        bandera = True
        while bandera==True:
            # Esperando conexion
            logging.info('Esperando conexion remota')
            connection, clientAddress = sock.accept()
            try:
                print('Conexion establecida desde', clientAddress)
                archivo = open('recibido.wav','wb')
                while True:
                    data = connection.recv(BUFFER_SIZE)  
                    while data: #Si se reciben datos (o sea, no ha finalizado la transmision del cliente)
                        logging.debug("Recibiendo...")
                        archivo.write(data)
                        data = connection.recv(BUFFER_SIZE)         
                    archivo.close()
                    logging.info('Transmision finalizada')
                    sock.close()
                    connection.close()
                    time.sleep(10)
                    enviar_nota_de_voz = hiloTCP(IP_ADDR)
                    enviar_nota_de_voz.hiloEnviador.start()
                    bandera = False
                    break
            
            except KeyboardInterrupt:
                sock.close()

            finally:
                # Se baja el servidor para dejar libre el puerto para otras aplicaciones o instancias de la aplicacion
                connection.close()

    def conexionTCPenvio(self, IP_ADDR):
        SERVER_ADDR = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024 
        
        File_Receive_request=b'\x02$201700722'
        client.publish("comandos/08/201700722",File_Receive_request,2,False)
        server_socket = socket.socket()
        server_socket.bind((SERVER_ADDR, SERVER_PORT))
        server_socket.listen(100)#1 conexion activa y 9 en cola
        try:
            while True:
                logging.info("\nEsperando conexion remota...\n")
                conn, addr = server_socket.accept()
                print('Conexion establecida desde ', addr)
                logging.debug('Enviando archivo de audio...')
                with open('recibido.wav', 'rb') as f: #Se abre el archivo a enviar en BINARIO
                    conn.sendfile(f, 0)
                    f.close()
                conn.close()
                print("\n\nArchivo enviado a: ", addr)
                server_socket.close()
        finally:
            print("Cerrando el servidor...")
            server_socket.close()


#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la congiduracion 
first =b'\x01$201700722$4000'
client.publish("comandos/08/201700722",first,2,False)

#*********** Suscripciones del servidor ******************
qos = 1
'''
user = configuracionesServidor(USER_FILENAME,qos)
user.subUsuarios()
'''
salas = configuracionesServidor(SALAS_FILENAME,qos)
salas.subSalas()
comandos = configuracionesServidor(USER_FILENAME,qos)
comandos.subComandos()
#***********************************************************

#Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()	#COn esto hacemos que las sub funcionen
#El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

time.sleep(5)
try:
    while True:
        comando_accion = comandosServidor(str(dato))
        
        if (comando_accion.separa()[0]=="03"):
            print("**************************************")
            recibe = hiloTCP(IP_ADDR)
            recibe.hiloRecibidor.start()
        else:
            logging.debug("No hago nada")

        time.sleep(10)	


except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")

finally:
    client.loop_stop() #Se mata el hilo que verifica los topics en el fondo
    client.disconnect() #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")