#!/usr/bin/python3
"Usage: %s [<'write'>]"

#############################################################################
##                      Redes II. Gynkana Entrega 1                        ##
##   Sergio González Velázquez   Grupo: 2ºB  Lab B1   Curso: 2017 / 2018   ##
#############################################################################

'''
--> USO: El programa puede ejecutarse de dos formas, dependiendo de si queremos
almacenar las instrucciones que recibimos del servidor en un fichero de texto o 
no. Si ejecutamos el programa con "SGVGinkana.py write", se creará un fichero con el nombre
"SGVRespuestas.txt que contendrá las respuestas del servidor a cada fase. Por el contrario,
si ejecutamos el programa como "SGVGinkana.py" no se creará ningún fichero adicional"


--> VARIABLES GLOBALES. Hemos definido una serie de funciones globales que utilizamos de manera
frecuente a lo largo del código. SERVER define el nombre del servidor de la ginkana; RECV_UDP es 
un tamaño que hemos definido para que, cuando esperemos una respuesta de una conexión UDP recibamos 
todos los datos. Este número se corresponde con el máximo tamaño de datos que puede contener un paquete
UDP y se calcula conociendo el tamaño máximo de un paquete IP (65.535 bytes) a los que se les debería 
restar el tamaño de la cabecera IP (20 bytes mínimo) y el tamaño de la cabecera UDP (8 bytes).
Por otro lado, escribir controla si se deben guardar las opciones en un fichero o no dependiendo de los 
argumentos recibidos al ejecutar la aplicación.
Finalmente finFase1 es un valor booleano que se utiliza en la Fase1 para sincronizar el hilo del servidor Local
que creamos y la función principal que ejecuta dicho hilo. 


--> FUNCIONES. Las hemos clasificado en dos grupos. Por una lado, tenemos una función para la resolución
de cada una de las fases de la ginkana. Por otro lado, funciones "auxiliares" que realizan una tarea general 
que se repite varias veces o tareas que se encuentra dentro de algun fase concreta. 


--> MODULOS
		-Socket. Utilizado a lo largo de la aplicación para comunicar un programa cliente y un programa servidor.
		-evaluadorExpresiones. Incluye funciones utilizadas para resolver la segunda fase de la ginkana. 
		-ICMP. Es un modulo propio que incluye funciones para resolver la cuarta etapa. 
		-threading. Hace posible la programación de hilos. Lo utilizamos en la fase 1 para enviar una petición
		 			servidor de la gynkana indicando como conectar con nuestra servidor local mientras ya está 
		 			funcionando este servidor local. 
		-time. Utilizamos la llamada al sistema sleep para "esperar" a que el servidor Local de la fase 1 reciba las 
				instrucciones para continuar
		-os. Utilizamos la llamada al sistema _exit() para finalizar el programa.
		-sys. Utilizamos la función argv para el procesamiento la línea de ordenes.
		-random. Contiene la funcion randint para generar un numero aleatorio en un rango determinado. 


'''

from socket import *
from modulos.evaluadorExpresiones import *
from modulos.ICMP import *
import threading
from sys import argv
from time import sleep
from os import _exit
from random import randint


SERVER='atclab.esi.uclm.es'
RECV_UDP=65507
PORT_FASE0_1=2000
PORT_FASE3=5000
PORT_FASE5=9000
PORT_PROXY5=randint(7000,8000) #Puerto elegido aleatoriamente para nuestro servidor PRoxy en un rango válido
NUM_FASE=0
MAX_CHILDREN=40
escribir=None	
nombreFichero="SGVRespuestas.txt"
finFase1=False


#############################################################################
##                   		FUNCIONES AUXILIARES	                       ##
#############################################################################

def procesarLineaOrdenes():
	global escribir
	if len(argv) == 1:
		escribir=False	

	elif len(argv)==2 and argv[1]=="write":
		escribir=True
	else:
		print(__doc__ % argv[0])
		_exit(1)


def escribirFichero(msg):
	encabezado=("\n-----------------FASE %d---------------------\n"% NUM_FASE)

	if NUM_FASE==0:
		with open(nombreFichero,'w') as f:
			f.write(encabezado)
			f.write(msg)
			f.close()
	else:
		with open(nombreFichero,'a') as f:
			f.write(encabezado)
			f.write(msg)
			f.close()


