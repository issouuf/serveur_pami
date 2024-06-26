# -*- coding: utf-8 -*-
#!/usr/bin/env python
# -*- coding: utf-8 -*-
 

# coding: utf-8 

import socket
import threading
import time 
import json
import pygame 
from tqdm import tqdm
import gpiozero
import sys 

pygame.init()


#window = pygame.display.set_mode((800,600))
window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

infoObject = pygame.display.Info()
screen_width = infoObject.current_w
screen_height = infoObject.current_h


blue_button = pygame.Rect(100, 100, 200, 50)
yellow_button = pygame.Rect(500, 100, 200, 50)
start_button = pygame.Rect(300, 300, 200, 50)
quit_button = pygame.Rect(10, 10, 50, 50)





#progress_bar = pygame.Rect(100, 500, 600, 50)  # x, y, width, height
progress_bar = pygame.Rect(screen_width * 0.1, screen_height * 0.8, screen_width * 0.8, screen_height * 0.05)

font = pygame.font.Font(None, 25) 
fontstart = pygame.font.Font(None, 100)

jack = gpiozero.Button(16, pull_up=True)

running = True


HOST = 'localhost'
PORT = 6789

nbr_pami = 1

start = False    
couleur = b' '

ordre_start = (b'S') # T pour 3 secondes et S pour 90 secondes 


tcpsock = socket.socket()

# class ClientThread(threading.Thread):

#     def __init__(self, ip, port, clientsocket):

#         threading.Thread.__init__(self)
#         self.ip = ip
#         self.port = port
#         self.clientsocket = clientsocket
#         print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))

#     def run(self):   
#         global start
#         global couleur 
#         print("Connexion de %s %s" % (self.ip, self.port, ))
#         r = self.clientsocket.recv(2048)
#         message = r.decode("utf-8")
#         print("données reçues: ",message)
        #if message == ("Pami_4",'utf-8'):
        # clientsocket.sendall(b'V') 
        # while True: 
        #     if start:
        #         clientsocket.sendall(b'S')
        #         start = False
        #     if couleur != b' ':
        #         clientsocket.sendall(couleur)
        #         couleur = b' '



#Pami_num 

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(('0.0.0.0',6789))


i = 0

listClient = []

connected_clients = [0]*5

class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket
        print("[+] Nouveau thread pour %s %s" % (self.ip, self.port, ))
        split_ip = int(ip.split(".")[3])-151
        print("split_ip ",ip, " ", split_ip)
        if split_ip <= 5 and split_ip >= 0 :
            connected_clients[split_ip] = clientsocket
        print(connected_clients)
        nb = 5
        for i in connected_clients:
            if i == 0:
                nb = nb - 1
        print("Nombre de PAMIs connectés: ", nb)
            

    # def run(self):   
    #     global start
    #     global couleur 
    #     print("Connexion de %s %s" % (self.ip, self.port, ))
    #     r = self.clientsocket.recv(2048)
    #     message = r.decode("utf-8")
    #     print("données reçues: ",message)
    #     client_number = message.split("_")[1] 
    #     connected_clients.append(client_number)  
    #     try:
    #         while True: 
    #             data = self.clientsocket.recv(1024)
    #             if not data:
    #                 connected_clients.remove(client_number)
    #                 break
    #     except:
    #         connected_clients.remove(client_number)
    def run(self):   
        global start
        global couleur 
        global running
        print("Connexion de %s %s" % (self.ip, self.port, ))
        r = self.clientsocket.recv(2048)
        message = r.decode("utf-8")
        print("données reçues: ",message)
        split_message = message.split("_")
        print("Message divisé: ", split_message)
        if len(split_message) > 1:
            client_number = split_message[1] 
            #connected_clients.append(client_number)  
            print("Clients connectés: ", connected_clients)
        else:
            print("Le message reçu n'est pas de la forme attendue.")
            try:
                while running: 
                    data = self.clientsocket.recv(1024)
                    if not data:
                        split_ip = int(self.ip.split(".")[3])-151
                        connected_clients[split_ip] = 0
                        print("Client disconnected: ", self.ip)
                        print(connected_clients)
                        break
            except:
                split_ip = int(self.ip.split(".")[3])-151
                connected_clients[split_ip] = 0
                print("Client disconnected: ", self.ip)
                print(connected_clients)


class ConnectionListener(threading.Thread):
    def __init__(self, tcpsock, nbr_pami):
        threading.Thread.__init__(self)
        self.tcpsock = tcpsock
        self.nbr_pami = nbr_pami

    def run(self):
        global running
        while running:
            self.tcpsock.listen(0)
            print("En écoute...")
            (clientsocket, (ip, port)) = self.tcpsock.accept()
            newthread = ClientThread(ip, port, clientsocket)
            clientsocket.sendall(b'V')
            newthread.start()

listener = ConnectionListener(tcpsock, nbr_pami)
listener.start()




