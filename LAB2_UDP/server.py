import socket
import threading
import queue

messages = queue.Queue()
clients = [] 
names = {} 

#Cezar Encryption
def caesar_encrypt(text, key=3):
    result = ""
    for c in text:
        if c.isalpha():
            shift = key % 26
            if c.isupper():
                result += chr((ord(c) - 65 + shift) % 26 + 65)
            else:
                result += chr((ord(c) - 97 + shift) % 26 + 97)
        else:
            result += c
    return result

def caesar_decrypt(text, key=3):
    return caesar_encrypt(text, -key)

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

# accept mess + store in queue
def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded = message.decode()
            print(decoded)

            if decoded.startswith("SIGNUP_TAG:"):
                name = decoded.split(":", 1)[1]
                names[addr] = name
                if addr not in clients:
                    clients.append(addr)
                for client in clients:
                    server.sendto(f"{name} joined!".encode(), client)
                continue

            if decoded.startswith("SIGNOUT_TAG:"):
                name = decoded.split(":", 1)[1]
                addr_to_remove = None
                for a, n in names.items():
                    if n == name:
                        addr_to_remove = a
                        break
                if addr_to_remove:
                    clients.remove(addr_to_remove)
                    del names[addr_to_remove]
                    print(f"[server] {name} disconnected")
                    for client_addr in clients:
                        server.sendto(f"{name} has left the chat.".encode(), client_addr)
                continue

            parts = decoded.strip().split()
            if len(parts) > 1:
                # DM
                if parts[1] == "/dm":
                    try:
                        sender = parts[0].replace(":", "")
                        target = parts[2]
                        dm_body_encrypted = " ".join(parts[3:]) 

                        found = False
                        for client_addr, client_name in names.items():
                            if client_name == target:
                                found = True
                                # criptam doar corpul dm
                                server.sendto(f"DM {sender}: {dm_body_encrypted}".encode(), client_addr)
                                # Confirmare necriptată către expeditor
                                server.sendto(f"DM to {target} | {sender}: {' '.join(parts[3:])}".encode(), addr)
                        if not found:
                            server.sendto(f"User '{target}' not found. Try /list".encode(), addr)
                    except Exception as e:
                        print("[server] DM error:", e)
                    continue

                elif parts[1] == "/list":
                    users_list = "\n".join(names.values())
                    server.sendto(users_list.encode(), addr)
                    continue

            if addr not in clients:
                clients.append(addr)
            for client_addr in clients:
                try:
                    server.sendto(message, client_addr) 
                except:
                    clients.remove(client_addr)


t1 = threading.Thread(target=receive) 
t2 = threading.Thread(target=broadcast) 

t1.start()
t2.start()