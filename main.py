import socket
from main_server import MainServer


server = MainServer('localhost', 4200, [])
server.start()