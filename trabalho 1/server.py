import socket
import time
import threading
import queue

DEFAULT_PORT = 23456
DEFAULT_BUFFER_SIZE = 1024


class Server:

#=====================================================================================================================================

#=====================================================================================================================================
#Construtor - inicializa as configurações para estabelecer conexões sockets, cria as filas F1, F2 e F3 e o banco de dados (em memória -> dicionário do python)

    def __init__(self):
        
        #Cria o socket TCP/IP    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Adquiri o hostname local
        self.local_hostname = socket.gethostname()

        #Adquiri o fully qualified hostname
        self.local_fqdn = socket.getfqdn()

        #Adquiri o endereco ip
        self.ip_address = socket.gethostbyname(self.local_hostname)

        input_port = DEFAULT_PORT
        input_buffer_size = DEFAULT_BUFFER_SIZE
        try:
            with open("settings.txt", 'r') as settings:
                i = 0
                for line in settings:
                    if i == 0:
                        self.port = int(line)
                    elif i == 1:
                        self.buffer_size = int(line)
                    i += 1
        except IOError:
            with open("settings.txt", "w") as settings:
                input_port = int(input("First run setup - which port to use (1024 < port < 65535)?\n"))
                if not (input_port > 1024 and input_port < 65535):
                    print("Using %d instead." % DEFAULT_PORT)
                    input_port = DEFAULT_PORT
                settings.write(str(input_port))
                input_buffer_size = int(input("Size for the buffer (at least 1024)?\n"))
                if not (input_buffer_size >= 1024):
                    print("Using %d instead." % DEFAULT_BUFFER_SIZE)
                    input_buffer_size = DEFAULT_BUFFER_SIZE
                settings.write("\n" + str(input_buffer_size))
                self.port = input_port
                self.buffer_size = input_buffer_size
                settings.write("\n" + str(self.ip_address))
        else:
            pass

        

        #Endereco do servidor
        print("port: %s, buffer-size: %s" % (self.port, self.buffer_size))
        self.server_address = (self.ip_address, self.port)
        print("server_address = %s, %s" % self.server_address)
        #Vincula a socket com a porta
        self.sock.bind(self.server_address)

        #Coloca o servidor para escutar conexoes
        self.sock.listen()
        self.event = threading.Event()


        self.recv_queue = queue.Queue(maxsize = -1)
        self.log_queue = queue.Queue(maxsize = -1)
        self.execution_queue = queue.Queue(maxsize = -1)

        self.data_base = {}

#=====================================================================================================================================

#=====================================================================================================================================

    def loadDataBase(self):
        try:
            with open("logfile.txt", 'r') as log:
                print("Restoring from log\n")
                for line in log:
                    self.execute_command(True, line)
        except:
            pass
        
#=====================================================================================================================================

#=====================================================================================================================================
#Recebe os comandos e o coloca em F1

    def recv_command(self, connection, client_address):
        print("New connection from ", client_address)
        while not self.event.is_set():
            data = connection.recv(self.buffer_size).decode()
            if not data:
                break
            self.recv_queue.put((connection, client_address, data))
        connection.close()
#=====================================================================================================================================

#=====================================================================================================================================
#Pega os comandos de F1 e os transporta para F2 e F3

    def transport_command(self):
        while not self.event.is_set():
            if not self.recv_queue.empty():
                connection, client_address, data = self.recv_queue.get()
                self.log_queue.put((client_address, data))
                self.execution_queue.put((connection, data))
#=====================================================================================================================================

#=====================================================================================================================================
#Escreve os comandos de F2 para um arquivo log

    def log_command(self):
        with open('logfile.txt', 'a') as log:
            while not self.event.is_set():
                if not self.log_queue.empty():
                    _, data = self.log_queue.get()
                    if data.split()[0] != "READ":
                        log.write(data + "\n")
                        log.flush()
                    
#=====================================================================================================================================

#=====================================================================================================================================
#Executa os comandos em F3 - utilizando das funções CRUD

    def execute_command(self, set_up = False, data = ""):
        while not self.event.is_set():
            if not self.execution_queue.empty() or set_up:
                if set_up == False:
                    connection, data = self.execution_queue.get()
                
                query = data.split()
                user_command = query[0]
                key = int(query[1])
                user_data = " ".join(map(str, query[2:])) if len(query) > 2 else ""

                response = ""
                server_info = ""


                if user_command == "CREATE":
                    response = self.create(key, user_data)
                    server_info = "SERVER - CREATE\n"
                elif user_command == "READ":
                    response = self.read(key)
                    server_info = "SERVER - READ\nSUCESS: "
                elif user_command == "UPDATE":
                    response = self.update(key, user_data)
                    server_info = "SERVER - UPDATE\n"
                elif user_command == "DELETE":
                    response = self.delete(key)
                    server_info = "SERVER - DELETE\n"
                else:
                    response = "%s nao e um comando valido" % user_command


                if not set_up:
                    print(server_info + response)
                    connection.send(response.encode())
                else:
                    break
            
#=====================================================================================================================================

#=====================================================================================================================================

#Funções correspondentes ao CRUD

#===============================

    def create(self, key, value):
        if not key in list(self.data_base.keys()):
            self.data_base[key] = value
            response = "SUCESS: key: %d - value: <%s> created\n" % (key, self.data_base[key])
        else:
            response = "ERROR: key already in the data base\n"
        return response
#=====================

    def read(self, key):
        if key in list(self.data_base.keys()):
            response = ("key: %d - value: %s\n" % (key, self.data_base[key]))
        else:
            response = "ERROR: key doesnt exist in data base\n"
        return response
#=====================

    def update(self, key, value):
        if key in list(self.data_base.keys()):
            self.data_base[key] = value
            response = "SUCESS: key: %d - value: %s updated\n" % (key, self.data_base[key])
        else:
            response = "ERROR: Key doesnt exist in data base\n"
        return response
#=====================

    def delete(self, key):
        if key in list(self.data_base.keys()):
            response = "SUCESS: key: %d - value: %s deleted\n" % (key, self.data_base[key])
            self.data_base.pop(key)
        else:
            response = "ERROR: Key doesnt exist in data base\n"
        return response
#=====================

#=====================================================================================================================================

#=====================================================================================================================================
#Essa função é o loop principal do programa - que roda na thread inicial - ele escuta por conexões e cria threads para gerenciá-las

    def run(self):
        print("Servidor recebendo conexoes")
        while True:
            try:
                connection, client_address = self.sock.accept()
                receiveT = threading.Thread(target = self.recv_command, args = (connection, client_address))
                receiveT.setDaemon(True)
                receiveT.start()
            except KeyboardInterrupt:
                self.event.set()
                print("\nClosed by admin")
                self.sock.close()
                break

#=====================================================================================================================================1

#=====================================================================================================================================
#Função a ser chamada para iniciar o servidor - cria as threads e começa a receber conexões

    def start(self):
        self.loadDataBase()

        transport_thread = threading.Thread(target = self.transport_command)
        transport_thread.setDaemon(True)
        transport_thread.start()

        log_thread = threading.Thread(target = self.log_command)
        log_thread.setDaemon(True)
        log_thread.start()

        execute_thread = threading.Thread(target = self.execute_command)
        execute_thread.setDaemon(True)
        execute_thread.start()

        self.run()
#=====================================================================================================================================


#=====================================================================================================================================
        

if __name__ == '__main__':
    server = Server()
    server.start()