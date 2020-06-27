import paho.mqtt.client as paho
import logging
import time
import socket
import random
import os
import sys       #Requerido para salir (sys.exit())
import threading #Concurrencia con hilos
from brokerdata import * #Informacion de la conexion
from comandos import *
from encriptado import *

PASSWORD = "hola"
USER_FILENAME ='usuario'
SALAS_FILENAME = 'salas'
DEFAULT_DELAY = 2
dato=b'\x01$000'

class MQTTconfig(paho.Client):
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
        if str(msg.topic)=="comandos/08/201700722":
            global dato 
            dato = msg.payload
            logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.info("El contenido del mensaje es: " + str(msg.payload))#que vino en el mss
            comandos_funcion(dato)
        else:
            mensaje_chat= msg.payload
            logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.info("El contenido del mensaje es: " + str(mensaje_chat.decode('utf-8')))#que vino en el mss

            
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


class configuracionCLiente(object):
    def __init__(self,filename='', qos=2):
        self.filename = filename
        self.qos = qos

    def subComandos(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            logging.debug("comandos/08/"+str(i[0]))
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            logging.debug("usuarios/08/"+str(i[0]))

    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), self.qos))
            logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

class hilos(object):
    def __init__(self,tiempo):
        self.tiempo=tiempo
        self.hiloGrabar=threading.Thread(name = 'Nota de voz',
                        target = hilos.grabarAudio,
                        args = (self,self.tiempo),
                        daemon = True
                        )
    def grabarAudio(self,tiempo=0):
        grabador = str("arecord -d "+str(tiempo)+" -f U8 -r 8000 ultimoAudio.wav")
        logging.info('Comenzando la grabación')
        os.system(grabador)
        logging.info('***Grabación finalizada***')
 
class hiloTCP(object):
    def __init__(self, SERVER_IP):
        self.SERVER_IP=SERVER_IP
        self.hiloConexion=threading.Thread(name = 'Concexion por TCP',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.SERVER_IP),
                        daemon = True
                        )
        self.hiloConexionRecibir=threading.Thread(name = 'Recibiendo archivo de audio',
                        target = hiloTCP.conexionTCPrecibir,
                        args = (self,self.SERVER_IP),
                        daemon = True
                        )

    def conexionTCP(self, SERVER_IP):
        self.SERVER_IP   = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024
        time.sleep(5)
        # Se crea socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Se conecta al puerto donde el servidor se encuentra a la escucha
        server_address = (self.SERVER_IP, SERVER_PORT)
        print('Conectando a {} en el puerto {}'.format(*server_address))
        sock.connect(server_address)
        
        try:
            archivo = open('EultimoAudio.wav','rb')
            print("Enviando...")
            l=archivo.read(BUFFER_SIZE)
            while l:
                print("Sending...")
                sock.send(l)
                l=archivo.read(BUFFER_SIZE)
            archivo.close()
            print("Done sending")
            first =b'\x01$201700722$4000'
            client.publish("comandos/08/201700722",first,2,False)
            sock.close()
        except ConnectionRefusedError:
            logging.error("El servidor ha rechazado la conexion, intente hacerlo otra vez")
  
    def conexionTCPrecibir(self,SERVER_IP):
        SERVER_ADDR = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024

        sock = socket.socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))

        try:
            buff = sock.recv(BUFFER_SIZE)
            archivo = open('recibido.wav', 'wb') #Aca se guarda el archivo entrante
            while buff:
                buff = sock.recv(BUFFER_SIZE) #Los bloques se van agregando al archivo
                archivo.write(buff)
            archivo.close() #Se cierra el archivo
            print("Recepcion de archivo finalizada")

        finally:
            print('Conexion al servidor finalizada')
            sock.close() #Se cierra el socket

        Desencriptar(getkey(PASSWORD),"recibido.wav")
        os.system('aplay (D)recibido.wav')

def comandos_funcion(dato_entrada):
    comando_accion = comandosServidor(str(dato_entrada))
    logging.debug("Si entro a la funcion")
    if (comando_accion.separa()[0]=="02"):
        recibir_audio= hiloTCP(SERVER_IP)
        recibir_audio.hiloConexionRecibir.start()
    else:
        pass



#Configuracion inicial de logging
logging.basicConfig(
    level = logging.DEBUG, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 

logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola

#SALU Iniciamos la configuracion del cliente MQTT
client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la congiduracion 

#************* Suscripciones del cliente *********
comandos= configuracionCLiente(USER_FILENAME,2)
comandos.subComandos()
usuarios = configuracionCLiente(USER_FILENAME,2)
usuarios.subUsuarios()
salas = configuracionCLiente(SALAS_FILENAME,2)
salas.subSalas()
#***************************************************

print('''
Menú:
1- Enviar texto
    a. Enviar a usuario --> PRESIONE "1a"
    b. Enviar a sala    --> PRESIONE "1b"
2- Enviar mensaje de voz
    a. Enviar a usuario --> PRESIONE "2a"
        i. Duración (Segundos)
    b. Enviar a sala    --> PRESIONE "2b"
        i. Duración (Segundos)
''')

client.loop_start()
#Loop principal: leer los datos de los sensores y enviarlos al broker en los topics adecuados cada cierto tiempo
try:
    while True: 
        comando = input("Ingrese el comando: ")
        
        if comando == "1a":
            topic_send = input("Ingrese el numero de usuario (Ej: '201700376', sin comillas): ")
            mensaje = input("Texto a enviar: ")
            client.publish("usuarios/08/"+str(topic_send),mensaje,1,False)
        elif comando == "1b":
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            mensaje = input("Texto a enviar: ")
            client.publish("salas/08/"+str(topic_send),mensaje,1,False)
        elif comando == "2a":
            topic_send = input("Ingrese el usuario al que desea enviar el audio (Ej: '201700376', sin comillas): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                size= os.stat('ultimoAudio.wav').st_size
                mensaje = comandosCliente(topic_send)
                print(mensaje.fileTransfer(size))
                client.publish("comandos/08/"+str(topic_send),mensaje.fileTransfer(size),1,False)
                Encriptar(getkey(PASSWORD),"ultimoAudio.wav")
                time.sleep(10)
                conexion= hiloTCP(SERVER_IP)
                conexion.hiloConexion.start()
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                break
        
        elif comando == "2b":
            topic_send = input("Ingrese la sala a la que desea enviar el audio (Ej: 'S01', sin comillas y S Mayúscula): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            #grabar = hilos(duracion)
            #grabar.hiloGrabar.start()
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                size= os.stat('ultimoAudio.wav').st_size
                mensaje = comandosCliente(topic_send)
                print(mensaje.fileTransfer(size))
                client.publish("comandos/08/"+str(topic_send),mensaje.fileTransfer(size),1,False)
                time.sleep(10)
                conexion= hiloTCP(SERVER_IP)
                conexion.hiloConexion.start()
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                break
        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")
               
        logging.debug("Los datos han sido enviados al broker")            
        #Retardo hasta la proxima publicacion de info
        time.sleep(DEFAULT_DELAY)

except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.loop_stop()
    client.disconnect()
    logging.info("Se ha desconectado del broker. Saliendo...")