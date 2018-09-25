import threading
import socket
import time

class Client:
    def __init__(self):
        try:
            with open("settings.txt", "r") as settings:
                i = 0
                for line in settings:
                    if i == 0:
                        self.port = int(line)
                    elif i == 1:
                        self.buffer_size = int(line)
                    else:
                        self.ip_address = line.rstrip()
                    i += 1
        except:
            pass

        print("Porta: %d, ip_address: %s" % (self.port, self.ip_address))

        self.event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ip_address, self.port)
        self.sock.connect(self.server_address)

    def issue_command(self):
        while not self.event.is_set():
            Client.print_menu()
            command = input()

            if command == "EXIT":
                self.event.set()
                break
            elif self.check_command(command):
                self.sock.send(command.encode())
            else:
                print("Invalid Command")

    
    def check_command(self, user_input):
        query = user_input.split()
        if len(query) <= 0:
            return False
        elif query[0] == "CREATE" or query[0] == "UPDATE":
            if len(query) >= 3 and query[1].isdigit():
                return True
        elif query[0] == "READ" or query[0] == "DELETE":
            if len(query) == 2 and query[1].isdigit():
                return True

        return False

    @staticmethod
    def print_menu():
        print("To add a new entry type CREATE <number> <message>\n"
              "To read an entry type READ <number>\n"
              "To modify an entry type UPDATE <number> <message>\n"
              "To remove an entry type DELETE <number>\n"
              "To close type 'sair': \n")
        


cliente = Client()
cliente.issue_command()