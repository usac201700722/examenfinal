import paho.mqtt.client as paho
import logging
import time
import socket
import random
import os
import sys                  #Requerido para salir (sys.exit())
import threading            #Concurrencia con hilos
from brokerdata import *    #Informacion de la conexion
from comandos import *
from encriptado import *
from cifradocesar import *

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
        topic_usuario="comandos/08/"+str(lista_user[0])
        if str(msg.topic)==topic_usuario:
            dato = msg.payload
            logging.debug("--------------------------------------------------------------------------")
            logging.debug("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.debug("El contenido del mensaje es: " + str(msg.payload))#que vino en el mss
            logging.debug("--------------------------------------------------------------------------")
            comandos_funcion(dato)
        else:      
            mensaje_chat= msg.payload
            frase_cifrada=str(mensaje_chat.decode('utf-8'))           
            frase_decodificada = decrypt(letras,5,frase_cifrada)
            logging.debug("Mensaje encriptado" + str(frase_cifrada))
            logging.info("**************************************************************************")
            logging.info("Ha llegado el mensaje al topic: " + str(msg.topic)) #de donde vino el mss
            logging.info("El contenido del mensaje es: " + str(frase_decodificada)) #que vino en el mss
            logging.info("**************************************************************************")
            
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
        com=[]
        for i in datos:
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            logging.debug("comandos/08/"+str(i[0]))
            com.append(i[0])
        return com
    
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        user = []
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            logging.debug("usuarios/08/"+str(i[0]))
            user.append(i[0])
        return user

    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        sal =[]
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), self.qos))
            logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))
            sal.append(str(i[0])+"S"+str(i[1]))
        return sal

    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

class comandosUsuario(object):
    #ARMCH este es el constructor de la clase comandos usuario
    def __init__(self, comando =""):
        self.comando=comando
    #ARMCH metodo que maneja cada una de las acciones que se van a realizar por mqtt
    def accion(self):
        if self.comando == "1a":    #ARMCH aqui envia mensajes a usuarios
            topic_send = input("Ingrese el numero de usuario (Ej: '201700376', sin comillas): ")
            mensaje = input("Texto a enviar: ")
            frase_cifrada = crypt_cesar(letras,5,mensaje)
            frase_cifrada=frase_cifrada.encode()
            client.publish("usuarios/08/"+str(topic_send),frase_cifrada,1,False)
        elif self.comando == "1b":  #ARMCH aqui envia mensajes a salas
            topic_send = input("Ingrese el nombre de la sala (Ej: 'S01', sin comillas y S Mayúscula): ")
            mensaje = input("Texto a enviar: ")
            frase_cifrada = crypt_cesar(letras,5,mensaje)
            frase_cifrada=frase_cifrada.encode()
            client.publish("salas/08/"+str(topic_send),frase_cifrada,1,False)
        elif self.comando == "2a":  #ARMCH aqui envia audio a usuarios
            topic_send = input("Ingrese el usuario al que desea enviar el audio (Ej: '201700376', sin comillas): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                size= os.stat('ultimoAudio.wav').st_size
                mensaje = comandosCliente(topic_send)
                
                client.publish("comandos/08/"+str(topic_send),mensaje.fileTransfer(lista_user[0],size),1,False)
                Encriptar(getkey(PASSWORD),"ultimoAudio.wav")

            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                     
        elif self.comando == "2b":  #ARMCH aqui envia audios a salas
            topic_send = input("Ingrese la sala a la que desea enviar el audio (Ej: 'S01', sin comillas y S Mayúscula): ")
            duracion = int(input("Ingrese la duracion del audio en segundos: (Max. 30 seg)"))
            if duracion<=30:    #ARMCH si el audio es menor que 30s lo envia
                grabador = str("arecord -d "+str(duracion)+" -f U8 -r 8000 ultimoAudio.wav")
                logging.info('Comenzando la grabación')
                os.system(grabador)
                logging.info('***Grabación finalizada***')
                size= os.stat('ultimoAudio.wav').st_size
                mensaje = comandosCliente(topic_send)
                client.publish("comandos/08/"+str(topic_send),mensaje.fileTransfer(lista_user[0],size),1,False)
                Encriptar(getkey(PASSWORD),"ultimoAudio.wav")
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                
                
        elif self.comando in ["exit","EXIT"]:   #ARMCH sale del programa
            sys.exit(0)

        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")
        
        #ARMCH hace una peque;a pausa antes de volver a pedir otro comando
        logging.debug("Los datos han sido enviados al broker")            
        time.sleep(DEFAULT_DELAY)

class hilos(object):
    def __init__(self,tiempo):
        self.tiempo=tiempo
        self.hiloAlive=threading.Thread(name = 'ALIVE',
                        target = hilos.enviarALIVE,
                        args = (self,self.tiempo),
                        daemon = False
                        )
    def enviarALIVE(self, tiempo=2):
        datos = []
        user = ''
        archivo = open('usuario','r') #Abrir el archivo en modo de LECTURA
        for line in archivo: #Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #Cerrar el archivo al finalizar
        for i in datos:
            user = i[0]
        while True:
            mensaje = comandosCliente(user)
            client.publish("comandos/08/"+str(user),mensaje.alive(),1,False)
            time.sleep(self.tiempo)

class hiloAudio(object):
    def __init__(self,mensaje):
        self.mensaje=mensaje
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloAudio.reproducirAudio,
                        args = (self,self.mensaje),
                        daemon = False
                        )
    def reproducirAudio(self, mensaje):
        logging.debug(mensaje)       
        logging.info("Reproduciendo nota de voz...")
        os.system('aplay Desencriptado_recibidoEncriptado.wav')
 
