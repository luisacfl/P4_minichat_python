#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 18:31:03 2019

@author: luisacfl
"""

import socket
import threading
import queue
import sys
import random
import os

def ReceiveData(sock):
    while True:
        try:
            #recibe datos del socket, 1024 bytes como tamaño máximo
            data, addr = sock.recvfrom(1024)
            print(data.decode('utf-8'))
        except:
            pass

def RunClient(serverIP):
    #traduce el nombre del host a formato IPv4
    host = socket.gethostbyname("127.0.0.1")
    #proporciona un puerto random
    port = random.randint(6000, 10000)
    print('IP del cliente: '+str(host)+' Puerto: '+str(port))
    #Se establece elpuerto 5000 por default
    server = (str(serverIP),5000)
    #Crea un nuevo socket, comunicación con datagramas
    #socket.socket(Protocolo que proveen el transporte de red,Tipo de socket)
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    
    #enlaza el socket con el host y el puerto
    s.bind((host,port))
    
    #recibe el nombre del usuario
    usuario = input('Nombre de usuario: ')
    #si no recibe ningún nombre, le asigna un usuario random
    if usuario == '':
        usuario = 'Guest'+str(random.randint(1000,9999))
        print('Tu nombre de usuario es:'+usuario)
    #Imprimir el menu
    print('Ingresa alguna de las siguientes opciones:\n(1)Enviar mensaje público\n(2)Ver usuarios conectados\n(3)Enviar mensaje privado\n(4)Salir del chat')
    #envía el nombre al socket del servidor
    s.sendto(usuario.encode('utf-8'), server)
    #constructor del hilo que recibe mensajes de otros clientes
    #target es el método a ser llamado cuando se corra el hilo
    #manda el socket creado como argumento
    threading.Thread(target=ReceiveData, args=(s,)).start()
    while True:
        #recibe el mensaje
        print('Ingresa opción del menu')
        opcion = input()
        #salir del ciclo
        data = usuario
        if opcion == '1' or opcion=='3':
            print('Ingresa mensaje: ')
            mensaje = input()
            data = data+'$'+mensaje     #envía los datos al servidor junto con nombre de usuario   
            if opcion=='3':
                print('Ingresa usuario: ')
                recieverUser = input()
                data = data+'$'+recieverUser
        elif opcion=='2':
            data=data+'$'+'get-users'
        elif opcion=='4':
            data=data+'$'+'salir'
            break
        else:
            print("ingresa opción válida")
            continue;
        
        s.sendto(data.encode('utf-8'),server)
    #envía ultimo mensaje al servidor (al enviar salir)
    s.sendto(data.encode('utf-8'),server)
    #cierra el socket
    s.close()
    os._exit(1)

#Server Code
def RecvData(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

def RunServer():
    #traduce el nombre del host a formato IPv4
    host = socket.gethostbyname("127.0.0.1")
    #puerto default, 5000
    port = 5000
    print('Server hosting on IP-> '+str(host))
    #crea socket del servidor, define protocolos y comunicación por datagrama
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #enlaza socket con el host y el puerto
    s.bind((host,port))
    
    #declara variable tipo conjunto
    #solo puede tener valores unicos
    #más fácil de saber si una dirección esta contenida en el conjunto
    clients = {}
    #Clase de colas sincronizada, utlilizada para manejar los hilos
    recvPackets = queue.Queue()

    print('Server Running...')

    #crea hilo para recibir datos de los clientes
    threading.Thread(target=RecvData,args=(s,recvPackets)).start()

    while True:
        #mientras que la cola del hilos contenga hilos
        while not recvPackets.empty():
            #obtener un hilo de la cola
            data,addr = recvPackets.get()
            #obtiene nombre del usuario
            data = data.decode('utf-8')
            data = data.split("$")
            #si el cliente es nuevo solo lo agrega a la lista de clientes
            if addr not in clients.values():
                #guarda direccion y nombre de usr en un diccionario
                clients.setdefault(data[0], addr)
                continue
            #si no, recibe también sus datos
            clients.setdefault(data[0], addr)
            #si el cliente envía salir, se elimina de la lista de clientes
            if data[1].endswith('salir'):
                mensaje = data[0]+' ha abandonado la sala.'
                for c in clients:
                    if clients.get(c)!=addr:
                        s.sendto(mensaje.encode('utf-8'),clients.get(c))
                clients.pop(data[0])
                continue
            if data[1].endswith('get-users'):
                for c in clients:
                    if c!=data[0]:
                        s.sendto(c.encode('utf-8'),addr)
                continue
            #imprime la dirección de donde los recibe y los datos que recibe
            mensaje = '['+data[0]+']'+'->'+data[1]
            print(str(addr)+mensaje)
            #para cada cliente diferente de la dirección actual, 
            #envía el mensaje del cliente
            if len(data)<3:
                for c in clients:
                    if clients.get(c)!=addr:
                        s.sendto(mensaje.encode('utf-8'),clients.get(c))
            elif len(data)==3:
                s.sendto(mensaje.encode('utf-8'), clients.get(data[2]))
                
    s.close()
#Serevr Code Ends Here

if __name__ == '__main__':
    if len(sys.argv)==1:
        RunServer()
    elif len(sys.argv)==2:
        RunClient(sys.argv[1])
    else:
        print('Run Server:-> python Chat.py')
        print('Run Client:-> python Chat.py <ServerIP>')