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
    #envía el nombre al socket del servidor
    s.sendto(usuario.encode('utf-8'), server)
    #constructor del hilo que recibe mensajes de otros clientes
    #target es el método a ser llamado cuando se corra el hilo
    #manda el socket creado como argumento
    threading.Thread(target=ReceiveData, args=(s,)).start()
    while True:
        #recibe el mensaje
        data = input()
        #salir del ciclo
        if data == 'salir':
            break
        elif data=='':
            continue
        data = '['+usuario+']' + '->'+ data
        #envía los datos al servidor junto con nombre de usuario
        s.sendto(data.encode('utf-8'),server)
    #envía ultimo mensaje al servidor ('salir')
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
    clients = set()
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
            #si el cliente es nuevo solo lo agrega a la lista de clientes
            if addr not in clients:
                clients.add(addr)
                print("first client"+addr)
                continue
            #si no, recibe también sus datos
            clients.add(addr)
            data = data.decode('utf-8')
            #si el cliente envía salir, se elimina de la lista de clientes
            if data.endswith('salir'):
                clients.remove(addr)
                continue
            #imprime la dirección de donde los recibe y los datos que recibe
            print(str(addr)+data)
            #para cada cliente diferente de la dirección actual, 
            #envía el mensaje del cliente
            for c in clients:
                if c!=addr:
                    s.sendto(data.encode('utf-8'),c)
    s.close()
#Serevr Code Ends Here

if __name__ == '__main__':
    if len(sys.argv)==1:
        RunServer()
    elif len(sys.argv)==2:
        RunClient(sys.argv[1])
    else:
        print('Run Serevr:-> python Chat.py')
        print('Run Client:-> python Chat.py <ServerIP>')