import socket 
from datetime import date, datetime
from threading import Thread
import os
import time
import tqdm
from threading import Thread 
from socketserver import ThreadingMixIn 
import re

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4 # send 4096 bytes each time step
vetorThreads = []

class ServerThread(Thread):
    def __init__(self,ip,port):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        print ('[+1] Novo socket thread iniciado: ' , ip , ':' , str(port)) 

    def getHost(self):
        return self.host 
    
    def getPort(self):
        return self.port
    
    def getTime(self):
        data_e_hora_atuais = datetime.now()
        data_e_hora = data_e_hora_atuais.strftime('%HH:%MM:%SS')
        return data_e_hora

    def getData(self):
        data_atual = date.today()
        data_em_texto = '{}/{}/{}'.format(data_atual.day, data_atual.month, data_atual.year)
        return data_em_texto

    def run(self): 
        while True : 
            data = con.recv(1024)
            if(data.decode() == 'EXIT'):
                break

            if(data.decode() == "DATE"):
                print(data.decode())
                con.send(self.getData().encode("utf-8"))
    
            if(data.decode() == "TIME"):
                print(data.decode())
                con.send(self.getTime().encode("utf-8"))

            if(data.decode() == "FILES"):
                arquivos = os.listdir(path = '.')
                tamanho = len(arquivos)
                
                con.send(tamanho.to_bytes(tamanho,'big'))
                time.sleep(0.1)
                i = 0
                while i < tamanho:
                    con.send(arquivos[i].encode())
                    i = i + 1
                    time.sleep(0.1)
                con.send("EXIT".encode())
                # arquivos = '\n'.join(arquivos) 
                # arquivos1 = arquivos.join("Quantidade").join(str(tamanho)).join("\n")
                # print(arquivos1)
                
            if((data.decode().split())[0] == 'DOWN'):
                filename = (data.decode().split())[1]
                
                # try:
                    # if(os.path.exists(filename)):
                        # print("Arquivo existe")
                filesize = os.path.getsize(filename)
                con.send(f"{filename}{SEPARATOR}{filesize}".encode())

                progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                with open(filename, "rb") as f:
                    for _ in progress:
                         # lê os bytes do arquivo
                        bytes_read = f.read(BUFFER_SIZE)
                        if not bytes_read:
                            # arquivo transmitido
                            break
                        con.sendall(bytes_read)
                        # atualiza a barra de progresso
                        progress.update(len(bytes_read))
                    print("enviado")
                        # if MESSAGE == 'exit':
                        #     break
                        # conn.send(MESSAGE.encode())  # echo 
                # except:
                #     print ("Arquivo não existe") 
                # finally:
                #     var = 0
                #     con.send(var.to_bytes(4,'big'))
                #     break

host = ""
port = 7000
addr = (host,port) 
serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serv_socket.bind(addr) # define para qual ip e porta deve aguardar conexão

# print ('aguardando conexao') 
# print(con,cliente) # ipServidor,portaServidor
# print ('conectado') s
# print ("aguardando mensagem")s
while 1:
    serv_socket.listen(10) # limite de conexões
    (con, (ip,port) ) = serv_socket.accept() # deixa o servidor escutando conexões
    novaThread = ServerThread(ip, port)
    novaThread.start()
    vetorThreads.append(novaThread)
    # data = con.recv(1024)
    # print(data.decode())
    
for t in vetorThreads: 
    t.join()
 
# recebe = con.recv(1024)
# print(data.decode("utf-8"))

serv_socket.close()
