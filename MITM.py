import socket
import threading
from constants import PORT

def forward(source, destination):
    while True:
        try:
            data = source.recv(4096)
            if not data:
                break
            print(data)
            destination.sendall(data)
        except Exception as e:
            print(f"Connection error: {e}")
            break
    source.close()
    destination.close()

def start_proxy(proxy_host, proxy_port, server_host, server_port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((proxy_host, proxy_port))
    proxy_socket.listen(5)
    print(f"Proxy listening on {proxy_host}:{proxy_port}")
    
    while True:
        client_socket, client_addr = proxy_socket.accept()
        print(f"Client connected from {client_addr}")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((server_host, server_port))
        print(f"Connected to server at {server_host}:{server_port}")
        
        threading.Thread(target=forward, args=(client_socket, server_socket), daemon=True).start()
        threading.Thread(target=forward, args=(server_socket, client_socket), daemon=True).start()

if __name__ == "__main__":
    PROXY_HOST = "127.0.0.1"
    PROXY_PORT = 8080         
    SERVER_HOST = "127.0.0.1" 
    SERVER_PORT = PORT        
    
    start_proxy(PROXY_HOST, PROXY_PORT, SERVER_HOST, SERVER_PORT)