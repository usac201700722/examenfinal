import paho.mqtt.client as mqtt #SALU libreria para crear un cliente MQTT
import logging                  #SALU Libreria para trabajar con niveles de logging
import time                     #SALU LIbreria para realizar pausas de tiempo
import os                       #SALU LIbreria para usar comandos de bash en python
import socket                   #SALU Libreria para abrir un socket TCP
import threading                #SALU Concurrencia con hilos
from brokerdata import *        #SALU Datos con credenciales y constantes
from comandos import *          #SALU metodos para los comandos para negociacion

'''
Classe y comentario hecho por: SALU
en esta clase se configura al cliente MQTT, realizando diferentes llamadas
a metodos o handlers de la libreria paho mqtt
'''
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

'''
Comentario y clase hecha por: HANC, La clase configuracionesCLiente se encarga de
suscribir al cliente en los topics necesarios para la transmision de datos de tal forma
que sea una suscripcion automatica en base a los archivos usuarios/salas.
'''
class configuracionesServidor(object):
    def __init__(self, filename='', qos=2):
        self.filename = filename
        self.qos = qos
    #HANC suscripcion a los comandos de salas
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
            #logging.debug("comandos/"+str(i[0])+"/S"+str(i[1]))
    #HANC suscripcion a los comandos de usuarios
    def subComandos(self):
        datos = []
        archivo = open(self.filename,'r')   #HANC Abrir el archivo en modo de LECTURA
        for line in archivo:                 #HANC Leer cada linea del archivo
            registro = line.split(',')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close()                     #HANC Cerrar el archivo al finalizar       
        for i in datos:
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            #logging.debug("comandos/08/"+str(i[0]))

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" Qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

'''
Clase y comentario hecho por: SALU
En esta clase se ejecutan dos hilos, uno para la recepcion de archivos del cliente
y otros para transmitir archivos a un cliente, estas conexiones se hacen con
sockets TCP, las cuales hay que manejarse con mucho cuidado porque si el socket
no se cierra bien es posible que la transmision de archivos no se ejecute de la manera
correcta
'''
class hiloTCP(object):
    #SALU constructor de la clase y aqui definimos los hilos asociados a la clase
    def __init__(self,topic,topic_negociador):
        self.topic=topic
        self.topic_negociador=topic_negociador
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloTCP.conexionTCP,
                        args = (self,),
                        daemon = True
                        )
        self.hiloEnviador=threading.Thread(name = 'Enviar nota de voz',
                        target = hiloTCP.conexionTCPenvio,
                        args = (self,),
                        daemon = True
                        )

    #SALU Conexion TCP que se encarga de recibir el archivo de audio desde el cliente
    def conexionTCP(self):  
        #SALU Crea un socket TCP
        okey = comandosCliente(self.topic)
        topic_send="comandos/08/"+str(self.topic_negociador)
        client.publish(topic_send,okey.OK(),2,False)     
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #SALU Bind the socket to the port
        serverAddress = (IP_ADDR_ALL, IP_PORT) #SALU Escucha en todas las interfaces
        print('Iniciando servidor en {}, puerto {}'.format(*serverAddress))
        sock.bind(serverAddress) #Levanta servidor con parametros especificados
        #SALU Habilita la escucha del servidor en las interfaces configuradas
        sock.listen(10) #SALU El argumento indica la cantidad de conexiones en cola
        
        bandera = True
        while bandera==True:
            
            #SALU Esperando conexion
            logging.info('Esperando conexion remota')
            connection, clientAddress = sock.accept()
            try:
                print('Conexion establecida desde', clientAddress)
                archivo = open('recibido.wav','wb')
                while True:
                    data = connection.recv(BUFFER_SIZE)  
                    while data: #SALU Si se reciben datos (o sea, no ha finalizado la transmision del cliente)
                        logging.debug("Recibiendo...")
                        archivo.write(data)
                        data = connection.recv(BUFFER_SIZE)         
                    archivo.close()
                    logging.info('Transmision finalizada')
                    sock.close()
                    connection.close()
                    acknowledge = comandosCliente(self.topic_negociador)
                    topic_send="comandos/08/"+str(self.topic_negociador)
                    client.publish(topic_send,acknowledge.ack(),2,False)
                    #SALU espera unos segundos y activa el socket para enviar el archivo inmediatamente
                    time.sleep(3)
                    enviar_nota_de_voz = hiloTCP(self.topic,self.topic_negociador)
                    enviar_nota_de_voz.hiloEnviador.start()
                    bandera = False
                    break
            
            except KeyboardInterrupt:
                sock.close()

            finally:
                #SALU Se baja el servidor para dejar libre el puerto para otras aplicaciones o instancias de la aplicacion
                connection.close()
    #SALU este metodo se encarga de enviar el archivo de audio a un cliente por medio de un socket TCP
    def conexionTCPenvio(self): 
        SERVER_PORT = 9808 
        objeto= comandosCliente(self.topic)
        fsize = os.stat('recibido.wav').st_size
        client.publish("comandos/08/"+str(self.topic),objeto.fileReceive(fsize),2,False)
        server_socket = socket.socket()
        server_socket.bind((SERVER_ADDR, SERVER_PORT))
        server_socket.listen(10)    #SALU 1 conexion activa y 9 en cola
        bandera = True
        try:
            while bandera==True:
                logging.info("\nEsperando conexion remota...\n")
                conn, addr = server_socket.accept()
                print('Conexion establecida desde ', addr)
                logging.debug('Enviando archivo de audio...')
                with open('recibido.wav', 'rb') as f: #SALU Se abre el archivo a enviar en BINARIO
                    conn.sendfile(f, 0)
                    f.close()               
                conn.close()
                server_socket.close()
                print("\n\nArchivo enviado a: ", addr)               
                #time.sleep(2)
                bandera= False


        finally:
            logging.warning("Cerrando el servidor...")
            server_socket.close()

