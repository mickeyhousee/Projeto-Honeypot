import socket
import threading
import datetime
from honeypot.logger import log_event
from honeypot.alert import send_email_alert

def handle_client(client_socket, addr):
    timestamp = datetime.datetime.now()
    try:
        data = client_socket.recv(1024)
        log_event("SSH", addr[0], timestamp, data)
        send_email_alert(
            subject=f"SSH Honeypot Connection from {addr[0]}",
            message=f"Connection at {timestamp}\nData: {data}"
        )
    except Exception as e:
        log_event("SSH", addr[0], timestamp, f"Error: {e}")
    finally:
        client_socket.close()

def run_ssh_honeypot(port=2222):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    print(f"[SSH] Honeypot listening on port {port}")
    while True:
        client, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
        client_thread.start() 