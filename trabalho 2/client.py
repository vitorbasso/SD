import threading
import socket
import time


class Client:

    # =====================================================================================================================================

    # =====================================================================================================================================
    # Construtor - Inicializa as configurações e estabelece conexão com o host usando os dados em settings.txt

    def __init__(self):

        # Tenta pegar as informações do servidor de settings.txt para poder se conectar a ele - caso não haja settings.txt a conexão não será realizada
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

        # Realiza a conexão com o servidor por meio de sockets
        self.event = threading.Event()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (self.ip_address, self.port)
        self.sock.connect(self.server_address)
        print(" conected")

# =====================================================================================================================================

# =====================================================================================================================================
# Lê os comandos do usuário, os valida e, então, manda para o servidor executar

    def issue_command(self):

        while not self.event.is_set():
            self.print_instructions()
            command = input()

            if command == "sair":
                self.event.set()
                self.sock.close()
                break
            elif self.is_valid(command):
                # Se o comando for válido, envia ele para o servidor
                self.sock.send(command.encode())
            else:
                print("Invalid Command")

# =====================================================================================================================================

# =====================================================================================================================================
# Recebe os comandos do usuário e verifica se estão formatados da maneira correta para serem processados pelo servidor

    def is_valid(self, user_input):

        query = user_input.split(",")

        if query[0] == "RESTART":
            return True
        elif len(query) < 2:
            return False
        elif query[1].isdigit():

            if query[0] == "CREATE" or query[0] == "UPDATE":
                return True
            elif query[0] == "READ" or query[0] == "DELETE":
                if len(query) == 2:
                    return True
        return False


# =====================================================================================================================================

# =====================================================================================================================================
# Recebe as respostas do servidor (OK e NOK) e as exibe ao usuário

    def recv_result(self):

        while not self.event.is_set():

            server_response = self.sock.recv(self.buffer_size).decode()

            if not server_response:
                self.event.set()
                break

            print("\nSERVER RESPONSE:\n%s" % server_response)
            print("\n")

# =====================================================================================================================================

# =====================================================================================================================================
# Simples função para formatar as instruções e facilitar para outras funções as printarem

    def print_instructions(self):

        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
              "~                     INSTRUCTIONS:                     ~\n"
              "~                                                       ~\n"
              "~    * To insert a new value type CREATE <id> <value>   ~\n"
              "~                                                       ~\n"
              "~    * To modify a value type UPDATE <id> <value>       ~\n"
              "~                                                       ~\n"
              "~    * To read a value type READ <id>                   ~\n"
              "~                                                       ~\n"
              "~    * To remove a value type DELETE <id>               ~\n"
              "~                                                       ~\n"
              "~    * To close type 'sair'                             ~\n"
              "~                                                       ~\n"
              "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

# =====================================================================================================================================

# =====================================================================================================================================
# Função a ser chamada para iniciar o cliente - cria a thread de exibição e fica esperando por comandos

    def start(self):

        display_thread = threading.Thread(target=self.recv_result)
        display_thread.setDaemon(True)
        display_thread.start()

        self.issue_command()

        if display_thread.is_alive():
            print("Shutting down in 5 seconds - (waiting for late responses)\n\n")
            time.sleep(5)
        else:
            print("Server is down")

# =====================================================================================================================================

# Fim da classe Client -----------------

# =====================================================================================================================================


if __name__ == '__main__':

    cliente = Client()
    cliente.start()