class hiloTCP(object):
    def __init__(self, SERVER_IP):
        self.SERVER_IP=SERVER_IP
        self.hiloConexion=threading.Thread(name = 'Conexion por TCP',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.SERVER_IP),
                        daemon = True
                        )
        self.hiloConexionRecibir=threading.Thread(name = 'Recibiendo archivo de audio',
                        target = hiloTCP.conexionTCPrecibir,
                        args = (self,self.SERVER_IP),
                        daemon = False
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
            archivo = open('Encriptado_ultimoAudio.wav','rb')
            l=archivo.read(BUFFER_SIZE)
            while l:
                print("Enviando nota de voz...")
                sock.send(l)
                l=archivo.read(BUFFER_SIZE)
            archivo.close()
            logging.debug("Nota de voz enviada satisfactoriamente")
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
            archivo = open('recibidoEncriptado.wav', 'wb') #Aca se guarda el archivo entrante
            while buff:
                archivo.write(buff)
                buff = sock.recv(BUFFER_SIZE) #Los bloques se van agregando al archivo
            archivo.close() #Se cierra el archivo
            #sock.close() #Se cierra el socket
            logging.info("Recepcion de archivo finalizada")

        finally:
            logging.debug('Conexion al servidor finalizada')
            
            Desencriptar(getkey(PASSWORD),"recibidoEncriptado.wav")
            #os.system('aplay Desencriptado_recibidoEncriptado.wav')
            sock.close()
            hilo = hiloAudio("topic")
            hilo.hiloRecibidor.start()

def comandos_funcion(dato_entrada):
    comando_accion = comandosServidor(str(dato_entrada))
    logging.debug("Si entro a la funcion")
    if (comando_accion.separa()[0]=="02"):
        recibir_audio= hiloTCP(SERVER_IP)
        recibir_audio.hiloConexionRecibir.start()
    elif (comando_accion.separa()[0]=="04"):
        logging.debug("Se envio ALIVE al servidor")
    elif (comando_accion.separa()[0]=="06"):
        logging.info("Se recibio OK del servidor para enviar el archivo")
        #time.sleep(10)
        conexion= hiloTCP(SERVER_IP)
        conexion.hiloConexion.start()
    else:
        pass

#Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 

logging.info("Cliente MQTT con paho-mqtt") #Mensaje en consola

#SALU Iniciamos la configuracion del cliente MQTT
client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la configuracion del cliente MQTT

#************* Suscripciones del cliente *********
comandos= configuracionCLiente(USER_FILENAME,2)
lista_com=comandos.subComandos()
usuarios = configuracionCLiente(USER_FILENAME,2)
lista_user=usuarios.subUsuarios()
salas = configuracionCLiente(SALAS_FILENAME,2)
lista_sal = salas.subSalas()
logging.debug(lista_com) #muestra el usuario
logging.debug(lista_user)
logging.debug(lista_sal)
#***************************************************

hilo_enviar_Alive= hilos(2)
#hilo_enviar_Alive.hiloAlive.start()
client.loop_start()
#Loop principal:
try:
    while True: 
        #ARMCH menu principal
        print('''
        -------------------------------------------------
        |Menú:                                          |
        |1- Enviar texto                                |
        |    a. Enviar a usuario --> PRESIONE "1a"      |
        |    b. Enviar a sala    --> PRESIONE "1b"      |
        |2- Enviar mensaje de voz                       |
        |    a. Enviar a usuario --> PRESIONE "2a"      |
        |        i. Duración (Segundos)                 |
        |    b. Enviar a sala    --> PRESIONE "2b"      |
        |        i. Duración (Segundos)                 |
        |3. Salir del sistema --> PRESIONE "exit/EXIT"  |
        --------------------------------------------------
        ''') 
        
        #comando = input("Ingrese el comando: ")
        dato_usuario = input("Ingrese el comando: ")    #ARMCH el usuario ingresa un comando
        com=comandosUsuario(dato_usuario)               #ARMCH instancia del objeto instancia usuario
        com.accion()                                    #ARMCH ejecuta las acciones mqtt 

except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...")

finally:
    client.loop_stop()
    client.disconnect()
    logging.info("Se ha desconectado del broker. Saliendo...")