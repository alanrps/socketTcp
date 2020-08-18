import socket
import time
import tqdm
import os
import re

BUFFER_SIZE = 4096

class Client:
    def __init__(self, ip):
        self.ip = ip  # ip da conexão
        self.port = 7000

    def getIp(self):
        return self.ip

    def getMensagem(self):
        return self.mensagem

    def getPort(self):
        return self.port


c = Client("127.0.0.1")


addr = (c.getIp(), c.getPort())
# família do protocolo, tipo de conexão(TCP/IP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
client_socket.connect(addr)

print('''
Funções Disponíveis:

ADDFILE caminhoArquivo
DELETE nomeArquivo
GETFILESLIST
GETFILE nomeArquivo
'''
    )

while 1:
    escolha = input("Digite a sua função:")

#-------------------------------------------------------------------------------
    if(escolha.split()[0] == "EXIT"):
        client_socket.send(escolha.encode("utf-8"))
        client_socket.close()
        break

#-------------------------------------------------------------------------------
    if(escolha.split()[0] == "ADDFILE"):
        codigo =  b'\x01' # Código que indica requisição
        comando = b'\x01' # Código do comando
        tamanhoNome = len(os.path.basename(escolha.split()[1])).to_bytes(1,'big') # Códificando Tamanho do nome(INT) p/ bytes 
        filename = os.path.basename(escolha.split()[1]) # Nome arquivo
        filenameByte = os.path.basename(escolha.split()[1]).encode('utf-8') # Convertendo nome arquivo(string) p/ Byte
        
        if (os.path.isfile(escolha.split()[1]) and os.path.exists(escolha.split()[1])):
            filesize = os.path.getsize(escolha.split()[1]) # Tamanho arquivo
            filesizeByte = filesize.to_bytes(4,'big') # Convertendo Tamanho arquivo p/ Byte

            solicitacao = codigo + comando + tamanhoNome + filesizeByte + filenameByte # Concatenando Bytes 
            client_socket.send(solicitacao) # Mandando solicitação

            progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(escolha.split()[1], "rb") as f:
                for _ in progress:
                    # lê os bytes do arquivo
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        # arquivo transmitido
                        break
                    client_socket.sendall(bytes_read)
                    # atualiza a barra de progresso
                    progress.update(len(bytes_read))
                print("enviado")

                resposta = client_socket.recv(3)
                print(resposta)
                if(resposta[0] == 2 and resposta[1] == 1):
                    if(resposta[2] == 1):
                        print("Arquivo adicionado com sucesso")
                    if(resposta[2] == 2):
                        print("Arquivo já existe no servidor")
        else:
            print("Arquivo não existe")

#-------------------------------------------------------------------------------
    if(escolha.split()[0] == "DELETE"):
        codigo =  b'\x01' # Código que indica requisição
        comando = b'\x02' # Código do comando
        tamanhoNome = len(os.path.basename(escolha.split()[1])).to_bytes(1,'big') # Códificando Tamanho do nome(INT) p/ bytes 
        filenameByte = os.path.basename(escolha.split()[1]).encode('utf-8') #Códificando nome arquivo(string) p/  Bytes

        solicitacao = codigo + comando + tamanhoNome + filenameByte
        client_socket.send(solicitacao)
        print("pacote enviado")


        resposta = client_socket.recv(3)
        if(resposta[0] == 2 and resposta[1] == 1):
            if(resposta[2] == 1):
                print("Arquivo removido com sucesso")
            if(resposta[2] == 2):
                print("Erro ao remover arquivo")

#-------------------------------------------------------------------------------

    if(escolha.split()[0] == "GETFILESLIST"):
        codigo =  b'\x01' # Código que indica requisição
        comando = b'\x03' # Código do comando
        tamanhoNome = (0).to_bytes(1,'big') # Códificando Tamanho do nome(INT) p/ bytes 
        filenameByte = "".encode('utf-8') #Códificando nome arquivo(string) p/

        solicitacao = codigo + comando + tamanhoNome + filenameByte
        client_socket.send(solicitacao)
        print("pacote enviado")

        qtdeArquivosByte = client_socket.recv(2) 
        qtdeArquivos = 0
        for i in range(0,2):
            qtdeArquivos = qtdeArquivos * 256 + int(qtdeArquivosByte[i])
        
        arquivos = []
        for i in range(0, qtdeArquivos):
            resposta = client_socket.recv(1024) 
            if(resposta != b""):
                arquivos.append(resposta[1:len(resposta)].decode('utf-8'))
        
        print("Quantidade de Arquivos:",qtdeArquivos)
        print(arquivos)
        resposta = client_socket.recv(3)
        if(resposta[0] == 2 and resposta[1] == 3):
            if(resposta[2] == 1):
                print("Lista de Arquivos retornada com sucesso")
            if(resposta[2] == 2):
                print("Erro ao retornar lista de arquivos")
#-------------------------------------------------------------------------------

    if(escolha.split()[0] == "GETFILE"):
        codigo =  b'\x01' # Código que indica requisição
        comando = b'\x04' # Código do comando
        tamanhoNome = len(os.path.basename(escolha.split()[1])).to_bytes(1,'big') # Códificando Tamanho do nome(INT) p/ bytes 
        filenameByte = os.path.basename(escolha.split()[1]).encode('utf-8') 
        filename = os.path.basename(escolha.split()[1])

        solicitacao = codigo + comando + tamanhoNome + filenameByte
        client_socket.send(solicitacao)

        resposta = client_socket.recv(7) # Retorna erro caso não encontre o arquivo e caso encontre retorna o tamanho 
        print(resposta)
        if(resposta[0] == 2 and resposta[1] == 4): # Para processo caso arquivo não exista
            if(resposta[2] == 2):
                print("Arquivo não existe")
                break
        else:
            filesize = 0 # Conversão de Byte para int
            for i in range(3,7):
                filesize = filesize * 256 + int(resposta[i])
            print(filesize)
            progress = tqdm.tqdm(range(filesize) , f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
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
                print("arquivo recebido com sucesso")
            resposta = client_socket.recv(3)
            print(resposta)

            if(resposta[0] == 2 and resposta[1] == 4):
                if(resposta[2] == 1):
                    print("Arquivo baixado com sucesso")
                if(resposta[2] == 2):
                    print("Erro ao baixar arquivo")
#-------------------------------------------------------------------------------
    else:
        print("Função inválida")

    
    

    
            

