import socket
from threading import Thread

class  Server:
    Clients = []

    #Create a TCP socket  over IPv4 + Accept max 5 connection
    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print(f"Server started on {HOST}:{PORT}. Server wainting for connection.....")


    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from: " + str(address))

            #The first message will be the username
            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket}

            self.broadcast_mess(client_name, client_name + " has joined the chat !!!")

            Server.Clients.append(client)
            Thread(target = self.handle_new_client, args = (client,)).start()

    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        while True:
            client_message = client_socket.recv(1024).decode()
            if client_message.strip() == client_name + ": bye" or not client_message.strip():
                self.broadcast_mess(client_name, client_name + " has left the chat ! :( ")
                Server.Clients.remove(client)
                client_socket.close()
                break
            else:
                self.broadcast_mess(client_name, client_message)

    #loop through the clients and send the message down each socket
    def broadcast_mess(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_socket.send(message.encode())

if __name__ == "__main__":
    server = Server('127.0.0.1', 7632)
    server.listen()
