import socket as sock
import threading

# Função para envio de mensagens para todos os clientes (broadcast)
# função é chamada pela thread de cada cliente 
# caso ocorra um erro chama a função remover para desconetar o cliente com problemas

def broadcast(mensagem, remetente=None): #evita que o remetente receba sua mensagem 
    for cliente in lista_clientes: # percorre todos os clientes conectados 
        if cliente != remetente: #verifica se o cliente atual do loop não é o remetente 
            try:
                cliente[0].sendall(mensagem.encode()) # cliente[0] representa o socket do cliente 
                # sendall(mensagem.encode()) converte a mensagem em bytes e a envia através do socket do cliente
                # sendall() garante que a mensagem inteira será enviada
            except:
                remover(cliente) #chamado para remover o cliente problemático da lista_clientes

# ==============================================================================================================

# Função para envio de mensagens privadas (unicast)
def unicast(mensagem, remetente_socket, destinatario_nome, remetente_nome):
    # mensagem: conteudo da mensagem a ser enviado
    # remetente_socket: socket do remetente que está enviando a mensagem
    # destinatario_nome: o nome do cliente que deverá receber a mensagem
    # remetente_nome: o nome do cliente que está enviando a mensagem, para exibir ao destinatário
    for cliente in lista_clientes:
        if cliente[1] == destinatario_nome:
            try:
                cliente[0].sendall(f"[Privado] {remetente_nome} >> {mensagem}".encode())
                # cliente[0] representa o socket do destinatário
                # sendall() envia a mensagem convertida em bytes com .encode()

                remetente_socket.sendall(f"[Privado para {destinatario_nome}] {mensagem}".encode())
                # envia a mensagem para o socket do remetente
                # informa o remetente que a mensagem foi enviada para o (destinatario_nome), junto com o conteudo da mensagem
                return
            except:
                remover(cliente)
    remetente_socket.sendall(f"Usuário {destinatario_nome} não encontrado.".encode())

# =================================================================================================================

# Função para remoção de clientes da lista
def remover(cliente):
    if cliente in lista_clientes:
        lista_clientes.remove(cliente)
        broadcast(f"{cliente[1]} saiu do chat.") # após a remoção o servidor envia uma mensagem broadcast informando quem saiu 
        atualizar_lista_conectados() #é chamada, e nela é exibido os users conectados 

# =========================================================================================================

# Função para atualizar e enviar a lista de clientes conectados a todos os clientes
# função que é chamada acima na funçao remover()
def atualizar_lista_conectados():
    clientes_conectados = "Usuários conectados: " + ", ".join([cliente[1] for cliente in lista_clientes])
    for cliente in lista_clientes:
        try:
            cliente[0].sendall(clientes_conectados.encode())
        except:
            remover(cliente)

# ===============================================================================================

# Função para recebimento de dados dos clientes
# executada por uma thread individual para cada cliente
def recebe_dados(sock_cliente, endereco):
    # Receber o nome do cliente
    nome = sock_cliente.recv(50).decode() # lê até 50 bytes do socket do cliente 
    lista_clientes.append((sock_cliente, nome))
    print(f"Conexão bem sucedida com {nome} via endereço: {endereco}")
    
    # Notificar todos sobre o novo cliente e atualizar lista de conectados
    broadcast(f"{nome} entrou no chat.")
    atualizar_lista_conectados()
    
    while True:
        try:
            mensagem = sock_cliente.recv(1024).decode()
            if mensagem.startswith("@"):
                destinatario, mensagem_privada = mensagem[1:].split(' ', 1)
                unicast(mensagem_privada, sock_cliente, destinatario, nome)
            else:
                broadcast(f"{nome} >> {mensagem}", sock_cliente)
        except:
            print(f"{nome} foi desconectado.")
            remover((sock_cliente, nome))
            sock_cliente.close()
            return

# Configuração do servidor
HOST = '172.20.10.3'
PORTA = 9999
lista_clientes = []
sock_server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
sock_server.bind((HOST, PORTA))
sock_server.listen() # permite que vários clientes se conectem ao servidor.
print(f"O servidor {HOST}:{PORTA} está aguardando conexões...")
# Loop principal do servidor para aceitar conexões
while True:
    sock_conn, ender = sock_server.accept() # Para cada novo cliente que se conecta, o servidor aceita a conexão (sock_server.accept()) e inicia uma thread dedicada para atender esse cliente, chamando a função recebe_dados
    thread_cliente = threading.Thread(target=recebe_dados, args=[sock_conn, ender])
    thread_cliente.start()
