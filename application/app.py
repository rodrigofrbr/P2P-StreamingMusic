import json
import socket
from models.client import Client
from models.file import File

from tabulate import tabulate

def start_client():
    action = input("Escreva o par exclusivo 'IP:porta' para acessar o proxy: ")
    ip_adress, port = [action.split(':')[0], action.split(':')[1]]
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.connect((ip_adress, int(port)))  

    is_not_registered : bool = json.loads(_socket.recv(1024).decode())

    if(is_not_registered):
        print("Cliente não registrado.")
        username = input("Informe seu nome de usuário para continuar: ")

        new_client_data = Client(username, "", [], True)
        
        new_client = Client.to_json(new_client_data)
        _socket.send(json.dumps(new_client).encode())
    else:
        print("Cliente registrado.")

    while True:
        action = input("Digite 'LISTA' para ver os arquivos, 'ADD_FILE' para adicionar arquivos ou 'FIM' para encerrar: ")
        _socket.send(json.dumps(action).encode())
        
        if action == "LISTA":
            
            client_list_data = json.loads(_socket.recv(1024).decode())
            client_list = [Client.from_json(client_data) for client_data in client_list_data]

            for client in client_list:
                print()
                print(f"Cliente: {client.name}, Endereço: {client.address[0]}:{client.address[1]}")
                client_table = [
                    ["Nome do Arquivo", "Caminho do Arquivo"]
                ] + [
                    [client_file.name, client_file.path] for client_file in client.files
                ]
                print(tabulate(client_table, headers="firstrow", tablefmt="grid"))
                print()
            
        elif action == "ADD_FILE":
            file_name = input("Informe o nome do arquivo: ")
            file_path = input("Informe o caminho desse arquivo: ")
            file_data = File.to_json(File(file_name, file_path))

            _socket.send(json.dumps(file_data).encode())
            print(_socket.recv(1024).decode())
            
        elif action == "FIM":
            print("Encerrando conexão...")
            response = _socket.recv(1024).decode()
            print(response)
            break

    _socket.close()

start_client()