import json
import socket
import threading
from models.client import Client
from models.file import File

class Proxy:
    def __init__(self, address: str, port : int, clients : list[Client]):
        self.address = address
        self.port = port
        self.clients = clients
        self.lock = threading.Lock()

    
    def handle_client(self, client : Client) -> Client:
        with self.lock:
            for existing_client in self.clients:
                if client.address[0] == existing_client.address[0]:
                    
                    if(client.name != ""):
                        existing_client.name = client.name
                    
                    existing_client.address = client.address
                    existing_client.files = existing_client.files + client.files
                    return existing_client
                
            self.clients.append(client)
            return client

        
    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.address, self.port))
        server_socket.listen(5)
        print(f"Servidor iniciado em {self.address}:{self.port}, aguardando conexões...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Novo cliente conectado: {client_address}")
            thread = threading.Thread(target=self.handle_conn, args=(client_socket, client_address))
            thread.start()

    def handle_conn(self, client_socket, client_address):
        current_client = self.handle_client(Client("", client_address, [], True))
        is_not_registered = current_client.name == ""
    
        if (is_not_registered):
            client_socket.send(json.dumps(is_not_registered).encode())
            new_client_data = json.loads(client_socket.recv(1024).decode())
            new_client = Client.from_json(new_client_data)
            new_client.address = client_address

            current_client = self.handle_client(new_client)
        else:
            client_socket.send(json.dumps(is_not_registered).encode())
        
        while True:
            request = json.loads(client_socket.recv(1024).decode())

            if request == "LISTA":
                other_clients_list = [Client.to_json(client) for client in self.clients]
                client_socket.send(json.dumps(other_clients_list).encode())

            elif request == "ADD_FILE":
                new_file_data = json.loads(client_socket.recv(1024).decode())
                new_file = File.from_json(new_file_data)
                current_client.add_file(new_file)

                client_socket.send(f"Arquivo '{new_file.name}' adicionado ao cliente {current_client.name}.".encode())

            elif request == "FIM":
                current_client.is_connected = False
                client_socket.send("Conexão encerrada.".encode())
                client_socket.close()
                print(f"Cliente {current_client.name}, endereço: {current_client.address} desconectado!")
                return

server = Proxy("0.0.0.0", 4200, [])
server.start()

