import socket
import threading
import random

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

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind(("localhost", random.randint(8000, 9000)))

name = input("Nickname: ")

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024) 
            decoded = message.decode()

            # dm decriptate
            if decoded.startswith("DM"):
                try:
                    prefix, encrypted = decoded.split(":", 1)
                    decrypted = caesar_decrypt(encrypted.strip())
                    print("\033[1;32;40m" + f"{prefix}: {decrypted}" + "\033[0m")
                except:
                    print("\033[1;32;40m" + decoded + "\033[0m")
            else:
                print("\033[1;31;40m" + decoded + "\033[0m")

        except Exception as e:
            print("[client] Error receiving:", e)
            break

t = threading.Thread(target=receive) 
t.daemon = True
t.start()

client.sendto(f"SIGNUP_TAG:{name}".encode(), ("localhost", 9999))

while True:
    try:
        message = input()
        if message.strip() == "bye":
            client.sendto(f"SIGNOUT_TAG:{name}".encode(), ("localhost", 9999))
            print("Disconnecting...")
            break
        
        if message.strip().startswith("/dm"):
            parts = message.strip().split()
            if len(parts) < 3:
                print("Usage: /dm username message")
                continue
            target = parts[1]
            dm_body = " ".join(parts[2:])
            encrypted_dm = caesar_encrypt(dm_body) #criptare, doar in client, cand trimiti dm-ul
            send_message = f"{name}: /dm {target} {encrypted_dm}"
        else:
            send_message = f"{name}: {message}"

        client.sendto(send_message.encode(), ("localhost", 9999))

    except KeyboardInterrupt:
        break
    except Exception as e:
        print("[client] Error sending:", e)
        break