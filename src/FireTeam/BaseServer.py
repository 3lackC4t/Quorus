import threading
import json
import socket
from datetime import datetime

class Server:
    
    def __init__(self):
        self._name = ""
        self._status = "CANDIDATE"
        self._address = socket.gethostbyname(socket.gethostname())
        self._default_port = 50515
        self._default_timeout = 15
        self._exp_clients = [] # The servers that this server believes it should be connected to.
        self._clients = [] # List of dictionaries containing information about the clients connected to this server.

    def cluster_init(self, message) -> None:
        # We do this to initialize our cluster. If the server wakes up and it's client list is empty it will search through the expected clients.

        announcer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        encoded_msg = self._Handler("Discover")

        for client in self._clients:            
            self._Dispatcher(encoded_msg, client) # For now we just goint ouse a raw address

    def send_msg(self, message) -> None:
        # Sends messages that are built by the dispatcher
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        sender.sendto(message, ())

    def recv_msg(self) -> None:
        # just sits here and accepts messages and then forwards them to the handler 
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind((self._address, self._default_port))
        receiver.settimeout(self._default_timeout)

        while True:
            try:
                data, addr = receiver.recvfrom(1024)
                self._Dispatcher(data)
                print(f"Received Message from {addr}")
            except socket.timeout:
                print(f"No messages received")

    def _Handler(self, msg_type: str):
        base_msg = {
            "NAME": self._name,
            "STATUS": self._status,
            "ADDRESS": self._address,
            "TIME_STAMP": str(datetime.now()),
        }

        if msg_type == "DISCOVER":
            base_msg["MESSAGE"] = "DISCOVER"
        elif msg_type == "ANNOUNCE":
            base_msg["MESSAGE"] = ""

        return json.loads(base_msg)

    def _Dispatcher(self, data, address):
        data = json.loads(data)
        message = data["MESSAGE"]

        if message == "DISCOVER":
            self.send_msg("ANNOUNCE", address)
        elif message == "ANNOUNCE"