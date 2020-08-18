import socket 
import time
import tqdm
import os
import re

BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

class Client:
    def __init__(self, ip):
        self.ip = ip #ip da conexão
        self.port = 7000

    def getIp(self):
        return self.ip 
    
    def getMensagem(self):
        return self.mensagem

    def getPort(self):
        return self.port
    
c = Client("127.0.0.1")


addr = (c.getIp(),c.getPort()) 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #família do protocolo, tipo de conexão(TCP/IP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(addr)

while 1:
    var = input("Digite a sua entrada: ")
    if(var == "EXIT"):
        client_socket.send(var.encode("utf-8"))
        client_socket.close()
        break
    
    client_socket.send(var.encode("utf-8"))
    
    if var == "FILES":
        data = client_socket.recv(1024)
        print(int.from_bytes(data, "big"))
        while 1:
            data = client_socket.recv(1024)
            if(data.decode() != "EXIT"):
                print(data.decode())
            else:
                break

    if ((var.split())[0] == 'DOWN'):
        # if(int.from_bytes(4, 'big')):
        # data = client_socket.recv(1024)
        # falha = int.from_bytes(data, "big")
        
        # if(falha == 0):
        #     break

        received = client_socket.recv(BUFFER_SIZE).decode()
        # print()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            for _ in progress:
                # lê 1024 bytes vindos do servidor
                bytes_read = client_socket.recv(1024)
                if len(bytes_read) < 1024:  
                    f.write(bytes_read)
                    progress.update(len(bytes_read))
                    break
                f.write(bytes_read)
                # atualiza a barra de progresso
                progress.update(len(bytes_read))
            print("finalizado")

    if var == "TIME" or var == "DATE":
        data = client_socket.recv(1024)
        print(data.decode())

    
        
    
    
    

    