# while True:
#     tcpsock.listen(0)
#     print("En écoute...")
#     (clientsocket, (ip, port)) = tcpsock.accept()
#     newthread = ClientThread(ip, port, clientsocket)
#     clientsocket.sendall(b'V')
#     newthread.start()
#     if len(connected_clients) == nbr_pami:
#         break

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print ('Connexion vers ' + HOST + ':' + str(PORT) + ' reussie.')

def draw_connected_clients():
    font = pygame.font.Font(None, 25)  # Choose the font for the text
    y_offset = 0  # Initial y offset
    for i, client in enumerate(connected_clients, start=1):
        if client != 0:
            text = font.render(f"Pami{i}: Connecté !", True, (0, 255, 0))  # Green for connected
            pygame.draw.rect(window, (0, 0, 0), (305, 100 + y_offset, 190, 30)) 
        else:
            text = font.render(f"Pami{i}: Non Connecté !", True, (255, 0, 0))  # Red for not connected
        window.blit(text, (305, 100 + y_offset))  # Draw the text on the screen
        y_offset += 30  # Increase the y offset for the next line
        pygame.display.flip()

def ordre_PAMI(message):
    for client in connected_clients:
        if client != 0:
            client.sendall(message)

buffer= ""
while running: 
    draw_connected_clients()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if blue_button.collidepoint(event.pos):
                ordre_PAMI(b'B')
            if yellow_button.collidepoint(event.pos):
                ordre_PAMI(b'J')
            if quit_button.collidepoint(event.pos):
                running = False
                pygame.quit()
                sys.exit(0)

            #if start_button.collidepoint(event.pos):
                # for i in tqdm(range(90),desc="Progression de start",unit="s",unit_scale=True): #90
                #     pygame.draw.rect(window, (255, 255, 255), progress_bar, 2)  # Draw progress bar border
                #     pygame.draw.rect(window, (0, 255, 0), (progress_bar.x, progress_bar.y, i * (progress_bar.width / 90), progress_bar.height))  # Draw progress bar
                #     text = font.render(f"Temps restant : {90 - i} s avant depart, Progression : {i / 90 * 100:.2f}%", True, (255, 255, 255)) #90
                #     # pygame.draw.rect(window, (0,0,0), (100, 550, 500, 25))
                #     # window.blit(text, (145, 550))  # Draw the text under the progress bar.
                #     pygame.draw.rect(window, (0, 0, 0), (progress_bar.x, progress_bar.y+30, 500, 25))
                #     window.blit(text, (progress_bar.x+45, progress_bar.y+30))
                #     if i == 89: #89
                #         pygame.draw.rect(window, (0, 0, 0), progress_bar)
                #         pygame.draw.rect(window, (0, 0, 0), (progress_bar.x, progress_bar.y+30, 500, 25))
                #         text = fontstart.render("PAMIs Lancés!", True, (0, 255, 0))
                #         window.blit(text, (progress_bar.x+60, progress_bar.y))

                #     pygame.display.flip()
                #     time.sleep(1)
                #ordre_PAMI(b'S')

    if jack.value == 1:
        #time.sleep(90)
        ordre_PAMI(ordre_start) #ordre_start
        print("Start")
        pygame.draw.rect(window, (0, 0, 0), progress_bar)
        pygame.draw.rect(window, (0, 0, 0), (progress_bar.x, progress_bar.y+30, 500, 25))
        text = fontstart.render("PAMIs Lancés!", True, (0, 255, 0))
        window.blit(text, (progress_bar.x+60, progress_bar.y))
        pygame.display.flip()
        if ordre_start =='T':
            time.sleep(15)
            running = False
            pygame.quit()
        elif ordre_start == 'S':
            time.sleep(100)
            running= False
            pygame.quit()
            sys.exit(0)



    # Dessin des boutons
    pygame.draw.rect(window, (0, 0, 255), blue_button)
    pygame.draw.rect(window, (255, 255, 0), yellow_button)
    #pygame.draw.rect(window, (0, 255, 0), start_button)
    pygame.draw.rect(window, (255, 0, 0), quit_button)

    pygame.display.flip()



    # # print ('Reception...')
    # donnees = client.recv(4096) #client
    # if not donnees:
    #     continue
    # buffer += donnees.decode()
    # while "\n" in buffer:
    #     line, buffer = buffer.split("\n", 1)
    #     print(line)

    #     # print ('Recu :', donnees)
    #     data = json.loads(line)
    #     # print(data["cmd"])
    #     if data["cmd"] == "start":
    #         for i in listClient:
    #             i.sendall(b'S')
    #     if data["cmd"] == "config":
    #         config = data["data"]
    #         if config["equipe"] == "jaune":
    #             for i in listClient:
    #                 i.sendall(b'J')
    #         if config["equipe"] == "bleu" : 
    #             for i in listClient:
    #                 i.sendall(b'B')