def servidorFase1(puertoServidor1,msg1):
	sockServer1=socket(AF_INET, SOCK_DGRAM)
	sockServer1.bind(('',puertoServidor1))
	global finFase1
	
	print("[FASE 1 Servidor Local] Esperando instrucciones de",SERVER,":",PORT_FASE0_1)
	while 1:
		msg1[0],client=sockServer1.recvfrom(1024)
		print("[FASE 1 Servidor Local] Instrucciones recibidas")
		finFase1=True

	sockServer1.close()


def handleFase5(sock,client,n):
	print("[FASE 5 Servidor Proxy] Cliente conectado",n,client)

	peticionHTTP=sock.recv(1024).decode()
		

	print("[FASE 5 Servidor Proxy] Petición Cliente ",n," :\n",peticionHTTP)
	
	"""
	Utilizamos la función splitlines para dividir la petición HTTP en líneas
	y quedarnos con la línea en la que se indica el host (línea tercera). Una
	vez que tenemos esa línea, vamos a dividirla con la función split() tomando
	como separador los dos puntos, pues la línea tiene un formato como sigue:
	Host: www.algo.com
	Nos interesa la parte que hay después de los dos puntos. 
	Finalmente, con la función strip() lo que hacemos es eliminar los espacios en 
	blanco que se quedan al principio de la dirección.
	"""
	host=peticionHTTP.splitlines()[2].split(":")[1].strip()
	
	
	sockClient=socket(AF_INET,SOCK_STREAM)
	sockClient.connect((host,80))
	sockClient.send(peticionHTTP.encode())

	

	respuestaHTTP=""
	while 1:
		resp=sockClient.recv(1024).decode()
		if resp=="":
			break
		else :
			respuestaHTTP+=resp

	
	print("[FASE 5 Servidor Proxy] Petición cliente",n,"descargada")
	#print("[FASE 5 Servidor Proxy] Respuesta Cliente ",n," :",respuestaHTTP.decode())

	sock.sendall(respuestaHTTP.encode())
	print("[FASE 5 Servidor Proxy] Petición cliente",n,"reedirigida")



	sock.close()

def ProxyFase5(sockServerProxy5):
	##sockServerProxy5=socket(AF_INET, SOCK_STREAM)
	sockServerProxy5.bind(('',PORT_PROXY5))
	sockServerProxy5.listen(5)

	n=0
	children=[]
	
	timeout = time.time() + 20

	while 1:
		child_sock,client=sockServerProxy5.accept()
		n=n+1
		hiloConcurrente5 = threading.Thread(target=handleFase5, args=(child_sock,client,n))
		hiloConcurrente5.start()

	print("[FASE 5 Servidor Proxy] Servidor cerrado")	
	sockServerProxy5.close()





def obtenerCodigo(msg,line=0):
	id=(msg.splitlines())[line] #Retorna una lista donde cada elemento es una línea de la cadena
	return id


#############################################################################
##                   FUNCIONES QUE RESUELVEN CADA ETAPA                    ##
#############################################################################

def fase0():

	print("[Fase 0] Comienzo de la Gynkana")
	sock0=socket(AF_INET, SOCK_STREAM)
	sock0.connect((SERVER,PORT_FASE0_1))
	msg0=sock0.recv(RECV_UDP).decode()

	print("[Fase 0] Recibidas instrucciones del servidor de la Ginkana")
	id0= obtenerCodigo(msg0)
	print("[Fase 0] Código necesario para la siguiente fase:")
	print(id0,"\n")
	sock0.close()

	print("\n------------------Fase 0 completada------------------\n")

	#Solo tiene lugar cuando se ha ejecutado el programa como 'SGV-B1.py write'
	if escribir:
		escribirFichero(msg0)
		global NUM_FASE
		NUM_FASE+=1
	return id0

