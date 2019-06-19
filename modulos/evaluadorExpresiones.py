#! /usr/bin/python3

#############################################################################
##                      Redes II. Gynkana Entrega 1                        ##
##   Sergio González Velázquez   Grupo: 2ºB  Lab B1   Curso: 2017 / 2018   ##
#############################################################################

"""
Este módulo ha sido implementado para utilizarlo en la segunda fase de la ginkana,
y en él se incluyen un conjunto de funciones que permiten:
	1. Comprobar que el servidor nos ha enviado una expresión correcta. Para ello, se determina si
	una expresión dada está o no balanceada. comprobando si todos los signos de apertura (paréntisis,
	llaves,corchetes) tienen su correspondiente signo de cierre.

	2. "Formatear" la expresión recibida del servidor. Dado un string que forma una expresión aritmética 
	en forma infija, ir elemento a elemento añadiendo un espacio entre ellos. Esto nos permitirá posteriormente,
	utilizar la función split() de la biblioteca estándar para dividir en trozos la expresión aritmética.

	3. Pasar de infija a postfija. Una vez formateada la expresión, utilizaremos un algoritmo
	que permite obtener una forma expresión postfija mucho más facil de calcular.

	4. Evaluar la expresión postfija y obtener el resultado. 

Para llevar a cabo estas tareas, hemos necesitado implementar unas pequeñas funciones "auxiliares" que son utilizadas
por las funciones "principales" que encapsulan cada una de las tareas mencionadas anteriormente. 

"""

from modulos.stack import Stack	
import math


#############################################################################
##                   		FUNCIONES AUXILIARES	                       ##
#############################################################################

def isOperator(c):
	if c=="+" or c=="-" or c=="*" or c=="/" or c=="^" or c=="%":
		return True
	else :
		return False

def isApertura(c):
	if c=="[" or c=="{" or c=="(":
		return True
	else :
		return False

def isCierre(c):
	if c=="]" or c==")" or c=="}":
		return True
	else :
		return False


def prioridadExpresion (op):
	if op=="+" or op=="-":
		return 1

	elif op=="*" or op=="/" or op=="%":
		return 2

	elif op=="^":
		return 4

	elif isApertura(op):
		return 5


def prioridadPila (op):
	if op=="+" or op=="-":
		return 1
	elif op=="*" or op=="/" or op=="%":
		return 2
	elif op=="^":
		return 3
	elif isApertura(op):
		return 0

def getApertura (c):
	if c==")" :
		return "("
	elif c=="}":
		return "{"
	elif c=="]": 
		return "["



#############################################################################
##                   		FUNCIONES PRINCIPALES	                       ##
#############################################################################

def isBalanceada(expresion):

	numA=0  #()
	numB=0	#{}
	numC=0	#[]

	for c in expresion:
		if c=='(':
			numA+=1
		elif c==')':
			numA-=1

		elif c=='{':
			numB+=1
		elif c== '}':
			numB-=1

		elif c=='[':
			numC+=1
		elif c==']':
			numC-=1

	if numA==0 and numB==0 and numC==0:
		return True
	else:
		return False


"""
Para "formatear" la expresión aritmética recibida del servidor partimos de que ya está balanceada.
El comportamiento de esta función se basa en ir recorriendo la expresión aritmética carácter a 
carácter, con el objetivo de separar los distintos elementos de la expresión  y añadir un espacio entre ellos 
para, posteriormente separar cada uno de estos elementos. El algoritmo hace únicamente una distinción entre carácteres:
	--> El carácter seleccionado en cada interacción es un número. Añadimos el carácter a la expresión
		resultado pero vamos a tener en cuenta el siguiente carácter. Si el siguiente carácter también es 
		un número, significa que se trata de un único elemento, y NO hay que añadir un espacio entre ambos. 
	--> Eñ carácter no es un número. Se trata entonces de un operador, espacio o sígno de apertura.
		Simplemente añadimos el carácter a la expresión resultado seguido de un espacio porque se trata de 
		dos elementos diferentes.

Finalmente, la función formatearExpresión() utiliza split( ) para retornar una lista en la que cada posición
tiene un elemento de la expresión aritmética original.  
"""
def formatearExpresion (expresionOriginal):

	expresionFormateada=""
	cont=0

	for c in expresionOriginal:
		expresionFormateada+=c

		if c.isdigit():
			if(cont+1!=len(expresionOriginal)): 
				if not(expresionOriginal[cont+1].isdigit()):
					expresionFormateada+=" "
		else:
			expresionFormateada+=" "

		cont+=1

	return expresionFormateada.split(" ")


"""


"""

