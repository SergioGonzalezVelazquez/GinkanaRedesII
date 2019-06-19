#!/usr/bin/python3
#############################################################################
##                           Redes II. Gynkana  	                       ##
##    Alumno: Sergio González Velázquez     Curso: 2017 / 2018             ##
#############################################################################

"""
El modulo ICMP ha sido implementado para resolver la cuarta etapa de la Ginkana y contiene
los siguientes elementos:

	-Una clase EchoRequest que permite construir un paquete ICMP Echo Request. Los atributos de esta clase
	son los diferentes campos que forman la cabecera de un mensaje ICMP. Además, contiene una función que permite
	empaquetar la cabecera del paquete una vez calculado el checksum del mismo. Con la función setPayload podemos añadir,
	ademas de una marca de tiempo, unos datos utiles al paquete. 

	-Una funcion decode EchoReply que permite desempaquetar un paquete ICMP pasado como parametro e imprimir en 
	pantalla los valores de cada uno de los campos de la cabecera y el payload del paquete.

	-Una funcion cksum que calcula la suma de comprobacion de cualquier paquete y que ha sido
	 proporcionada por David Villa.

"""

import struct, random, sys, time
from socket import htons
from string import printable

'''
cksum() es una función que calcula la suma de comprobación de cualquier paquete
ICMP. Ha sido descargada de:
https://bitbucket.org/arco_group/python-net/src/tip/raw/icmp_checksum.py
Copyright (C) 2009, 2014  David Villa Alises
'''
def cksum(data):

    def sum16(data):
        #"sum all the the 16-bit words in data"
        if len(data) % 2:
            data += bytes('\0',"ascii")

        return sum(struct.unpack("!%sH" % (len(data) // 2), data))

    retval = sum16(data)                       # sum
    retval = sum16(struct.pack('!L', retval))  # one's complement sum
    retval = (retval & 0xFFFF) ^ 0xFFFF        # one's complement
    return retval

'''

Notas

'''

class EchoRequest:
	def __init__(self):

		#ConstruirCabecera
		self.type=8 #1Byte
		self.code=0 #1Byte
		self.checksum=0#2Bytes. Se calculará una vez obtenido el payload
		self.id=random.randrange((2**16)-1)#2Bytes. Número aleatorio de 16 bits
		self.sequence=0 #2Bytes
		self.payload=None
		

	def setPayload(self,id):
		self.timestamp=time.strftime("%H:%M:%s")
		self.payload=(struct.pack("!8s",self.timestamp.encode()))+ (bytes(id,"ascii"))		

	def createPacket(self):

		header=struct.pack("!BBHHH",self.type,self.code,self.checksum,self.id,self.sequence)
				
		#B es un byte sin signo. 
		#H representa un entero de 16 bits sin signo (checksum, id, sequence)

		self.checksum=cksum(header+self.payload)
		header=struct.pack("!BBHHH",self.type,self.code,self.checksum,self.id,self.sequence)


		return header+self.payload 

	def getType(self):
		return self.type
	def getCode(self):
		return self.code
	def getChecksum(self):
		return self.checksum
	def getId(self):
		return self.id
	def getSequence(self):
		return self.sequence
	def getTimestamp(self):
		return self.timestamp



def decodeEchoReply(packet):

	#Utilizando wireshark, nos damos cuenta que los 20 primeros bytes del paquete son
	#la cabecera IP, los 8 siguientes bytes la  cabecera ICMP y por útlimo el payload.

	#Decodificamos la cabecera ICMP 
	header=packet[20:28]
	payload=packet[28:]
	headerDecode=struct.unpack("!BBHHH",header)


	#Comprobamos el cheksum del mensaje recibido
	if cksum(header+payload) == 0 :
		print("Checksum correcto")
	else:
		print("Checksum incorrecto")
		return -1
	
	
	#Imprimimos el mensaje decodificado.
	print("--> Header")
	print("\t|-Type : %d"% headerDecode[0] )
	print("\t|-Code : %d"%headerDecode[1])
	print("\t|-Checksum : %s"%hex(headerDecode[2]))
	print("\t|-Identification :%d "%headerDecode[3])
	print("\t|-Sequence Number :%d "%headerDecode[4])

	print("-->Payload:")
	print(payload.decode())


	return payload.decode()
	

	
	