""" Notas sobre la Fase 1:

-Puesto que un servidor no debe iniciar la comunicación, utilizamos un hilo principal (fase1) que comunica
al servidor de la ginkana en qué puerto vamos a ejecutar nuestro servidor Local. Antes de que se produzca dicha
notificación, un hilo que ejecuta el servidor local ya ha arrancado y estará bloqueado en recvfrom().
-Además, un servidor debe permanecer abierto a la espera de peticiones. Por ello, en la función servidorFase1
utilizamos un bucle infinito que no finalizará hasta que no termine la ejecución del programa.
-La sincronización entre esta función fase1 y el servidor Local se lleva a cabo mediante la variable global
finFase1, de tal forma que la función fase1 estará esperando hasta que el servidor reciba las instrucciones y ponga
esta variable global a TRUE. En ese momento, fase1 necesitará el mensaje que ha recibido el servidor Local para continuar.
-Para poder pasar el mensaje que ha recibido el servidor Local a Fase1 utilizamos el paso por referencia.
 Es este el motivo por el que msg1 es una lista. Las listas en python se pasan por referencia.

"""

def fase1(id0):

	puertoServidor1=randint(7500,8500)
	msg1=[""] 
	hilo1 = threading.Thread(target=servidorFase1, args=(puertoServidor1,msg1))
	hilo1.start()

	peticion="%s %s" % (id0,puertoServidor1)
	sockClient1=socket(AF_INET, SOCK_DGRAM)
	sockClient1.sendto(peticion.encode(),(SERVER,PORT_FASE0_1))
	print("[FASE 1 Cliente] Petición:",repr(peticion)," enviada a",SERVER,":",PORT_FASE0_1) 

	global finFase1
	while not(finFase1):
		sleep(2)

	#Como msg1 se pasó por referencia, en esa variable tenemos el mensaje recibido por el servidor
	id1= obtenerCodigo(msg1[0].decode())
	print("[Fase 1] Código necesario para la siguiente fase:")
	print(id1,"\n")

	sockClient1.close()
	print("\n------------------Fase 1 completada------------------\n")

	if escribir:
		escribirFichero(msg1[0].decode())
		global NUM_FASE
		NUM_FASE+=1

	return id1

""" Notas sobre la Fase 2:
Para resolver esta segunda etapa hemos implementado el modulo evaluadoExpresiones.
Como no sabemos de antemano cuantas operaciones arimeticas tenemos que resolver,
nuestro cliente TCP estará en un bucle infinito del que podrá salir dadas dos condiciones:
	-Que el mensaje que recibe sea un error y no una operacion a resolver.
	-Que hayamos recibido todas las operaciones.
En cualquier otro caso, (hemos recibido una operacion), lo que tenemos que comprobar es 
si la operación ha llegado correctamente o le falta alguna parte. Para ello, hacemos uso de la 
función isBalanceada del modulo evaluadorEXPresiones.
Una vez que tenemos la expresión completa, hacemos lo siguiente:
	1- "Formatear la expresión". Consiste en añadir un espacio después de cada elemento de la operación,
								para poder utilizar la función split.
	2- Utilizando el algoritmo que se explica en el módulo, pasamos la operación (que vendrá en forma infija) a 
	forma postfija, pues consideramos que será así más fácil de resolver.
	3- Finalmente, evaluamos la expresión postfija que hemos obtenido y mandamos el resultado al servidor.
"""

def fase2(id1):

	sockClient2=socket(AF_INET, SOCK_STREAM)
	sockClient2.connect((SERVER,int(id1)))
	cont=0


	while 1:
		msg2=sockClient2.recv(1024).decode()

		if msg2.startswith("ERROR"):
			print (msg2)
			exit()
		elif (msg2.find("You passed the step 2!")!=-1): 
		#find() retorna -1 si no encuentra esa subcadena dentro del mensaje recibido
			break
		else: 
			while not (isBalanceada(msg2)):
				msg2+=sockClient2.recv(1024).decode()
			
			print("[FASE 2 SERVIDOR] Expresión artimética:",msg2)
			expresion=formatearExpresion(msg2) 
			#Función definida en el módulo EvaluadorExpresiones. Añade un espacio después de cada elemento
			expresion=pasarPostfija(expresion)
			#Función definida en el módulo EvaluadorExpresiones. Convierte la expresión formateada en postfija.
			resultado="("+str(evaluarPostfija(expresion))+")"
			#Función definida en el módulo EvaluadorExpresiones. Evalua la expresión en forma postfija
			print("[FASE 2 RESPUESTA] Resultado",resultado)
			sockClient2.sendall(resultado.encode()) 
		
	print("\n[FASE 2] Instrucciones recibidas")
	id2= obtenerCodigo(msg2)
	print("[Fase 2] Código necesario para la siguiente fase:")
	print(id2,"\n")
	print("\n------------------Fase 2 completada------------------\n")

	if escribir:
		escribirFichero(msg2)
		global NUM_FASE
		NUM_FASE+=1

	return id2

