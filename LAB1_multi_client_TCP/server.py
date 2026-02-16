import socket
from threading import Thread

class  Server:
    Clients = []

    #Create a TCP socket  over IPv4 + Accept max 5 connection
    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print(f"Server started on {HOST}:{PORT}. Server waiting for connection.....")


    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print("Connection from: " + str(address))

            #The first message will be the username
            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket}

            self.broadcast_mess(client_name, client_name + " has joined the chat !!!")
            
            welkome_message = ("Use /dm username message for private message.")
            client['client_socket'].send(welkome_message.encode())

            self.Clients.append(client)
            Thread(target = self.handle_new_client, args = (client,)).start()

    def handle_new_client(self, client):
        client_name = client['client_name']
        client_socket = client['client_socket']
        while True:
            client_message = client_socket.recv(1024).decode()
            # Disconnect the client on bye and on empty messages
            if client_message.strip() == client_name + ": bye" or not client_message.strip():
                print("[server]", client_name, "disconnected")
                self.broadcast_mess(client_name, client_name + " has left the chat ! :( ")
                self.Clients.remove(client)
                client_socket.close()
                break
            
            # Private messages
            elif client_message.strip().split()[1] == "/dm":
                target = client_message.strip().split()[2]
                dm_body = client_message.strip().split()[3:]
                dm_body = ' '.join(dm_body)
                
                if not (target or dm_body):
                    print("[server] Error: DM refused to send")
                    continue
                
                found = False
                for client_recipient in self.Clients:
                    if client_recipient['client_name'] == target:
                        found = True
                        message_to_send = f"DM {client_name}: {dm_body}" 
                        client_recipient['client_socket'].send(message_to_send.encode())
                        # Also can send echo to the sender
                if not found:
                    user_not_found_message = f"User '{target}' not found. Try /list" 
                    client_socket.send(user_not_found_message.encode())

            else:
                print("[server]", client_message)
                self.broadcast_mess(client_name, client_message)

    #loop through the clients and send the message down each socket
    def broadcast_mess(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_socket.send(message.encode())

if __name__ == "__main__":
    server = Server('127.0.0.1', 7632)
    server.listen()

#TODO 
#Add a lock around Clients list, explain why it was added, explain why it will be fine either way
#Implement /list command
#TODO DM routing
#Optionally also send an acknowledgment/echo to the sender, e.g. "(DM to Bob) Alice: hello"
#TODO Edge cases
#What happens when?
# Self-DM
#Username collisions
#Socket of recipient disconnected