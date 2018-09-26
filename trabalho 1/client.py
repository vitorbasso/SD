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

            if command == "sair":
                self.event.set()
                self.sock.close()
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
            if len(query) >= 2 and query[1].isdigit():
                return True
        elif query[0] == "READ" or query[0] == "DELETE":
            if len(query) == 2 and query[1].isdigit():
                return True

        return False

    def receive_result(self):
        while not self.event.is_set():
            message = self.sock.recv(self.buffer_size).decode()
            if not message:
                self.event.set()
                break
            print(message)
            print("\n")
            

    @staticmethod
    def print_menu():
        print("To add a new entry type CREATE <id> <message>\n"
              "To read an entry type READ <id>\n"
              "To modify an entry type UPDATE <id> <message>\n"
              "To remove an entry type DELETE <id>\n"
              "To close type 'sair': \n")
        

    def start(self):
        display_thread = threading.Thread(target = self.receive_result)
        display_thread.setDaemon(True)
        display_thread.start()

        issue_command_thread = threading.Thread(target = self.issue_command)
        issue_command_thread.setDaemon(True)
        issue_command_thread.start()

        issue_command_thread.join()

        if display_thread.is_alive():
            print("Terminando\n\n")
            time.sleep(5)
        else:
            print("Server is down")

if __name__ == '__main__':
    cliente = Client()
    cliente.start()