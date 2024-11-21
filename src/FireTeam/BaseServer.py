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

        self._handler = Handler()
        self._dispatcher = Dispatcher()

    def listen(self) -> None:
        with open(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as receiver:
            receiver.bind((self.address, self.default_port))
            print(f"Node:{self.id}::listening on Port:{self.default_port}::Status:{self.current_role}")

            while True:
                try:
                    data, sender = receiver.recvfrom(self.default_buffer)
                    print(f"RCVD::Sender:{sender}::data:{data}")
                    self._handler.de_serialize(data, sender)

                except socket.timeout:
                    pass
                except OSError:
                    pass
                finally:
                    pass

    def send_msg(self, address, port, data) -> None:
        with open(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sender:
            sender.sendto(data, (address, port))

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
            last_term = self.log[len(self.log -1)]["TERM"]

        logOk = (last_term <= log_term) or (log_term == last_term and len(self.log) < log_len )

        if self.current_term >= curr_term and logOk and self.voted_for is not None:
            self.voted_for = id

            msg = self._dispatcher({
                "MSG_TYPE" : "VOTE_RESPONSE",
                "ID": self.id,
                "CURRENT_TERM": self.current_term,
                "RESPONSE": True
            })

            self.send_msg()         

               

# The Handler is responsible for formatting incoming messages
# Raw stream data is sent to the handler, decoded and then returned
class Handler:
    def __init__(self):
        self.data = {{}, ""}

    def de_serialize(self, data, sender):
        self.data[0] = json.loads(data)
        self.data[1] = sender
 

# The Dispatcher is responsible for formatting outgoing messages
# Any time a Node's send_msg method is called it will spawn call the dispatcher to 
# format the message
class Dispatcher:
    def __init__(self):
        pass

    def format(self, params):
        pass