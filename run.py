import threading
from honeypot.services.ssh import run_ssh_honeypot
from honeypot.services.ftp import run_ftp_honeypot
from honeypot.services.http import run_http_honeypot
from web.dashboard import run_dashboard
import honeypot.config as config


def main():
    threads = []
    if 'SSH' in config.ENABLED_SERVICES:
        threads.append(threading.Thread(target=run_ssh_honeypot, args=(config.SERVICE_PORTS['SSH'],), daemon=True))
    if 'FTP' in config.ENABLED_SERVICES:
        threads.append(threading.Thread(target=run_ftp_honeypot, args=(config.SERVICE_PORTS['FTP'],), daemon=True))
    if 'HTTP' in config.ENABLED_SERVICES:
        threads.append(threading.Thread(target=run_http_honeypot, args=(config.SERVICE_PORTS['HTTP'],), daemon=True))
    threads.append(threading.Thread(target=run_dashboard, daemon=True))

    for t in threads:
        t.start()

    # Keep the main thread alive
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down honeypot...")

if __name__ == "__main__":
    main() 