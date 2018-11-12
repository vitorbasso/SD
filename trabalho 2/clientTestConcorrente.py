import threading
import time
import client

import grpc
import standard_pb2
import standard_pb2_grpc

class ClientTest(client.Client):

    def __init__(self):
        client.Client.__init__(self)
        self.startFrom = 0


    def issue_command(self, command):

        if self.is_valid(command):
            # Se o comando for válido, envia ele para o servidor
            response = self.CreateRequisition(command)
            if not response:
                print("Fail with requisition.\n")
            else:
                print(response.message)

            # self.sock.send(command.encode())
            # response = self.sock.recv(self.buffer_size).decode()
        elif command == "sair":
            self.event.set()
            # self.sock.close()
        else:
            print("Invalid Command")
        return response.message

    def issue_silent_command(self, command):

        if command == "sair":
            self.event.set()
            # self.sock.close()
        elif self.is_valid(command):
            response = self.CreateRequisition(command)
            # Se o comando for válido, envia ele para o servidor
            # self.sock.send(command.encode())
            #response = self.sock.recv(self.buffer_size).decode()
        else:
            print("Invalid Command")
        return response.message

    def teste1(self, start):
        #TESTE 1
 
        self.issue_command("CREATE %d I" % start)
        time.sleep(2)
        self.issue_command("READ %d" % start)
        time.sleep(2)
        self.issue_command("UPDATE %d IUPDATE" % start)
        time.sleep(2)
        self.issue_command("READ %d" % start)
        time.sleep(2)
        self.issue_command("DELETE %d" % start)

        self.startFrom += 1
        

    def teste2(self, start):
        #TESTE 2
 
        self.issue_command("CREATE %d I" % (start + (10 * 1)))
        time.sleep(2)
        self.issue_command("CREATE %d I" % (start + (10 * 1)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 2)))
        time.sleep(2)
        self.issue_command("UPDATE %d J" % (start + (10 * 2)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 2)))
        time.sleep(2)
        self.issue_command("CREATE %d J" % (start + (10 * 2)))
        time.sleep(2)
        self.issue_command("DELETE %d" % (start + (10 * 2)))

    def teste3(self, start):
        self.teste1(start)
        self.teste2(start)

        #TESTE 3
        self.issue_command("CREATE %d item 1" % (start + (10 * 3)))
        time.sleep(2)
        self.issue_command("CREATE %d item 2" % (start + (10 * 4)))
        time.sleep(2)
        self.issue_command("CREATE %d item 3" % (start + (10 * 5)))
        time.sleep(2)
        self.issue_command("CREATE %d item 4" % (start + (10 * 6)))
        time.sleep(2)
        self.issue_command("CREATE %d item 5" % (start + (10 * 7)))
        time.sleep(5)
        self.issue_command("RESTART")

    def teste4(self, start):

        self.issue_command("READ %d" % (start + (10 * 3)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 4)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 5)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 6)))
        time.sleep(2)
        self.issue_command("READ %d" % (start + (10 * 7)))
        time.sleep(2)

        self.issue_command("CREATE %d item 6" % (start + (10 * 8)))
        time.sleep(2)
        self.issue_command("CREATE %d item 7" % (start + (10 * 9)))
        time.sleep(2)
        self.issue_command("CREATE %d item 8" % (start + (10 * 10)))
        time.sleep(2)
        self.issue_command("CREATE %d item 9" % (start + (10 * 11)))
        time.sleep(2)
        self.issue_command("CREATE %d item 10" % (start + (10 * 12)))
        time.sleep(2)

        #TESTE 4
        self.issue_silent_command("CREATE %d 1" % (start + (10 * 13)))
        for i in range(start + 10 * 14,start + 10 * 14 + 1000 * 10, 10):  
            v = self.issue_silent_command("READ %d" % (i - 10))
            v = self.extract(v)
            v = int(v)       
            self.issue_silent_command("CREATE %d %d" % (i, (v + 1)))
            
            
        
        self.issue_command("READ %d" % (start + (10 * 1013)))

                
    def extract(self, v):
        v = v[v.rfind('<')+1: v.rfind('>')]
        return v
        
    def start(self, id):

        self.teste3(id)
        input("\nRESTART SERVER\n")
        self.teste4(id)
            


        print("Shutting down in 5 seconds - (waiting for late responses)\n\n")
        time.sleep(5)

  

if __name__ == '__main__':

    client_threads = []
    clients = []

    for i in range(10):
        clients.append(ClientTest())

    for i in range(10):
        client_threads.append(threading.Thread(target = clients[i].teste3, args = (i,)))
        client_threads[-1].start()

    for i in range(10):
        client_threads[i].join()

    input("\nRESTART SERVER\n")

    client_threads = []
    for i in range(10):
        client_threads.append(threading.Thread(target = clients[i].teste4, args = (i,)))
        client_threads[-1].start()

    for i in range(10):
        client_threads[i].join()
        