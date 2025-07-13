from flask import Flask, render_template_string, request, redirect, send_file
from honeypot.logger import export_logs
import honeypot.config as config
import os
from honeypot.tor import enable_tor_proxy, is_tor_running
import sys

tor_proc = None

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global tor_proc
    message = ''
    if request.method == 'POST':
        if 'start_tor' in request.form:
            if not is_tor_running():
                tor_proc = enable_tor_proxy()
                if tor_proc:
                    message = 'TOR started!'
                else:
                    message = 'Failed to start TOR.'
            else:
                message = 'TOR is already running.'
        elif 'restart_honeypot' in request.form:
            message = 'Honeypot is restarting...'
            # Render the message before restarting
            logs = export_logs()
            tor_status = 'Running' if is_tor_running() else 'Not Running'
            html = render_template_string('''
                <h1>HoneyPot Dashboard</h1>
                <p style="color:green;">{{ message }}</p>
                <script>setTimeout(function(){ window.location.reload(); }, 2000);</script>
            ''', message=message)
            # Flush response before restarting
            from flask import Response
            import threading
            def restart():
                import time
                time.sleep(1)
                os.execl(sys.executable, sys.executable, *sys.argv)
            threading.Thread(target=restart, daemon=True).start()
            return html
        else:
            # Handle service enable/disable and port changes
            for service in config.SERVICE_PORTS.keys():
                enabled = request.form.get(f'enable_{service}', 'off') == 'on'
                port = request.form.get(f'port_{service}', config.SERVICE_PORTS[service])
                if enabled and service not in config.ENABLED_SERVICES:
                    config.ENABLED_SERVICES.append(service)
                elif not enabled and service in config.ENABLED_SERVICES:
                    config.ENABLED_SERVICES.remove(service)
                try:
                    config.SERVICE_PORTS[service] = int(port)
                except ValueError:
                    pass
            # Save config changes
            with open(os.path.join(os.path.dirname(__file__), '../honeypot/config.py'), 'w') as f:
                f.write('SERVICE_PORTS = ' + str(config.SERVICE_PORTS) + '\n')
                f.write('ENABLED_SERVICES = ' + str(config.ENABLED_SERVICES) + '\n')
            message = 'Configuration updated! Please restart the honeypot to apply changes.'
    logs = export_logs()
    tor_status = 'Running' if is_tor_running() else 'Not Running'
    return render_template_string('''
        <h1>HoneyPot Dashboard</h1>
        <form method="post">
            <h2>Service Controls</h2>
            <table border="1">
                <tr><th>Service</th><th>Enabled</th><th>Port</th></tr>
                {% for service, port in service_ports.items() %}
                <tr>
                    <td>{{ service }}</td>
                    <td><input type="checkbox" name="enable_{{ service }}" {% if service in enabled_services %}checked{% endif %}></td>
                    <td><input type="number" name="port_{{ service }}" value="{{ port }}" min="1" max="65535"></td>
                </tr>
                {% endfor %}
            </table>
            <input type="submit" value="Update Configuration">
        </form>
        <form method="post">
            <h2>TOR Integration</h2>
            <p>Status: <b>{{ tor_status }}</b></p>
            <button name="start_tor" value="1">Start TOR</button>
        </form>
        <form method="post">
            <button name="restart_honeypot" value="1" style="background-color:orange;">Restart Honeypot</button>
        </form>
        <p style="color:green;">{{ message }}</p>
        <h2>Recent Logs</h2>
        <a href="/export_logs"><button>Download Logs</button></a>
        <table border="1">
            <tr><th>Log Entry</th></tr>
            {% for log in logs %}
            <tr><td>{{ log }}</td></tr>
            {% endfor %}
        </table>
    ''', logs=logs, service_ports=config.SERVICE_PORTS, enabled_services=config.ENABLED_SERVICES, message=message, tor_status=tor_status)

@app.route('/export_logs')
def export_logs_route():
    logs = export_logs()
    log_path = os.path.join(os.path.dirname(__file__), '../logs/exported_logs.txt')
    with open(log_path, 'w') as f:
        for log in logs:
            f.write(log + '\n')
    return send_file(log_path, as_attachment=True)

def run_dashboard():
    app.run(host='0.0.0.0', port=5000) 