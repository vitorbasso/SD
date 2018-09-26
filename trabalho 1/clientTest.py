import threading
import socket
import time
import client

class ClientTest(client.Client):


    def issue_command(self, command):
        
        if command == "sair":
            self.event.set()
            self.sock.close()
        elif self.is_valid(command):
            #Se o comando for válido, envia ele para o servidor
            self.sock.send(command.encode())        
        else:
            print("Invalid Command")

    def auto_run(self):
        #TESTE 1
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("READ 1")
        time.sleep(2)
        self.issue_command("UPDATE 1 IUPDATE")
        time.sleep(2)
        self.issue_command("DELETE 1")
        #TESTE 2
        time.sleep(2)
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("READ 2")
        time.sleep(2)
        self.issue_command("UPDATE 2 J")
        time.sleep(2)
        self.issue_command("CREATE 2 J")
        time.sleep(2)
        self.issue_command("READ 2")
        time.sleep(2)
        self.issue_command("DELETE 2")
        #TESTE 3
        time.sleep(2)
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("CREATE 2 J")
        time.sleep(2)
        self.issue_command("CREATE 3 K")
        time.sleep(2)
        self.issue_command("CREATE 4 L")
        time.sleep(2)
        self.issue_command("CREATE 5 M")
        time.sleep(2)
                
    def start(self):

        display_thread = threading.Thread(target = self.recv_result)
        display_thread.setDaemon(True)
        display_thread.start()

        self.auto_run()

        if display_thread.is_alive():
            print("Shutting down in 5 seconds - (waiting for late responses)\n\n")
            time.sleep(5)
        else:
            print("Server is down")

  

if __name__ == '__main__':
    
    cliente = ClientTest()
    cliente.start()