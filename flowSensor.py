import os   
import sys
import AWSIoTPythonSDK     #Importa la libreria de AWSIoTPythonSDK
sys.path.insert(0, os.path.dirname(AWSIoTPythonSDK.__file__))

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient #Importa la clase que implementa el cliente MQTT
from datetime import date, datetime	#Importa la clases de tiempo
import logging
import argparse
import json


import RPi.GPIO as GPIO	#Importa la libreria de GPIO para el control de puertos de I/O
import time, sys

FLOW_SENSOR = 27	#Define el puerto de entrada del sensor de flujo de acuerdo a numeracion BMC

GPIO.setmode(GPIO.BCM)	#Define numeracion BMC para los puertos
GPIO.setup(FLOW_SENSOR, GPIO.IN, pull_up_down = GPIO.PUD_UP) #Configura el puerto 27 como de entrada con estado inicial de alto voltaje

global count	#Crea una variable global llamada count para el conteo de los pulsos enviados por el sensor
count = 0		#Inicializa la variable en Cero (0)

# AWS IoT certificate based connection
myMQTTClient = AWSIoTMQTTClient("123afhlss456")	#Crear un nombre para el cliente MQTT
myMQTTClient.configureEndpoint("a3cmxruztsldcp.iot.us-west-2.amazonaws.com", 8883)	#Punto de enlace de API REST
myMQTTClient.configureCredentials("/home/pi/AWS_Certs/root_ca.pem", "/home/pi/AWS_Certs/cloud-private.pem.key", "/home/pi/AWS_Certs/cloud-certificate.pem.crt") #Indica la ubicacion de los certificados digitales necesarios para la autenticacion del dispositivo
myMQTTClient.configureOfflinePublishQueueing(-1)  # Define una cola de "Publish" infinita
myMQTTClient.configureDrainingFrequency(2)  # 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
 
#connect and publish
myMQTTClient.connect()  #Metodo de conexion del cliente MQTT hacia el Broker
myMQTTClient.publish("thing/info", "connected", 0)

def countPulse(channel):#Metodo para el conteo de pulsos enviados por el sensor
     global count
     if start_counter == 1:
      	  count = count+1
     
GPIO.add_event_detect(FLOW_SENSOR, GPIO.FALLING, callback=countPulse)  #Define la operacion y metodo de ejecucion sobre interrpciones del sensor

while True:	#Metodo de jecucion infinito
    try:
	start_counter = 1					      
        time.sleep(1)
	now = datetime.utcnow()
    	now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ') #Metodo que establece el tiempo actual
        fluid = count * 2.6	#Calculo del volumen de liquido a partir del numero de pulsos
	print "The flow is: %.3f ml" % (fluid)	#Imprime en pantalla el valor del volumen de liquido
	payload = '{ "timestamp": "' + now_str + '","flow": ' + str(fluid) + ' }'	#Se crea el payload o dato que con el tiempo actual y el valor del volumen
	myMQTTClient.publish("thing/data", payload, 0)	#Metodo que publica el dato en el topic o tema "thing/data"
	        
    except KeyboardInterrupt:#Se ejecuta si se present una interrupcion en la ejecucion del codigo
        print '\ncaught keyboard interrupt!, bye'
        GPIO.cleanup()
        sys.exit()	#Se cierra el programa