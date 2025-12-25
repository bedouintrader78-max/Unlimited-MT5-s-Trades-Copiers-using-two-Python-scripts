# utils/socket_utils.py
import socket
import time

def connect_socket(host: str, port: int) -> socket.socket:
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            print(f"Connected to {host}:{port}")
            return s
        except Exception as e:
            print(f"Socket connect failed: {e}. Retrying in 5s...")
            time.sleep(5)

def send_json(sock: socket.socket, data: dict):
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except Exception as e:
        print("Send failed:", e)
