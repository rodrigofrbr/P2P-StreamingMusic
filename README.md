# Projeto Peer-to-Peer Streaming

Este projeto consiste em uma rede peer-to-peer para fornecer arquivos de áudio em streaming, manipulando as comunicações entre cliente e servidor através de sockets. Este guia fornecerá as instruções necessárias para configurar o ambiente usando Docker.

## Pré-requisitos

- Docker instalado na sua máquina.
- Familiaridade básica com o uso de redes Docker.

## Configuração do Ambiente

Siga os passos abaixo para configurar o ambiente e executar os containers.

### 1. Criar uma rede Docker personalizada

Execute o comando abaixo para criar uma rede Docker com o IP e a máscara de sub-rede desejados. Substitua `'desired-ip'` pelo IP inicial desejado, `'desired-mask'` pela máscara da sub-rede e `'network-name'` pelo nome da rede.

```bash
docker network create --subnet='desired-ip'/'desired-mask' 'network-name'
```

### 2. Construir as imagens Docker

Construa as imagens Docker para o aplicativo e o proxy nos respectivos diretórios usando os comandos abaixo:

```bash
   docker build -t app_p2p .
   docker build -t proxy_p2p .
```

### 3. Executar os containers

Executar o container do Proxy. Substitua `'network-name'` pela rede docker criada e `'desired-ip'` pelo IP desejado dentro da rede Docker:

```bash
   docker run -it --rm --network 'network-name' --ip 'desired-ip' proxy_p2p
```
Executar o container do Aplicativo. Substitua `'network-name'` pela rede docker criada e `'desired-ip'` pelo IP desejado dentro da rede Docker:

```bash
   docker run -it --rm --network 'network-name' --ip 'desired-ip' app_p2p
```
## Notas

> ⚠️ **Atenção:** Certifique-se de que o IP fornecido para cada container está dentro do intervalo especificado pela máscara de sub-rede definida ao criar a rede.
