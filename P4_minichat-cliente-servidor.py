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
            data, addr = sock.recvfrom(1024)
            print(data.decode('utf-8'))
        except:
            pass

def RunClient(serverIP):
    host = socket.gethostbyname("127.0.0.1")
    port = random.randint(6000, 10000)
    print('IP del cliente: '+str(host)+' Puerto: '+str(port))
    server = (str(serverIP),5000)
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    
    usuario = input('Nombre de usuario: ')
    if usuario == '':
        usuario = 'Guest'+str(random.randint(1000,9999))
        print('Tu nombre de usuario es:'+usuario)
    s.sendto(usuario.encode('utf-8'), server)
    threading.Thread(target=ReceiveData, args=(s,)).start()
    while True:
        data = input()
        if data == 'salir':
            break
        elif data=='':
            continue
        data = '['+usuario+']' + '->'+ data
        s.sendto(data.encode('utf-8'),server)
    s.sendto(data.encode('utf-8'),server)
    s.close()
    os._exit(1)

#Server Code
def RecvData(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

def RunServer():
    host = socket.gethostbyname("127.0.0.1")
    port = 5000
    print('Server hosting on IP-> '+str(host))
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    clients = set()
    recvPackets = queue.Queue()

    print('Server Running...')

    threading.Thread(target=RecvData,args=(s,recvPackets)).start()

    while True:
        while not recvPackets.empty():
            data,addr = recvPackets.get()
            if addr not in clients:
                clients.add(addr)
                continue
            clients.add(addr)
            data = data.decode('utf-8')
            if data.endswith('qqq'):
                clients.remove(addr)
                continue
            print(str(addr)+data)
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