import json
import socket
import threading
from tabulate import tabulate
from models.client import Client
from models.file import File
import wave

def client_service():
    action = input("Escreva o par exclusivo 'IP:porta' para acessar o proxy: ")
    proxy_ip, proxy_port = action.split(':')
    _proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _proxy_socket.connect((proxy_ip, int(proxy_port)))

    is_not_registered = json.loads(_proxy_socket.recv(1024).decode())

    if is_not_registered:
        print("Cliente não registrado.")
        username = input("Informe seu nome de usuário para continuar: ")

        new_client_data = Client(username, "", [], True)
        new_client = Client.to_json(new_client_data)
        _proxy_socket.send(json.dumps(new_client).encode())
    else:
        print("Cliente registrado.")

    while True:
        action = input("Digite 'LISTA' para ver os arquivos, 'ADD_FILE' para adicionar arquivos, 'CONNECT_PEER' para obter o streaming do áudio ou 'FIM' para encerrar: ")
        _proxy_socket.send(json.dumps(action).encode())

        if action == "LISTA":
            client_list_data = json.loads(_proxy_socket.recv(1024).decode())
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

            _proxy_socket.send(json.dumps(file_data).encode())
            print(_proxy_socket.recv(1024).decode())

        elif action == "CONNECT_PEER":
            udp_socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            ip_peer = input("Informe o endereço IP do peer: ")
            file_name_peer = input("Informe o nome do arquivo do peer: ")

            udp_socket_client.sendto(file_name_peer.encode(), (ip_peer, 4200))
            print("Recebendo áudio e enviando para agente...")

            try:
                while True:
                    # Recebe os dados de áudio em blocos
                    data, _ = udp_socket_client.recvfrom(1024)
                    print("Recebendo e processando stream para agente de áudio...")
                    if data == b"END_OF_FILE":
                        break

                    # Especificamente para tratar a execucao em tempo real no docker
                    udp_socket_send.sendto(data, ('host.docker.internal', 4200))

                    try:
                        ack, _ = udp_socket_send.recvfrom(1024)
                        if ack != b"ACK":
                            udp_socket_send.sendto(data, ('host.docker.internal', 4200))
                            continue
                    except socket.timeout:
                        print("Timeout aguardando ACK. Reenviando pacote.")
                        udp_socket_send.sendto(data, ('host.docker.internal', 4200))

                    udp_socket_client.sendto(b"ACK", (ip_peer, 4201))

            except Exception as e:
                print(f"Ocorreu um erro ao receber o arquivo '{file_name_peer}': {e}")

            udp_socket_client.close()
            udp_socket_send.close()
            print("Stream de áudio concluído.")

        elif action == "FIM":
            print("Encerrando conexão...")
            response = _proxy_socket.recv(1024).decode()
            print(response)
            break

def start_client():
    udp_socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_server.bind(("0.0.0.0", 4200))

    thread = threading.Thread(target=client_service)
    thread.start()

    while True:
        data, client_address = udp_socket_server.recvfrom(1024)
        print(f"Solicitação recebida de: {client_address} para o arquivo: {data.decode()}")

        thread = threading.Thread(target=handle_udp_conn, args=(data, client_address))
        thread.start()

def handle_udp_conn(data, client_address):
    file_name = data.decode()

    udp_socket_server_file = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket_server_file.bind(("0.0.0.0", 4201))

    
    print(f"Enviando arquivo em:'{file_name}' para {client_address}")

    # Abre o arquivo em modo binário para leitura
    try:
        with open(f"./files/{file_name}", "rb") as file:
            while True:
                # Lê o arquivo em blocos de 1024 bytes
                print("Enviando stream...")
                chunk = file.read(1024)
                if not chunk:
                    break

                # Envia o bloco para o cliente
                udp_socket_server_file.sendto(chunk, client_address)

                try:
                    ack, _ = udp_socket_server_file.recvfrom(1024)
                    if ack != b"ACK":
                        udp_socket_server_file.sendto(chunk, client_address)
                        continue
                except socket.timeout:
                    print("Timeout aguardando ACK. Reenviando pacote.")
                    udp_socket_server_file.sendto(chunk, client_address)
            
    except Exception as e:
        print(f"Ocorreu um erro ao enviar o arquivo '{file_name}': {e}")

    udp_socket_server_file.sendto(b"END_OF_FILE", client_address)
    print(f"Envio do arquivo em:'{file_name}' concluído para {client_address}")
    

start_client()