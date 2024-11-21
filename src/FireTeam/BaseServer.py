import threading
import socket
import json
from datetime.datetime import now

class Server:
    
    def __init__(self):
        self._name = ""
        self._address = socket.gethostbyname(socket.gethostname())
        self._default_port = 50515
        self._default_timeout = 15
        self._exp_clients = []
        self._clients = []

    def send_msg(self, message_dict) -> None:
        if message_dict["TYPE"] == "heartbeat":
            while True:
                message_dict["TIME_STAMP"] = str(now())
                
                ser_message = json.loads(message_dict)

                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                for client in self._clients:
                    sock.sendto(ser_message, (client, self._default_port))

        else:
            message = b"This is a test message"
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def recv_msg(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self._address, self._default_port))
        sock.settimeout(self._default_timeout)

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                self._clients.append(addr)
                data = data.decode()
                print(data)
            except:
                print("Something Catastrophic Happened")


