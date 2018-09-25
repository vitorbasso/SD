import socket
import time
import threading
import queue

DEFAULT_PORT = 23456
DEFAULT_BUFFER_SIZE = 1024


class Server:

#=====================================================================================================================================
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
        self.process_queue = queue.Queue(maxsize = -1)

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
                self.process_queue.put((connection, data))
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
#Executa os comandos em F3
 
    def execute_command(self, reload = False, data = ""):
        while not self.event.is_set():
            if not self.process_queue.empty() or reload:
                if reload == False:
                    _, data = self.process_queue.get()
                
                query = data.split()
                user_command = query[0]
                #key = int(query[1])
                #user_data = " ".join(map(str, query[2:])) if len(query) > 2 else ""

                #response_message = ""

                if user_command == "CREATE":
                    print("Server - CREATE")
                elif user_command == "READ":
                    print("Server - READ")
                elif user_command == "UPDATE":
                    print("Server - UPDATE")
                elif user_command == "DELETE":
                    print("Server - DELETE")
                else:
                    print("%s nao e um comando valido" % user_command)
#=====================================================================================================================================

#=====================================================================================================================================
    def main_loop(self):
        print("Servidor recebendo conexoes")
        while True:
            try:
                connection, client_address = self.sock.accept()
                workerT = threading.Thread(target = self.recv_command, args = (connection, client_address))
                workerT.setDaemon(True)
                workerT.start()
            except KeyboardInterrupt:
                self.event.set()
                print("\nClosed by admin")
                self.sock.close()
                break
#=====================================================================================================================================
    def run(self):
        enqueue_thread = threading.Thread(target = self.transport_command)
        enqueue_thread.setDaemon(True)
        enqueue_thread.start()

        execute_thread = threading.Thread(target = self.execute_command)
        execute_thread.setDaemon(True)
        execute_thread.start()

        log_thread = threading.Thread(target = self.log_command)
        log_thread.setDaemon(True)
        log_thread.start()

        self.main_loop()
#=====================================================================================================================================


#=====================================================================================================================================
        





if __name__ == '__main__':
    server = Server()
    server.run()