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
BUFFER_SIZE = 4096 # send 4096 bytes each time step 4096
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
            solicitacao = con.recv(1024)

            try:
                 #Função add Arquivo
                if(solicitacao[0] == 1 and solicitacao[1] == 1):
                    print("Função add arquivo")
                    filesize = 0
                    for i in range(3,7):
                        filesize = filesize * 256 + int(solicitacao[i])
                    filename = solicitacao[7:len(solicitacao)].decode('utf-8')

                    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                    with open(filename, "wb") as f:
                        for _ in progress:
                            # lê 1024 bytes vindos do servidor
                            bytes_read = con.recv(1024)
                            if len(bytes_read) < 1024:  
                                f.write(bytes_read)
                                progress.update(len(bytes_read))
                                break
                            f.write(bytes_read)
                            # atualiza a barra de progresso
                            progress.update(len(bytes_read))
                        print("Arquivo transferido com sucesso")
                        con.send(b'\x02' + b'\x01' + b'\x01')
            except:
                con.sendall(b'\x02' + b'\x01' + b'\x02')

            if(solicitacao[0] == 1 and solicitacao[1] == 2):
                print("Delete Arquivo")
                
                filename = solicitacao[3:len(solicitacao)].decode('utf-8')

                if os.path.isfile(filename):
                    os.remove(filename)
                    print("arquivo removido com sucesso")
                    con.send(b'\x02' + b'\x01' + b'\x01')
                    # con.close()
                else:
                    print("Arquivo não encontrado")
                    con.send(b'\x02' + b'\x01' + b'\x02')
                    # con.close()      
                
            
            if(solicitacao[0] == 1 and solicitacao[1] == 3):
                print("get file list")

                try:
                    count = 0
                    arquivos = os.listdir(".") # Cria lista com todos arquivos contidos no servidor
                    resposta = b''

                    qtdeBytes = len(arquivos).to_bytes(2,'big') # Quantidade de arquivos em Bytes
                    con.send(qtdeBytes)
                    
                    for arquivo in arquivos:
                        print(arquivo)
                        resposta = len(arquivo).to_bytes(1,'big') + arquivo.encode('utf-8')
                        con.send(resposta)
                        time.sleep(0.1)

                        resposta = b""
                    print("Lista de arquivos enviada com sucesso")
                    con.send(b'\x02' + b'\x03' + b'\x01')
                except:
                    print("erro ao listar arquivos")
                    con.send(b'\x02' + b'\x03' + b'\x02')
                

            if(solicitacao[0] == 1 and solicitacao[1] == 4):
                print("Get File")
                filename = solicitacao[3:len(solicitacao)].decode('utf-8')

                if (os.path.isfile(filename) and os.path.exists(filename)):
                    filesize = os.path.getsize(filename)
                    filesizeByte = filesize.to_bytes(4,'big')
                    con.send(b'\x00' + b'\x00' + b'\x00' + filesizeByte)

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
                        print("enviado realizado com sucesso")
                        time.sleep(0.1)
                        
                    con.send(b'\x02' + b'\x04' + b'\x01')
                    print(b'\x02' + b'\x04' + b'\x01')
                else:
                    print("Arquivo não existe")
                    filesizeByte = (0).to_bytes(4,'big')
                    con.send(b'\x02' + b'\x04' + b'\x02' + filesizeByte)
            
          
host = ""
port = 7000
addr = (host,port) 
serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serv_socket.bind(addr) # define para qual ip e porta deve aguardar conexão

while 1:
    serv_socket.listen(10) # limite de conexões
    (con, (ip,port) )= serv_socket.accept() # deixa o servidor escutando conexões
    novaThread = ServerThread(ip, port)
    novaThread.start()
    vetorThreads.append(novaThread)
    # solicitacao = con.recv(1024)
    # print(solicitacao.decode())
    
for t in vetorThreads: 
    t.join()
 
# recebe = con.recv(1024)
# print(solicitacao.decode("utf-8"))

serv_socket.close()
