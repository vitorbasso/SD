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
            response = self.sock.recv(self.buffer_size).decode()
            print(response) 
        else:
            print("Invalid Command")

    def teste1(self):
        #TESTE 1
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("READ 1")
        time.sleep(2)
        self.issue_command("UPDATE 1 IUPDATE")
        time.sleep(2)
        self.issue_command("READ 1")
        time.sleep(2)
        self.issue_command("DELETE 1")
        

    def teste2(self):
        #TESTE 2
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("CREATE 1 I")
        time.sleep(2)
        self.issue_command("READ 2")
        time.sleep(2)
        self.issue_command("UPDATE 2 J")
        time.sleep(2)
        self.issue_command("READ 2")
        time.sleep(2)
        self.issue_command("CREATE 2 J")
        time.sleep(2)
        self.issue_command("DELETE 2")

    def teste3(self):
        #TESTE 3
        self.issue_command("CREATE 1 item 1")
        time.sleep(2)
        self.issue_command("CREATE 2 item 2")
        time.sleep(2)
        self.issue_command("CREATE 3 item 3")
        time.sleep(2)
        self.issue_command("CREATE 4 item 4")
        time.sleep(2)
        self.issue_command("CREATE 5 item 5")
        time.sleep(5)

        self.sock.close()
        input("\nRESTART SERVER\n")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.server_address))

        self.issue_command("READ 1")
        time.sleep(2)
        self.issue_command("READ 2")
        time.sleep(2)
        self.issue_command("READ 3")
        time.sleep(2)
        self.issue_command("READ 4")
        time.sleep(2)
        self.issue_command("READ 5")
        time.sleep(2)

        self.issue_command("CREATE 6 item 6")
        time.sleep(2)
        self.issue_command("CREATE 7 item 7")
        time.sleep(2)
        self.issue_command("CREATE 8 item 8")
        time.sleep(2)
        self.issue_command("CREATE 9 item 9")
        time.sleep(2)
        self.issue_command("CREATE 10 item 10")
        time.sleep(2)

    def teste4(self):
        print("oi")


        


    
    def print_choice(self):
        print("Qual teste fazer\n"
              "1 - CRUD OK\n"
              "2 - CRUD NOK\n"
              "3 - Recuperação de estado (deletar o log antes)\n"
              "4 - Ordem de execução (deletar o log antes)\n")
                
    def start(self):

        self.print_choice()
        choice = int(input())

        if choice == 1:
            self.teste1()
        elif choice == 2:
            self.teste2()
        elif choice == 3:
            self.teste3()
        elif choice == 4:
            self.teste3()
        else:
            print("\nInvalido\n")
            


        print("Shutting down in 5 seconds - (waiting for late responses)\n\n")
        time.sleep(5)

  

if __name__ == '__main__':
    
    cliente = ClientTest()
    cliente.start()