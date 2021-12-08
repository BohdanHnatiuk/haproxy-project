import socket
from flask import Flask, Response, request

app = Flask(__name__)

@app.route('/')
def home_page():
    server_name = request.host.split(':')[0]
    server_ip = request.host_url.split(':', 1)
    user_agent = request.user_agent.string
    return f'Container ID: {socket.getfqdn()},<br>Server IP: {server_ip },<br>User Agent: {user_agent},<br>Len: {len(user_agent)}'

@app.route('/healthz')
def health_ok():
    status_code = Response(status=200)
    return status_code
    