def evaluar(op,num1,num2=None):
	
	res=None	

	if op=="+":
		res=num1+num2

	elif op=="-":
		if num2!=None:
			res=num1-num2
		else:
			res=-num1

	elif op=="*":
		res=num1*num2

	elif op=="/":
		res=math.floor(num1/num2) #Redondea por abajo


	elif op=="^":
		res=num1**num2

	elif op=="%":
		res=num1%num2

	return int(res)


"""
El siguiente algoritmo hace uso de una pila para convertir una expresión infija a forma posfija. Esta versión 
en python está basada en  el siguiente tutorial:
							https://www.youtube.com/watch?v=d7UZdz_yGXQ

El algoritmo hace también uso de una tabla de prioridades que específica la prioridad que tiene un operador en la 
expresión infija y la prioridad con que se añade a la expresión postfija. Esta tabla puede ver en las funciones 
definidas anteriormente prioridadPila() y prioridadExpresión(). 
Partiendo la expresión infija vamos a recorrerla elemento a elemento y formar poco a poco la expresión postfija
resultante:

	Cogemos un elemento de la expresión infija:

	 	1. Si es un número lo añadimos directamente a la expresión postfija.

	 	2. Si es un operador...

	 		a)... y la pila está vacía. Se añade directamente a la pila. 

	 		b) ... la pila no está vacía. Nos preguntamos, ¿la prioridad del operador que estamos analizando en la
	 		expresión infija es mayor que la prioridad de la cabeza de la pila en la pila?

	 			i) SI. El operador se añade a la pila.
	 			ii) NO (es menor o igual). Sacamos el tope de la pila y lo añadimos a la expresión postfija. Repetimos
	 			este proceso hasta que el tope de la pila tenga una prioridad mayor o la pila se encuentre vacía. 
	 			Una vez cumplida esa condición, metemos en la pila el operador que estabamos analizando en un primer momento.
		
		3. Es un signo de apertura. Lo tratamos igual que si fuera un operador. Como la prioridad del signo de apertura
		en la expresión es mayor que la de cualquier elemento en la pila, siempre se va a añadir a la pila.
		Nota: Cuando sacamos elementos de la pila y los añadimos a la expresión postfija (2.b.ii), los paréntesis no se añaden,
		simplemente se sacan y se descartan. 

		4. Es un signo de cierre. Sacar todos los operadores de la pila y pasarlos a la expresión postfija hasta que encontremos
		su correspondiente paréntesis de apertura en la pila, que también se saca y se descarta. 

	Finalmente, cuando hemos terminado de recorrer toda la expresión infija, si la pila no se ha quedado vacía, añadimos a la 
	expresión postfija los operadores que queden en la pila. 


"""

def pasarPostfija (expresionInfija):
	#Recibe como argumento una lista
	#Devuelve una lista

	pila=Stack()
	expresionPostfija=[]

	for c in expresionInfija:

		
		if c.isdigit():

			expresionPostfija.append(c)


		elif isOperator(c) or isApertura(c):

			#Si es el primero siempre lo apilamos
			if pila.isEmpty():
				pila.push(c)


			else:
				#Si la prioridad de c es mayor que el tope de la pila
				if prioridadExpresion(c)>prioridadPila(pila.peek()):
					pila.push(c)



				else:
				
					while not(pila.isEmpty()):
						
						if (prioridadExpresion(c)>prioridadPila(pila.peek())) or isApertura(pila.peek()):
							
							break
						else:
						
							a=pila.pop()
							expresionPostfija.append(a)
							
					pila.push(c)
				
		
		elif isCierre(c):

			aperC=getApertura(c)
			while (not(pila.isEmpty())):
				p=pila.pop()
				if not(p==aperC) :
					if not(isApertura(p)):
						expresionPostfija.append(p)
				else :
					break

	while not(pila.isEmpty()):
		a=pila.pop()
		if isOperator(a):
			expresionPostfija.append(a)

	return expresionPostfija


"""


"""
def evaluarPostfija(expresionPostfija):
#Algoritmo extraido de:
# http://quegrande.org/apuntes/EI/1/EDI/teoria/06-07/tad_-_pila_-_expresiones_aritmeticas.pdf
	
	pila=Stack() #Pila de operandos
	op1=None
	op2=None
	for i in expresionPostfija:

		if isOperator(i):
			if(pila.size()>=2):
				op2=pila.pop()
				op1=pila.pop()
				pila.push(evaluar(i,op1,op2))
			elif(pila.size()==1):
				op1=pila.pop()
				pila.push(evaluar(i,op1))

		elif i.isdigit():
			pila.push(int(i))

	return pila.peek()	