""" Notas sobre la Fase 3:
El objetivo de esta fase consiste en implementar un 'navegador web', de tal 
forma que podamos descarganos un fichero de un servidor HTTP.
Para ello, lo que haremos es conectarnos al servidor en el que se aloja el fichero
deseado a través de una conexión TCP. Una vez que la conexión haya sido aceptada,
enviaremos una petición HTTP con el metodo GET, utilizado para solicitar un recurso especifico.
Como no sabemos el tamaño que tendra el mensaje de respuesta, utilizamos un bucle.
Finalmente, imprimimos en pantalla el mensaje HTTP recibido. 
"""

def fase3(id2):
#http://www.wellho.net/resources/ex.php4?item=y303/browser.py

	sockClient3=socket(AF_INET,SOCK_STREAM)
	sockClient3.connect((SERVER,PORT_FASE3))

	peticion="GET /"+id2+ " HTTP/1.1\n\n"

	print("[FASE 3] Petición HTTP enviada: " + repr(peticion)) 
	#Rep() imprime el string tal cual, incluyendo los caracteres especiales como \n
	sockClient3.send(peticion.encode())

	msg3=""
	#Bucle para recibir todos los datos
	while True:
		resp=sockClient3.recv(1024).decode()
		if resp=="":
			break
		else :
			msg3+=resp


	sockClient3.close()

	print("\n[FASE 3] Respuesta del servidor:")
	print(msg3)
	id3= obtenerCodigo(msg3,5) #El id necesario para la sig. fase aparece en la quinta línea de la respuesta
	print("[Fase 3] Código necesario para la siguiente fase:")
	print(id3,"\n")

	print("\n------------------Fase 3 completada------------------\n")

	if escribir:
		escribirFichero(msg3)
		global NUM_FASE
		NUM_FASE+=1

	return id3


""" Notas sobre la Fase 4:
En esta cuarta fase tenemos que enviar un paquete ICMP Echo Request. Para formar el paquete ICMP basta
con crear un objeto de la clase EchoRequest, contenida en el modulo propio ICMP. COn el metodo setPayload de dicha clase
podemos añadir la carga util del paquete, en nuestro caso el id obtenido en la fase anterior. Finalmente, el metodo
createPacket se encarga de empaquetar el paquete una vez calculado el checksum.

Utilizando wireshark, nos hemos dado cuenta de que como respuesta se reciben dos mensajes de tipo ECHO Reply. Es por ello,
por lo que vamos a invocar dos veces a la funcion recv del socket RAW. 
Para cada uno de estos paquetes recibidos vamos a calcular su checksum con la funcion decodeEchoReply, y en el caso de 
haber llegado corruptos, finalizaremos el programa. 

"""

