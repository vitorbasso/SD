import socket
import time

DEFAULT_PORT = 23456

class Server:
    
    def __init__(self):
        #Cria o socket TCP/IP    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #Adquiri o hostname local
        self.local_hostname = socket.gethostname()

        #Adquiri o fully qualified hostname
        self.local_fqdn = socket.getfqdn()

        #Adquiri o endereco ip
        self.ip_address = socket.gethostbyname(self.local_hostname)
        try:
            with open("settings.txt", 'r') as settings:
                for line in settings:
                    self.port = int(line)
        except IOError:
            with open("settings.txt", "w") as settings:
                input_port = int(input("First run setup - which port to use (1024 < port < 65535)?\n"))
                if not (input_port > 1024 and input_port < 65535):
                    print("Using %d instead." % DEFAULT_PORT)
                    input_port = DEFAULT_PORT
                settings.write(str(input_port))
                self.port = input_port
        else:
            pass

        #Endereco do servidor
        print("port: %s" % self.port)
        self.server_address = (self.ip_address, self.port)
        
        #Vincula a socket com a porta
        self.sock.bind(self.server_address)


if __name__ == '__main__':
    server = Server()