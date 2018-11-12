import socket
import time
import threading
import queue
import os


# GRPC =================================================
from concurrent import futures

import grpc
import standard_pb2
import standard_pb2_grpc
# ======================================================

DEFAULT_PORT = 23456
DEFAULT_BUFFER_SIZE = 1024
DEFAULT_IP_ADDRESS = "127.0.1.1"
DEFAULT_PUBLIC_KEY = "c144efbb-c793-4d57-b6ed-7ee40321656e"
_ONE_DAY_IN_SECONDS = 60 * 60 * 24
DEFAULT_LOG_NUMBER = 0


class ServerNew(standard_pb2_grpc.StandardServicer):

    # Construtor - inicializa as configurações para estabelecer conexões sockets, cria as filas F1, F2 e F3 e o banco de dados (em memória -> dicionário do python)
    def __init__(self):

        # Cria o socket TCP/IP
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Adquiri o hostname local
        # self.local_hostname = socket.gethostname()

        # Adquiri o fully qualified hostname
        # self.local_fqdn = socket.getfqdn()

        # Adquiri o endereco ip
        # self.ip_address = socket.gethostbyname(self.local_hostname)

        input_port = DEFAULT_PORT
        input_buffer_size = DEFAULT_BUFFER_SIZE
        self.timer = None
        self.time_between_snaps = 10

        # Tenta pegar as informações port, buffer_size de settings.txt - caso não exista ele cria um novo settings.txt com os valores fornecidos ou padrões para
        # port, buffer_size e ip_address
        try:
            with open("settings.txt", 'r') as settings:
                i = 0
                for line in settings:
                    if i == 0:
                        self.port = int(line)
                    elif i == 1:
                        self.buffer_size = int(line)
                    elif i == 2:
                        #self.ip_address = line.split('\n')[0]
                        self.ip_address = line.rstrip()
                    elif i == 3:
                        self.public_key = line
                    i += 1
        except IOError:
            with open("settings.txt", "w") as settings:
                input_port = int(
                    input("First run setup - which port to use (1024 < port < 65535)?\n"))
                if not (input_port > 1024 and input_port < 65535):
                    print("Using %d instead." % DEFAULT_PORT)
                    input_port = DEFAULT_PORT
                settings.write(str(input_port))
                input_buffer_size = int(
                    input("Size for the buffer (at least 1024)?\n"))
                if not (input_buffer_size >= 1024):
                    print("Using %d instead." % DEFAULT_BUFFER_SIZE)
                    input_buffer_size = DEFAULT_BUFFER_SIZE
                settings.write("\n" + str(input_buffer_size))
                self.port = input_port
                self.buffer_size = input_buffer_size
                self.ip_address = DEFAULT_IP_ADDRESS
                self.public_key = DEFAULT_PUBLIC_KEY
                settings.write("\n" + str(self.ip_address))
                settings.write("\n" + self.public_key)
        else:
            pass

        try:
            with open("last_snap.txt", "r") as last_snap:
                for line in last_snap:
                    self.logNumber = int(line)
        except IOError:
            with open("last_snap.txt", "w") as last_snap:
                last_snap.write(str(DEFAULT_LOG_NUMBER))
                self.logNumber = DEFAULT_LOG_NUMBER
        else:
            pass

        # Endereco do servidor
        # print("port: %s, buffer-size: %s" % (self.port, self.buffer_size))
        self.server_address = self.ip_address + ":" + str(self.port)
        # print("server_address = %s, %s" % self.server_address)
        # Vincula a socket com a porta
        # self.sock.bind(self.server_address)

        # Coloca o servidor para escutar conexoes
        # self.sock.listen()

        self.event = threading.Event()

        self.recv_queue = queue.Queue(maxsize=-1)
        self.log_queue = queue.Queue(maxsize=-1)
        self.execution_queue = queue.Queue(maxsize=-1)
        self.chord_queue = queue.Queue(maxsize=-1)

        self.data_base = {}

    # Carrega o banco de dados na memória
    def loadDataBase(self):

        try:
            with open("snap." + str(self.logNumber) + ".txt", "r") as file:
                for line in file:
                    args = line.split(" ")
                    key = int(args[0])
                    data = str(" ".join(args[1:]))
                    data = data.rstrip()
                    self.data_base[key] = data
        except:
            pass

        try:

            with open("logfile." + str(self.logNumber) + ".txt", 'r') as log:
                print("Restoring from log - ")
                for line in log:
                    self.execute_command(True, line)
                print("Restored Sucessfuly!\n")

        except:
            pass

    # Recebe os comandos e o coloca em F1
    def recv_command(self, connection, client_address):

        print("\nNew connection from %s\n" % str(client_address))

        while not self.event.is_set():
            data = connection.recv(self.buffer_size).decode()
            if not data:
                break
            self.recv_queue.put((connection, client_address, data))
        connection.close()

    # Recebe os comandos GRPC e o coloca em F1
    def recv_command_grpc(self, request, context):
        print("Method: %s\n" % str(context._rpc_event.call_details.method))
        if request and str(request.key) and (request.value or request.method == "READ" or request.method == "DELETE"):
            reply = standard_pb2.StandardReply()
            self.recv_queue.put((request, context, reply))
            # TODO: Fazer método que espera enquanto requisição não está pronta.
            while not reply.message:
                pass
            return reply
        else:
            return standard_pb2.StandardReply(message="ERROR: Req NOK.\n")

    # Pega os comandos de F1 e os transporta para F2 e F3
    def transport_command(self):

        while not self.event.is_set():
            if not self.recv_queue.empty():
                request, context, reply = self.recv_queue.get()
                self.log_queue.put((request, context))
                self.execution_queue.put((request, context, reply))

    # Escreve os comandos de F2 para um arquivo log
    def log_command(self):
        while not self.event.is_set():
            if not self.log_queue.empty():
                with open("logfile." + str(self.logNumber) + ".txt", 'w') as log:
                    request, _ = self.log_queue.get()
                    if request.method != "READ":
                        log.write(request.method + ' ' + str(request.key) +
                                  ' ' + str(request.value) + "\n")
                        log.flush()

    # Executa os comandos em F3 - utilizando das funções CRUD
    def execute_command(self, set_up=False, data=""):

        while not self.event.is_set():
            if not self.execution_queue.empty() or set_up:
                if set_up == False:
                    request, context, reply = self.execution_queue.get()
                    data = str(request.method) + ' '
                    data += str(request.key) + ' '
                    data += str(request.value)

                query = data.split()
                user_command = query[0]
                key = int(query[1])
                user_data = " ".join(map(str, query[2:])) if len(
                    query) > 2 else ""

                response = ""
                server_info = ""

                # print("Comando: " + user_command)
                if user_command == "CREATE":
                    response = self.create(key, user_data)
                    server_info = "SERVER - CREATE"

                elif user_command == "READ":
                    response = self.read(key)
                    server_info = "SERVER - READ"

                elif user_command == "UPDATE":
                    response = self.update(key, user_data)
                    server_info = "SERVER - UPDATE"

                elif user_command == "DELETE":
                    response = self.delete(key)
                    server_info = "SERVER - DELETE"

                else:
                    response = "%s not a valid command." % user_command

                if not set_up:
                    server_info += " (FROM ADDRESS %s)\n" % str(
                        context._rpc_event.call_details.host)
                    print(server_info + response)
                    reply.message = response
                else:
                    break

    # Função a ser chamada para iniciar o servidor - cria as threads e começa a receber conexões

    def updateLog(self):
        self.logNumber += 1
        try:
            with open("snap." + str(self.logNumber) + ".txt", "a") as snap:
                for key in list(self.data_base.keys()):
                    snap.write(str(key) + " " + self.data_base[key] + "\n")
                snap.flush()
            if os.path.isfile("snap." + str(self.logNumber - 3) + ".txt"):
                os.remove("snap." + str(self.logNumber - 3) + ".txt")
            if os.path.isfile("last_snap.txt"):
                os.remove("last_snap.txt")
            try:
                with open("last_snap.txt" , "a" ) as last_snap:
                    last_snap.write(str(self.logNumber))
            except:
                pass
        except:
            pass

        if os.path.isfile("logfile." + str(self.logNumber - 3) + ".txt"):
            os.remove("logfile." + str(self.logNumber - 3) + ".txt")

    def snapStart(self):
        while not self.event.is_set():
            time.sleep(self.time_between_snaps)
            self.updateLog()
            
            
 
   
    def start(self):

        self.loadDataBase()

        transport_thread = threading.Thread(target=self.transport_command)
        transport_thread.setDaemon(True)
        transport_thread.start()

        log_thread = threading.Thread(target=self.log_command)
        log_thread.setDaemon(True)
        log_thread.start()

        execute_thread = threading.Thread(target=self.execute_command)
        execute_thread.setDaemon(True)
        execute_thread.start()

        snap_thread = threading.Thread(target=self.snapStart)
        snap_thread.setDaemon(True)
        snap_thread.start()

        # self.run()

    # Funções GRPC
    def Restart(self, request, context):
        if (request.public_key == self.public_key):
            print('Restarting server command.')
            self = ServerNew()
            self.start()
            return standard_pb2.StandardReply(message='OK - Restart.\n')
        else:
            return standard_pb2.StandardReply(message='NOK - Restart.\n')

    def Create(self, request, context):
        request.method = 'CREATE'
        return self.recv_command_grpc(request, context)

    def Read(self, request, context):
        request.method = 'READ'
        return self.recv_command_grpc(request, context)

    def Update(self, request, context):
        request.method = 'UPDATE'
        return self.recv_command_grpc(request, context)

    def Delete(self, request, context):
        request.method = 'DELETE'
        return self.recv_command_grpc(request, context)

    # Funções correspondentes ao CRUD
    def create(self, key, value):

        if not key in list(self.data_base.keys()):
            self.data_base[key] = value
            response = "SUCESS: key: %d - value: <%s> created\n" % (
                key, self.data_base[key])
        else:
            response = "ERROR: key already in the data base\n"

        return response

    def read(self, key):

        if key in list(self.data_base.keys()):
            response = ("key: %d - value: <%s>\n" % (key, self.data_base[key]))
        else:
            response = "ERROR: key doesnt exist in data base\n"

        return response

    def update(self, key, value):

        if key in list(self.data_base.keys()):
            self.data_base[key] = value
            response = "SUCESS: key: %d - value: <%s> updated\n" % (
                key, self.data_base[key])
        else:
            response = "ERROR: Key doesnt exist in data base\n"

        return response

    def delete(self, key):

        if key in list(self.data_base.keys()):
            response = "SUCESS: key: %d - value: <%s> deleted\n" % (
                key, self.data_base[key])
            self.data_base.pop(key)
        else:
            response = "ERROR: Key doesnt exist in data base\n"

        return response
# ======================================================
# Fim da classe Server ================================================================================================================


def onInit():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    s = ServerNew()
    s.start()
    standard_pb2_grpc.add_StandardServicer_to_server(s, server)
    print(s.server_address)
    server.add_insecure_port(s.server_address)
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    onInit()
