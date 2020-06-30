import paho.mqtt.client as paho #ARMCH esta libreria nos permite hacer la conexion con broker mqtt
import logging              #ARMCH libreria para sustituir el print
import time                 #ARMCH    nos permite hacer pausas de tiempo
import socket               #ARMCH permite abrir un socket tcp
import random               #ARMCH nos sirve para generar numeros aleatorios de la encriptacion        
import os                   #ARMCH sirve para ejecutar comandos de bash en python
import sys                  #ARMCH Requerido para salir (sys.exit())
import threading            #ARMCH Concurrencia con hilos
from brokerdata import *    #ARMCH Informacion de la conexion
from comandos import *      #ARMCH se encarga de todas las tramas de negociacion
from encriptado import *    #ARMCH sirve para encriptar los archivos de audio
from cifradocesar import *  #ARMCH sirve para encriptar los mensajes de texto

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
        #topic_usuario="comandos/08/"+str(lista_user[0])
        if str(msg.topic) in lista_comandos_generales:
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
'''
Comentario y clase hecha por: HANC, La clase configuracionesCLiente se encarga de
suscribir al cliente en los topics necesarios para la transmision de datos de tal forma
que sea una suscripcion automatica en base a los archivos usuarios/salas.
'''
class configuracionCLiente(object):
    #HANC Constructor de la clase
    def __init__(self,filename='', qos=2):
        self.filename = filename
        self.qos = qos

    #HANC Suscripcion de comandos de Negociacion
    def subComandos(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        com=[]
        for i in datos:
            client.subscribe(("comandos/08/"+str(i[0]), self.qos))
            #logging.debug("comandos/08/"+str(i[0]))
            com.append(i[0])
        return com
    
    #HANC Suscripcion a la que llegan los mensajes
    def subUsuarios(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        user = []
        for i in datos:
            client.subscribe(("usuarios/08/"+str(i[0]), self.qos))
            #logging.debug("usuarios/08/"+str(i[0]))
            user.append(i[0])
        return user

    #HANC Suscripcion a las salas del Usuario
    def subSalas(self):
        datos = []
        archivo = open(self.filename,'r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('S')
            registro[-1] = registro[-1].replace('\n', '')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        sal =[]
        for i in datos:
            client.subscribe(("salas/"+str(i[0])+"/S"+str(i[1]), self.qos))
            client.subscribe(("comandos/"+str(i[0])+"/S"+str(i[1]), self.qos))
            #logging.debug("salas/"+str(i[0])+"/S"+str(i[1]))
            sal.append("comandos/"+str(i[0])+"/S"+str(i[1]))
        return sal

    #HANC Representacion de la clase configuracionesCLiente
    def __str__(self):
        datosMQTT="Archivo de datos: "+str(self.filename)+" qos: "+ str(self.qos)
        return datosMQTT

    def __repr__(self):
        return self.__str__

#comentario y clase hecho por ARMCH :
#esta clase se encarga de procesar las secciones que el usuario ingresa al menu principal


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
                logging.warning("ATENCION: Espere unos segundos en lo que responde el servidor")

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
                logging.warning("ATENCION: Espere unos segundos en lo que responde el servidor")
            else:
                logging.error("¡La duracion debe ser menor a 30 seg!")
                
                
        elif self.comando in ["exit","EXIT"]:   #ARMCH sale del programa
            sys.exit(0)

        else:
            logging.error("El comando ingresado es incorrecto, recuerde ver las instrucciones")
        
        #ARMCH hace una peque;a pausa antes de volver a pedir otro comando
        logging.debug("Los datos han sido enviados al broker")            
        time.sleep(DEFAULT_DELAY)
'''
Comentario y clase hecho por: HANC La clase hilos se pretende enviar el alive del cliente
para indicarle al servidor que este esta conectado.
'''

class hilos(object):
    #HANC Constructor de la clase hilos
    def __init__(self,tiempo):
        self.tiempo=tiempo
        self.hiloAlive=threading.Thread(name = 'ALIVE',
                        target = hilos.enviarALIVE,
                        args = (self,self.tiempo),
                        daemon = True
                        )

    #HANC Metodo que envia hilos cada 2 segundos
    def enviarALIVE(self, tiempo=2):
        
        datos = []
        user = ''
        archivo = open('usuario','r') #HANC Abrir el archivo en modo de LECTURA
        for line in archivo: #HANC Leer cada linea del archivo
            registro = line.split('\n')
            datos.append(registro) 
        archivo.close() #HANC Cerrar el archivo al finalizar
        for i in datos:
            user = i[0]
        mensaje = comandosCliente(user)
        while True:           
            client.publish("comandos/08/"+str(user),mensaje.alive(),2,False)
            time.sleep(self.tiempo)

#comentario y clase hecho por ARMCH
# esta clase sirve para ejecutar un hilo y reproducir un audio que le ingresa al usuario.
class hiloAudio(object):
    
    #ARMCH constructor de la clase
    def __init__(self,mensaje):
        self.mensaje=mensaje
        self.hiloRecibidor=threading.Thread(name = 'Guardar nota de voz',
                        target = hiloAudio.reproducirAudio,
                        args = (self,self.mensaje),
                        daemon = False
                        )
    #ARMCH metodo de la clase que reproduce el audio    
    def reproducirAudio(self, mensaje):
        logging.debug(mensaje)       
        logging.info("Reproduciendo nota de voz...")
        os.system('aplay Desencriptado_recibidoEncriptado.wav')


        
#clase y comentario hecho por ARMCH
#esta clase consta de dos hilos 
#un hilo para enviar los archivos de audio al servidor por medio de una conexion tcp
#otro hilo se encarga para recibir un archivo de audio del servidor por medio de la conexion tcp
class hiloTCP(object):
    #ARMCH constructor de la clase , se definen los dos hilos de la clase
    def __init__(self, SERVER_IP):
        self.SERVER_IP=SERVER_IP
        self.hiloConexion=threading.Thread(name = 'Conexion por TCP',
                        target = hiloTCP.conexionTCP,
                        args = (self,self.SERVER_IP),
                        daemon = False
                        )
    
        self.hiloConexionRecibir=threading.Thread(name = 'Recibiendo archivo de audio',
                        target = hiloTCP.conexionTCPrecibir,
                        args = (self,self.SERVER_IP),
                        daemon = False
                        )
    
    #ARMCH este metodo se encarga de enviar la nota de voz del cliente/servidor
    def conexionTCP(self, SERVER_IP):
        self.SERVER_IP   = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024
        time.sleep(5)
        #ARMCH Se crea socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #ARMCH Se conecta al puerto donde el servidor se encuentra a la escucha
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
            sock.close()
        except ConnectionRefusedError:
            logging.error("El servidor ha rechazado la conexion, intente hacerlo otra vez")
    
    #ARMCH este metodo se encarga de recibir el audio del servidor
    def conexionTCPrecibir(self,SERVER_IP):
        SERVER_ADDR = '167.71.243.238'
        SERVER_PORT = 9808
        BUFFER_SIZE = 64 * 1024
        sock = socket.socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))

        try:
            buff = sock.recv(BUFFER_SIZE)
            archivo = open('recibidoEncriptado.wav', 'wb') #ARMCH Aca se guarda el archivo entrante
            while buff:
                archivo.write(buff)
                buff = sock.recv(BUFFER_SIZE) #ARMCH Los bloques se van agregando al archivo
            archivo.close() #ARMCH Se cierra el archivo
            #sock.close() #Se cierra el socket
            logging.info("Recepcion de archivo finalizada")

        finally:
            logging.debug('Conexion al servidor finalizada')          
            Desencriptar(getkey(PASSWORD),"recibidoEncriptado.wav")                      
            hilo = hiloAudio("topic")
            hilo.hiloRecibidor.start()
            sock.close()

#ARMCH aqui se ejecutaran los comandos de negociacion que le entren al cliente
def comandos_funcion(dato_entrada):
    comando_accion = comandosServidor(str(dato_entrada))

    #ARMCH si el comando es FRR entonces abre un socket TCP para recibir el archivo
    if (comando_accion.separa()[0]=="02"):
        recibir_audio= hiloTCP(SERVER_IP)
        recibir_audio.hiloConexionRecibir.start()

    #ARMCH el comando ALIVE se envia al servidor, pero tambien le llega al cliente que lo envio
    #por el topic al que se envio, entonces aqui solo mostramos un mensaje debug que se envio el 
    #alive al servidor.
    elif (comando_accion.separa()[0]=="04"):
        logging.debug("Se envio ALIVE al servidor")
    
    #ARMCH Si el comando es OK, entonces el cliente abre un socket TCP para enviar el archivo
    #al servidor.
    elif (comando_accion.separa()[0]=="06"):
        logging.info("Se recibio OK del servidor para enviar el archivo")
        conexion= hiloTCP(SERVER_IP)
        conexion.hiloConexion.start()
    
    #ARMCH Si el comando es NO, entonces el cliente No abre el socket TCP porque el remitente
    #no esta conectado.
    elif (comando_accion.separa()[0]=="07"):
        logging.error("Se recibio NO del servidor para enviar el archivo")
        logging.error("El destinatario no esta conectado en este momento")
    
    #ARMCH si el comando es un ACK significa que el archivo se envio correctamente ó bien
    #que el servidor chequeo de manera correcta el alive.
    elif (comando_accion.separa()[0]=="05"):
        logging.debug("Se recibio ACK del servidor")
    else:
        pass    #ARMCH Por si llega un comando erroneo por cualquier razon que no haga nada

#SALU Configuracion inicial de logging
logging.basicConfig(
    level = logging.INFO, 
    format = '[%(levelname)s] (%(processName)-10s) %(message)s'
    ) 

logging.info("BIENVENIDOS A WHATSAPPBROS") #SALU Mensaje en consola

#SALU Iniciamos la configuracion del cliente MQTT
client = MQTTconfig(clean_session=True)
rc = client.run()   #SALU Corre la configuracion del cliente MQTT

#************* Suscripciones del cliente *******************************
#SALU: en este apartado suscribimos al cliente automaticamente y recopilamos
#los datos que nos serviran para los mensajes de las tramas que entren
comandos= configuracionCLiente(USER_FILENAME,2)
lista_com=comandos.subComandos()
usuarios = configuracionCLiente(USER_FILENAME,2)
lista_user=usuarios.subUsuarios()
salas = configuracionCLiente(SALAS_FILENAME,2)
lista_sal = salas.subSalas()
lista_comandos_generales=[]
lista_comandos_generales.append("comandos/08/"+str(lista_user[0]))
lista_comandos_generales.extend(lista_sal)
logging.debug(lista_comandos_generales)
#************************************************************************
client.loop_start()

#SALU comienza el hilo de ALIVE, para que envie cada cierto tiempo el alive al servidor
#OJO: usamos 120 segundos y no 2, porque mientras mas rápido se envien los alives al servidor
#mas se tarda toda la negociacion, y esto puede causar problemas en la transmision de audios.
#sabemos que es mucho tiempo, pero solo asi logramos que la negociacion no fuera tan tardada
hilo_enviar_Alive= hilos(120)
hilo_enviar_Alive.hiloAlive.start()        #SALU se activa el ALIVE


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
        |3. Salir del sistema --> PRESIONE "exit/EXIT"
        |                                               |
        | NOTA:La transmision de audios es un poco lenta|
        | por favor tenga paciencia.                    |
        -------------------------------------------------
        ''') 
        
        dato_usuario = input("Ingrese el comando: ")    #ARMCH el usuario ingresa un comando
        com=comandosUsuario(dato_usuario)               #ARMCH instancia del objeto instancia usuario
        com.accion()                                    #ARMCH ejecuta las acciones mqtt 

except KeyboardInterrupt:
    logging.warning("Desconectando del broker MQTT...") #SALU da una advertencia al desconectar del broker

finally:
    client.loop_stop()          #SALU se detiene el loop principal
    client.disconnect()         #SALU Se desconecta del broker
    logging.info("Se ha desconectado del broker. Saliendo...")  #SALU mensaje final