import os
import sys
import socket
import threading
import pyaml
import json
from datetime import datetime
from time import sleep

"""
Quorus is an attempt at a lightweight and containerizable
quorum algorithm for use in high availability servers.
"""

GLOBALS = {
    "STATUS": "",
    "ROLE": "",
    "PORT": 50515,
    "ADDRESS": socket.gethostbyname(socket.gethostname),
    "DEFAULT_TIMEOUT": 5,
    "LOG_PATH": "",
    "HELLO_INTERVAL": 0.5,
}

def logger() -> None:
    pass

def send_hello() -> None:
    hello_msg = {
            "status": GLOBALS["STATUS"],
            "role": GLOBALS["ROLE"],
            "sender": GLOBALS["ADDRESS"]
        } 

    while True:
        hello_msg["time_stamp"] = str(datetime.now())
        serialized_msg = json.dump(hello_msg)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_sock.sendto(serialized_msg ,"<broadcast>", GLOBALS["PORT"])
        sleep(GLOBALS["HELLO_INTERVAL"])

def listen_for_hello() -> None:
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serv_sock.bind((GLOBALS["ADDRESS"], GLOBALS["PORT"]))
    serv_sock.listen()

    clients = []

    try:
        
    except:
        pass

def main() -> None:
    pass

if __name__ == "__main__":
    main()