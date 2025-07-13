import subprocess
import socket

def enable_tor_proxy():
    try:
        # Start TOR as a subprocess (assumes tor is installed and in PATH)
        proc = subprocess.Popen(['tor'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[TOR] TOR process started.")
        return proc
    except Exception as e:
        print(f"[TOR] Failed to start TOR: {e}")
        return None

def is_tor_running(host='127.0.0.1', port=9050):
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False 