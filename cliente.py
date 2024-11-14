import socket as sock
import threading
import tkinter as tk
from tkinter import scrolledtext

# IP e PORTA do servidor
HOST = '172.20.10.2'
PORTA = 9999
socket_cliente = sock.socket(sock.AF_INET, sock.SOCK_STREAM) # criação de socket para se conectar com o servidor 
# Cliente solicita conexão com servidor
socket_cliente.connect((HOST, PORTA))


# ==============================================================================================================
# função para receber mensagens do servidor
# é executada por uma thread secundária,  loop que tenta receber mensagens continuamente 
# se uma mensagem é recebida, é exibida na interface grafica (CHAT_TEXT_AREA)
# se ocorrer ERRO ou DESCONEXÃO, o socket fecha e a thread é finalizada 
def recebe_mensagens():
    while True:
        try:
            mensagem = socket_cliente.recv(1024).decode() # lê ate 1024 bytes de dados DECODE decodifica os bytes para uma string
            if mensagem:
                chat_text_area.config(state='normal') #habilita area de texto para receber mensagem 
                chat_text_area.insert(tk.END, mensagem + '\n') # insere mensagem no final da area de texto e quebra a linha com /n para garantir que as mensagens fiquem separadas 
                chat_text_area.config(state='disabled') # desabilita area de texto para evitar edições 
                chat_text_area.yview(tk.END)# SCROLL automático para última mensagem recebida 
        except:
            print("Erro ao receber a mensagem... Desconectado.")
            socket_cliente.close()
            break

# ==============================================================================================================



# Função para enviar mensagem, utiliza o socket para enviar mensagens digitadas pelo usuário ao servidor.
# Executada pela thread principal, quando o user digita e envia uma mensagem 
# MSG_ENTRY é o campo de entrada da mensagem É LIMPO ÁPOS CADA ENVIO DE MENSAGEM 
# ENVIADA AO SERVIDOR USANDO  socket_cliente.sendall(mensagem.encode()) (RECEBIDA EM BITS e CONVERTE EM TEXTO)
def enviar_mensagem():
    mensagem = msg_entry.get()
    if mensagem:
        socket_cliente.sendall(mensagem.encode())
        msg_entry.delete(0, tk.END)

# =====================================================================================


# Interface gráfica com Tkinter
def iniciar_interface():
    global chat_text_area, msg_entry

    root = tk.Tk()
    root.title("Chat Cliente")

    # Área de texto para o chat
    chat_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
    chat_text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Entrada para mensagens
    msg_entry = tk.Entry(root, width=80)
    msg_entry.pack(side=tk.LEFT, padx=10, pady=5)
    msg_entry.bind("<Return>", lambda event: enviar_mensagem())

    # Botão para enviar mensagens
    enviar_btn = tk.Button(root, text="Enviar", command=enviar_mensagem)
    enviar_btn.pack(side=tk.RIGHT, padx=10, pady=5)

    # Iniciar thread para receber mensagens
    thread_receber = threading.Thread(target=recebe_mensagens)
    thread_receber.daemon = True
    thread_receber.start()

    root.mainloop()

# thread principal solicita o nome do user e envia ao servidor
nome = input("Informe seu nome para entrar no chat: ")
socket_cliente.sendall(nome.encode())

# Iniciar a interface gráfica
iniciar_interface()