global acivos   #SALU: el uso de variables globales en una MALA PRACTICA, sin embargo, solo 
activos = []    # de esta forma se me ocurrio hacer que el chequeo de ALIVEs funcionara bien.

#HANC Método que verifica si un usuario esta contenido en una lista
def Carnets(carne):  
    i=0
    while(i <len(activos)):
        if activos[i] == carne:
            return True
        else:
            i+=1
    return False
'''
Método y comentario hecho por: SALU
Este metodo se encarga de procesar las tramas de los comandos del cliente
y de esta manera empezar la negociacion en la transferencia de archivos
'''
def comandosEntrada(dato):
    comando_accion = comandosServidor(str(dato))    #SALU variable tipo comandosServidor
    topic = comando_accion.separa()[1]              #SALU topic que envia datos o recibe (depende de la trama)
    topic_transmisor = comando_accion.separa()[2]   #SALU cuando se envia audio este es el usuario que hace la negociacion
    
    #SALU: Cuando es un FTR hace lo siguiente
    if (comando_accion.separa()[0]=="03"):
        logging.info("Se recibio FTR del cliente: "+str(topic_transmisor))
        esta_activo = Carnets(topic)    #SALU método que verifica si el remitente esta activo
        if esta_activo==True:           #SALU Si el remitente esta activo abre el socket TCP
            recibe = hiloTCP(topic,topic_transmisor)
            recibe.hiloRecibidor.start()
        else:                           #SALU si el remitente NO esta activo envia un mensaje de NO al negociador
            logging.warning("EL USUARIO NO ESTA ACTIVO")
            Nel_crack = comandosCliente(topic_transmisor)
            topic_send="comandos/08/"+str(topic_transmisor)
            client.publish(topic_send,Nel_crack.NO(),2,False) 

    #SALU CUando el comando es un ALIVE el servidor guarda al usuario en una lista y envia una 
    #validacion con ACK   
    if (comando_accion.separa()[0]=="04"):
        logging.debug("Se recibio ALIVE de: "+str(topic))
        activos.append(topic)
        acknowledge = comandosCliente(topic)
        topic_send="comandos/08/"+str(topic)
        client.publish(topic_send,acknowledge.ack(),2,False)

    else:
        logging.debug("Comando no encontrado")
    time.sleep(5)

#SALU Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(threadName)-10s) %(message)s'
    )

#SALU empieza la configuracion MQTT
client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la congiduracion 

#first =b'\x01$201700722$4000'
#client.publish("comandos/08/201700722",first,2,False)

#*********** Suscripciones del servidor ******************
#SALU hace las suscripciones automaticas del servidor
qos = 1
salas = configuracionesServidor(SALAS_FILENAME,qos)
salas.subSalas()
comandos = configuracionesServidor(USER_FILENAME,qos)
comandos.subComandos()
#***********************************************************

#SALU Iniciamos el thread (implementado en paho-mqtt) para estar atentos a mensajes en los topics subscritos
client.loop_start()	#COn esto hacemos que las sub funcionen
#SALU El thread de MQTT queda en el fondo, mientras en el main loop hacemos otra cosa

#time.sleep(5)
try:
    while True:
        logging.debug("Esperando comando...")
        time.sleep(5)
        	
except KeyboardInterrupt:
    logging.warning("Desconectando del broker...")  #SALU Advertencia que se esta desconectando del broker

finally:
    client.loop_stop()          #SALU Se mata el hilo que verifica los topics en el fondo
    client.disconnect()         #SALU Se desconecta del broker
    logging.info("Desconectado del broker. Saliendo...")    #SALU mensaje final