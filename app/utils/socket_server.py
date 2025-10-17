import socket
import threading

class SocketServer:
    def __init__(self, host='127.0.0.1', port=5002):
        self.host = host
        self.port = port
        self.clients = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Portu tekrar kullanım izni
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def handle_client(self, client):
        while True:
            try:
                msg = client.recv(1024)
                if not msg:
                    break
                self.broadcast(msg, sender=client)
            except:
                break
        self.clients.remove(client)
        client.close()

    def broadcast(self, message, sender=None):
        for c in self.clients:
            if c != sender:
                try:
                    c.send(message)
                except:
                    pass

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Socket server {self.host}:{self.port} çalışıyor...")

        while True:
            client, addr = self.server.accept()
            print(f"{addr} bağlandı.")
            self.clients.append(client)
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()


socket_server_instance = SocketServer()
