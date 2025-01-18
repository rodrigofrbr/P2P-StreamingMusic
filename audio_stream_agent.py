import socket
import pyaudio

# Definir configurações do PyAudio para a reprodução do áudio
p = pyaudio.PyAudio()

# Definir o formato do áudio (exemplo: mono, 16-bit, 44100Hz)
FORMAT = pyaudio.paInt16  # 16 bits por amostra
CHANNELS = 2  # Stereo (2 canais)
RATE = 44100  # Taxa de amostragem (44.1 kHz)
CHUNK = 1024  # Tamanho do bloco de áudio a ser lido

# Abrir o stream de áudio para reprodução
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                frames_per_buffer=CHUNK)

# Criar o socket para escutar as conexões UDP
udp_socket_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket_server.bind(('0.0.0.0', 4200))  # Escutando na porta 12345

print("Aguardando dados de áudio...")

while True:
    # Receber dados de áudio em blocos de 1024 bytes
    data, client_address = udp_socket_server.recvfrom(CHUNK)
    print(f"Processando dados de: {client_address}")
    
    if not data:
        break
    
    # Reproduzir o áudio assim que os dados são recebidos
    stream.write(data)

    udp_socket_server.sendto(b"CTRL", client_address)


# Finalizar o stream de áudio e fechar o PyAudio
stream.stop_stream()
stream.close()
p.terminate()
udp_socket_server.close()
print("Reprodução de áudio concluída.")
