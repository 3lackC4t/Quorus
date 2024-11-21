import threading
import socket
import sys
import os
import json
from datetime import datetime

class Node:
    def __init__(self):
        self.default_port = 50515
        self.address = socket.gethostbyname(socket.gethostname())
        self.default_buffer = 4096

        self.id = ""
        self.current_term = 0
        self.voted_for = None
        self.current_role = "FOLLOWER"
        self.current_leader = None
        self.votes_recieved = []

        self.log = []
        self.commit_length = []
        self.sent_length = []

        self.nodes_expected = {}
        self.nodes = {}

    def listen(self) -> None:
        receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver.bind((self.address, self.default_port))

        print(f"Node:{self.id}::listening on Port:{self.default_port}::Status:{self.current_role}")
        while True:
            try:
                data, sender = receiver.recvfrom(self.default_buffer)

            except socket.timeout:
                pass
            except OSError:
                pass
            finally:
                pass

    def send_msg(self, log) -> None:
        

    def election_timeout(self):
        self.current_term += 1
        if self.current_role == "LEADER":
            return
               