def fase4(id3):
#https://blog.adrianistan.eu/2017/05/10/mandando-paquetes-icmp-echo-personalizados-python/

	#Construcción del paquete ICMP Echo Request
	msgEchoRequest=EchoRequest()
	msgEchoRequest.setPayload(id3)
	packet=msgEchoRequest.createPacket()

	#Mostramos en pantalla el mensaje EchoRequest construido
	print("[FASE 4] Mensaje \'ICMP Echo Request\' Construido")
	print("--> Header")
	print("\t|-Type : %d" % msgEchoRequest.getType())
	print("\t|-Code : %d"% msgEchoRequest.getCode())
	print("\t|-Checksum : %d"% msgEchoRequest.getChecksum())
	print("\t|-Identification :%d "% msgEchoRequest.getId())
	print("\t|-Sequence Number : %d "% msgEchoRequest.getSequence())

	print("-->Data")
	print("\t|-Timestamp : %s " %msgEchoRequest.getTimestamp())
	print("\t|-ID : %s" % id3)

	
	socketRaw4=socket(AF_INET,SOCK_RAW,getprotobyname('icmp'))
	socketRaw4.sendto(packet, (gethostbyname(SERVER), 2000))
	print("[FASE 4] Mensaje \'ICMP Echo Request\'enviado correctamente. Esperando respuesta")

	msgEchoReply=bytearray("","utf8")
	msgEchoReply1 = socketRaw4.recv (1024)
	print("[FASE 4] Mensaje \'ICMP Echo Reply\' 1 recbido")
	payload1=decodeEchoReply(msgEchoReply1)
	msgEchoReply2 = socketRaw4.recv (2048)
	print("\n\n[FASE 4] Mensaje \'ICMP Echo Reply\' 2 recbido")
	payload2=decodeEchoReply(msgEchoReply2)

	if payload1==-1 or payload2==-1 : #decodeEchoReply devuelve -1 si el checksum es incorrecto
		print("[FASE 4] Finalizando programa")
		exit(1)

	id4=obtenerCodigo(payload2)
	print("[Fase 4] Código necesario para la siguiente fase:")
	print(id4,"\n")

	if escribir:
		escribirFichero(payload2)
		global NUM_FASE
		NUM_FASE+=1

	
	print("\n------------------Fase 4 completada------------------\n")

	return id4


""" Notas sobre la Fase 5:
En esta ultima etapa tenemos que implementar un servidor proxy que sea capaz de 
recibir concurrentemente una serie de peticiones HTTP, obtener los recursos solicitados y reenviarlos.

La funcion fase5 arranca un hilo que ejecuta la funcion sockServerProxy5, la cual modela el comportamiento 
de nuestro servidor proxy. Posteriormente, envia una peticion al servidor de la Ginkana notificando de que 
nuestro servidor proxy ya esta funcionado y esperando peticiones. El socketCliente5 se mantiene abierto porque en 
el recibiremos el ultimo mensaje si todo ha ido bien. 
Notese que, el socket del servidor proxy habia sido abierto en esta funcion y pasado como parametro de ProxyFase5. El 
motivo de esta decisión, es que cuando recibamos el ultimo mensaje a través del socket sockCLiente5, podremos cerrar
el socket del servidor, que seguirá bloqueado esperando nuevas peticiones. 

"""

def fase5(id4):

	sockServerProxy5=socket(AF_INET, SOCK_STREAM)
	hiloProxy = threading.Thread(target=ProxyFase5, args=(sockServerProxy5,))
	hiloProxy.start()

	peticionFase5="%s %s"% (id4, PORT_PROXY5)
	sockCliente5=socket(AF_INET,SOCK_STREAM)
	sockCliente5.connect((SERVER,PORT_FASE5))
	sockCliente5.send(peticionFase5.encode())
	
	print("[FASE 5 Cliente] Petición:",repr(peticionFase5),"enviada a",SERVER,":",PORT_FASE5)
	

	msgFinal=sockCliente5.recv(1024).decode()
	
	print("[FASE 5 Cliente] ",msgFinal)
	
	sockCliente5.close()
	sockServerProxy5.close()
	print("[FASE 5] Socket del Servidor Proxy cerrado")	
	
	print("\n------------------Fase 5 completada------------------\n")




#############################################################################
##                   			MAIN 					                   ##
#############################################################################

procesarLineaOrdenes()
print("-"*65)
print("|\tSergio González Velázquez \tLab B1\t 2017/2018\t|")
print("-"*65,"\n\n")

id0=fase0()
id1=fase1(id0)
id2=fase2(id1)
id3=fase3(id2)
id4=fase4(id3)
fase5(id4)

print("\n\n"+"-"*48)
print("|\t\tGINKANA COMPLETADA\t\t|")
print("-"*48,"\n\n")

_exit(0)
