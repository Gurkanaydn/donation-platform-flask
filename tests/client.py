import socket
import threading

HOST = '127.0.0.1'  # Socket server IP
PORT = 5002         # Socket server port

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f"{HOST}:{PORT} socket server’a bağlandı. Mesaj bekleniyor...")

def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg:
                print(f"Server Mesajı: {msg}")
        except:
            print("Server bağlantısı kesildi.")
            break

threading.Thread(target=receive_messages, daemon=True).start()

# Sonsuz döngü ile programı açık tut
try:
    while True:
        pass
except KeyboardInterrupt:
    client.close()
    print("Client kapatıldı.")
