import threading
import socket
import sys
import os
import math
import json
from time import sleep
from datetime import datetime

class Node:
    def __init__(self):
        self.default_port = 50515
        self.address = "127.0.0.1" 
        self.default_buffer = 4096

        self.id = f"{self.address}:{self.default_port}"
        self.current_term = 0
        self.voted_for = None
        self.current_role = "FOLLOWER"
        self.current_leader = None
        self.votes_recieved = []

        self.log = []
        self.commit_length = []
        self.sent_length = []

        self.nodes_expected = []
        self.nodes = []

        self._handler = Handler()
        self._dispatcher = Dispatcher()

    def listen(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("0.0.0.0", self.default_port))
            print(f"Node:{self.id}::listening on Port:{self.default_port}::Status:{self.current_role}")

            while True:
                try:
                    data, sender = receiver.recvfrom(self.default_buffer)
                    print(f"RCVD::Sender:{sender}::data:{data}")
                    self._handler.de_serialize(data, sender)
                    print(self._handler.data)
                except socket.timeout:
                    print("timieout occured while listening")
                except OSError:
                    print("something attempted to connect but failed")

    def send_msg(self, address, port, data) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(self._dispatcher.format(data), (address, port))

    def set_role(self, role):
        self.current_role = role

    def set_cur_leader(self, leader):
        self.current_leader = leader

    def election_timeout(self):
        self.current_term += 1
        if self.current_role == "LEADER":
            return
        
        self.current_role = "CANDIDATE"
        self.voted_for = self.id
        self.votes_recieved = [self.id]

        last_term = 0

        if len(self.log) > 0:
            last_term = self.log[len(self.log - 1)]["TERM"]
        
        msg = self._dispatcher.format({
            "ID": self.id,
            "ADDRESS": self.address,
            "PORT": self.default_port,
            "MSG_TYPE": "ELECTION_TIMEOUT",
            "NODE_ID": self.id, 
            "CURRENT_TERM" : self.current_term,
            "LOG_LENGTH" : len(self.log),
            "LAST_TERM" : last_term
        })

        for client in self.nodes:
            self.send_msg(client["ADDRESS"], client["PORT"], msg)

    def vote_request(self, id, curr_term, log_len, log_term):
        if self.current_term <= curr_term:
            self.current_term = curr_term
            self.current_role = "FOLLOWER"
            self.voted_for = None

        last_term = 0
        if len(self.log) > 0:
            last_term = self.log[len(self.log) -1]["TERM"]

        logOk = (last_term <= log_term) or (log_term == last_term and len(self.log) < log_len )

        if self.current_term >= curr_term and logOk and self.voted_for is None:
            self.voted_for = id

            msg = self._dispatcher({
                "ID": self.id,
                "ADDRESS": self.address,
                "PORT": self.default_port,               
                "MSG_TYPE" : "VOTE_RESPONSE",
                "CURRENT_TERM": self.current_term,
                "RESPONSE": True,
            })

            return msg
        else:
            msg = self._dispatcher({
                "ID": self.id,
                "ADDRESS": self.address,
                "PORT": self.default_port,              
                "MSG_TYPE" : "VOTE_RESPONSE",
                "CURRENT_TERM": self.current_term,
                "RESPONSE": False, 
            })

            return msg       

    def vote_response(self, voterId, term, granted):
        if self.current_role == "CANDIDATE" and term == self.current_term and granted:
            self.votes_recieved.append(voterId)
        
        if len(self.votes_recieved) >= math.ceil((len(self.nodes) + 1) / 2):
            self.current_role = "LEADER"
            self.current_leader = self.id
            for client in self.clients:
                pass

    def election_timer_reset(self):
        pass

    def send_heartbeat(self):
        while self.current_role == "LEADER":
            msg = self._dispatcher({
                "ID": self.id,
                "ADDRESS": self.address,
                "PORT": self.default_port,              
                "MSG_TYPE" : "VOTE_RESPONSE",
                "CURRENT_TERM": self.current_term,
            })

            for client in self.nodes:
                self.send_msg(client["ADDRESS"], client["PORT"], msg)
            
            sleep(1)
        sleep(1)

# The Handler is responsible for formatting incoming messages
# Raw stream data is sent to the handler, decoded and then returned
class Handler:
    def __init__(self):
        self.data = [{}, ""]

    def de_serialize(self, data, sender):
        self.data[0] = json.loads(data)
        self.data[1] = sender
 

# The Dispatcher is responsible for formatting outgoing messages
# Any time a Node's send_msg method is called it will spawn call the dispatcher to 
# format the message
class Dispatcher:
    def __init__(self):
        pass

    def format(self, msg):
        return json.dumps(msg).encode("utf-8")