#  * HAPROXY PROJECT * Landingi *

   * [Overview](#overview)
   * [Tech Stack](#tech-stack)
   * [Prerequisites](#prerequisites)
   * [Code](#code) 
   * [Usage](#usage)
   * [Cleanup](#cleanup)

## Overview
<b>This repository contains:</b><br>
  1. simple HAPROXY configuration that provides:<br>
    a. blocking traffic with user-agent length equal to or less than 16 characters;<br>
    b. blocking traffic for user-agent which is on the list of forbidden user agents (loaded from a file); <br>
    c. allowing traffic for user-agent which is on the list of allowed user agents (override for rule 1);<br>
    d. backend consists of two servers `backend1` and `backend2`, where `backend2` is the backup server.<br>
  2. backendN is a Python application that supports:<br>
    a. http "/healthz" endpoint returning" HTTP 200 OK "for haproxy healthchecks;<br>
    b. the http "/" endpoint returning any content that allows distinguishing the container from which it is served.<br>

When querying localhost: 9090 on the local machine, the output will be from backend1.
In the case of the backend1 stops, the haproxy should serve the content from backend2.
After picking up the backend1 again, traffic should be served from backend1 again. 

## Tech Stack
* Docker-compose
* HAPROXY

## Prerequisites
Before launching the solution please install docker and docker-compose.

## Code
### haproxy.cfg

```shell
frontend public_frontend
   mode http
   log global
   timeout client 5s
   bind *:80
   # blocking traffic for User-Agent which is in the forbidden "blacklist_agent.lst"
   acl is_blacklisted  req.fhdr(User-Agent) -f /usr/local/etc/haproxy/blacklist_agent.lst 
   http-request deny deny_status 403 if is_blacklisted
   # blocking traffic for User-Agent if length of User-Agent equal to or less than 16 characters 
   # and User-Agent is not in the "whitelist_agent.lst"
   http-request deny if { req.hdr(User-Agent) -m len le 16 } !{ req.fhdr(User-Agent) -f /usr/local/etc/haproxy/whitelist_agent.lst }
   default_backend public_web_servers

backend public_web_servers
   option httpchk
   http-check connect
   http-check send meth GET uri /healthz
   # Health checks return a "200 OK" response, and are classified as successful.
   http-check expect status 200
   mode http
   server s1 172.20.1.2:5000 check weight 100%
   server s2 172.20.1.3:5000 check
```
### app.py

```shell
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
```

## Usage
Clone this repository and change the directory to the appropriate one:
```shell
   cd haproxy-project
```
Run:
```shell
	docker-composer up -d
```
Use the following command for validating:
```shell
   curl -A "user-agent-name-here" http://localhost:9090
```

Use the following command to check health status:
```shell
   curl -A "user-agent-name-here" -I http://localhost:9090/healthz
```
The response will be:
```shell
   HTTP/1.0 200 OK
   content-type: text/html; charset=utf-8
   content-length: 0
   server: Werkzeug/2.0.2 Python/3.9.9
   date: Wed, 08 Dec 2021 19:26:27 GMT
   connection: keep-alive
```

## Cleanup
Run the following command if you want to delete all the containers and network created before:
```shell
   docker-composer down
```
Also, you may delete downloaded images.
