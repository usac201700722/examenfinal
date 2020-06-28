import paho.mqtt.client as mqtt
import logging
import time
import os 
import socket
import threading #Concurrencia con hilos
from brokerdata import *
from comandos import * 

SALAS_FILENAME = 'salas'
USER_FILENAME = 'usuarios'

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
        
        dato = msg.payload
        logging.debug("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
        logging.debug("El contenido del mensaje es: " + str(dato.decode('utf-8')))#que vino en el mss
        comandosEntrada(dato)
            
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
    def __init__(self,topic):
        self.topic=topic
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.topic),
                        daemon = True
                        )
        self.hiloEnviador=threading.Thread(name = 'Enviar nota de voz',
                        target = hiloTCP.conexionTCPenvio,
                        args = (self,self.topic),
                        daemon = True
                        )

    def conexionTCP(self, topic):
        # Crea un socket TCP
        logging.info(self.topic)
        okey = comandosCliente(self.topic)
        logging.debug(okey.OK())
        client.publish("comandos/08/201700722",okey.OK(),2,False)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

                    time.sleep(5)
                    enviar_nota_de_voz = hiloTCP(self.topic)
                    enviar_nota_de_voz.hiloEnviador.start()
                    bandera = False
                    break
            
            except KeyboardInterrupt:
                sock.close()

            finally:
                # Se baja el servidor para dejar libre el puerto para otras aplicaciones o instancias de la aplicacion
                connection.close()

    def conexionTCPenvio(self, topic):
        print(self.topic)
        #SERVER_ADDR = '167.71.243.238'
        SERVER_PORT = 9808
        #BUFFER_SIZE = 64 * 1024 
        objeto= comandosCliente(self.topic)
        fsize = os.stat('recibido.wav').st_size
        
        client.publish("comandos/08/201700722",objeto.fileReceive(fsize),2,False)
        server_socket = socket.socket()
        server_socket.bind((SERVER_ADDR, SERVER_PORT))
        server_socket.listen(1)#1 conexion activa y 9 en cola
        bandera = True
        try:
            while bandera==True:
                logging.info("\nEsperando conexion remota...\n")
                conn, addr = server_socket.accept()
                print('Conexion establecida desde ', addr)
                logging.debug('Enviando archivo de audio...')
                with open('recibido.wav', 'rb') as f: #Se abre el archivo a enviar en BINARIO
                    conn.sendfile(f, 0)
                    f.close()               
                conn.close()
                server_socket.close()
                print("\n\nArchivo enviado a: ", addr)               
                print("Cerrando el servidor...")
                time.sleep(2)
                bandera = False
        finally:
            print("Cerrando...")
            server_socket.close()

def comandosEntrada(dato):
    comando_accion = comandosServidor(str(dato))
    topic = comando_accion.separa()[1]
    
    if (comando_accion.separa()[0]=="03"):
        logging.info("Habilitando socket TCP para recepcion y envio de archivo")                  
        recibe = hiloTCP(topic)
        recibe.hiloRecibidor.start()
    elif (comando_accion.separa()[0]=="04"):
        logging.debug("**************************************")            
        logging.debug("Se recibio ALIVE de: "+str(topic))
    else:
        logging.debug("Comando no encontrado")
    time.sleep(5)

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la congiduracion 
first =b'\x01$201700722$4000'
client.publish("comandos/08/201700722",first,2,False)

#*********** Suscripciones del servidor ******************
qos = 1
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
        logging.debug("Hilo principal")
        time.sleep(5)
        	
except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")

finally:
    client.loop_stop()          #Se mata el hilo que verifica los topics en el fondo
    client.disconnect()         #Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")