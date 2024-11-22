import threading
import socket
import sys
import os
import math
import json
from time import sleep
from datetime import datetime

"""
node format for reference

node = {
    'ADDRESS': '<an IP address or host name>',
    'PORT': '<The port the node is listening on>'
    'ID': '<then nodes id>',    
}

log format for reference

log = {

}
"""

class Node:
    def __init__(self):
        self.default_port = 50515
        self.address = "127.0.0.1" 
        self.default_buffer = 4096
        self.default_timeout = 10

        self.id = f"{self.address}:{self.default_port}"
        self.current_term = 0
        self.voted_for = None
        self.current_role = "FOLLOWER"
        self.current_leader = None
        self.votes_recieved = []
        self.self_elect_after_isolation = True
        self.isolation_election_threshhold = 3
        self.election_attempts = 0

        self.log = []
        self.commit_length = []
        self.sent_length = []
        self.log_buffer = []

        self.nodes_expected = []
        self.nodes = []

        self._handler = Handler()
        self._dispatcher = Dispatcher()

    def listen(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
            receiver.bind(("0.0.0.0", self.default_port))
            receiver.settimeout(self.default_timeout)
            print(f"Node:{self.id}::listening on Port:{self.default_port}::Status:{self.current_role}")
            
            while True:
                match self.current_role:
                    case 'LEADER':
                        self.leader_logic(receiver)
                    case 'FOLLOWER':
                        self.follower_logic(receiver)
                    case 'CANDIDATE':
                        self.candidate_logic(receiver)


    def follower_logic(self, receiver):
        try:
            data, sender = receiver.recvfrom(self.default_buffer)
            data = self._handler.de_serialize(data, sender)
            msg_type = data[0]['MSG_TYPE']

            match msg_type:
                case 'APPEND_ENTRIES':
                    self.election_timer_reset()
                case 'VOTE_REQUEST':
                    self.vote_request(self.id, self.current_term, len(self.log), )
                case 'DISCOVERY':
                    self.acknowledge()
    
        except socket.timeout:
            self.election_timeout()

    def candidate_logic(self, receiver):
        try:
            data, sender = receiver.recvfrom(self.default_buffer)
            data = self._handler.de_serialize(data, sender)
            msg_type = data[0]['MSG_TYPE']

            match msg_type:
                case 'VOTE_RESPONSE':
                    self.vote_response()
                case 'VOTE_REQUEST':
                    self.vote_request(self.id, self.current_term, len(self.log), )
                case 'APPEND_ENTRIES':
                    self.current_role = 'FOLLOWER'

        except socket.timeout:
            self.election_timeout()       

    def leader_logic(self, receiver):
        try:
            data, sender = receiver.recvfrom(self.default_buffer)
            data = self._handler.de_serialize(data, sender)
            msg_type = data[0]['MSG_TYPE']
            
            match msg_type:
                case 'CLIENT REQUEST':
                    self.handle_broadcast()
                case 'APPEND_ENTRIES_RESPONSE':
                    self.process_append_entries_response(data)
            

        except:
            pass

    def acknowledge(self):

    def send_msg(self, address, port, data) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            sender.sendto(self._dispatcher.format(data), (address, port))
    
    def find_nodes(self):
        msg = {
            'ID': self.id,
            'ADDRESS': self.address,
            'PORT': self.default_port,
            'MSG_TYPE': "DISCOVERY",
        }
        for node in self.nodes_expected:
            self.send_msg(node['ADDRESS'], node['PORT'], msg)

    def election_timeout(self):
        print(f"Timeout Detected on node {self.id}. Performing Election")
        self.current_term += 1
        if self.current_role == "LEADER":
            return
        
        self.current_role = "CANDIDATE"
        self.voted_for = self.id
        self.votes_recieved = [self.id]
        self.election_attempts += 1

        last_term = 0

        if len(self.log) > 0:
            last_term = self.log[len(self.log - 1)]["TERM"]
        
        msg = self._dispatcher.format({
            "ID": self.id,
            "ADDRESS": self.address,
            "PORT": self.default_port,
            "MSG_TYPE": "VOTE_REQUEST",
            "NODE_ID": self.id, 
            "CURRENT_TERM" : self.current_term,
            "LOG_LENGTH" : len(self.log),
            "LAST_TERM" : last_term
        })

        for node in self.nodes:
            self.send_msg(node["ADDRESS"], node["PORT"], msg)

        if self.election_attempts >= self.isolation_election_threshhold:
            if self.self_elect_after_isolation:
                print(f"Node {self.id} detected isolation: electing self as leader")
                self.current_role = 'LEADER'
                self.current_leader = self.id
                self.election_attempts = 0
            else:
                print(f"Node: {self.id} detected isolation. self_election is disabled by default.")

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
            for node in self.nodes:
                self.sent_length = len(self.log)
                acked_length = 0
                self.replicate_log(self.id, node)
        elif term > self.current_term:
            self.current_term = term
            self.current_role = "FOLLOWER" 
            self.voted_for = None
            self.election_timer_reset()

    def handle_broadcast(self, payload: list):

        entry = {
            "ID": self.id,
            "ADDRESS": self.address,
            "PORT": self.default_port,
            "MSG_TYPE": "LOG_UPDATE",
            "CURRENT_TERM": self.current_term,
            "CONTENT": payload,
        }

        if self.current_role == "LEADER": 
            for node in self.nodes:
                self.replicate_log(self.id, node)

        elif self.current_leader is not None:
            self.send_msg(self.current_leader["ADDRESS"], self.current_leader["PORT"], entry)

        else:
            self.log_buffer.append(entry)

    def replicate_log(self):
        if self.current_role != "LEADER":
            return
        


    def election_timer_reset(self):
        pass

    def append_entries(self, payload = []):
        while self.current_role == "LEADER":
            msg = self._dispatcher({
                "ID": self.id,
                "ADDRESS": self.address,
                "PORT": self.default_port,              
                "MSG_TYPE" : "VOTE_RESPONSE",
                "CURRENT_TERM": self.current_term,
                "CONTENT": payload,
            })

            for node in self.nodes:
                try:
                    self.send_msg(node["ADDRESS"], node["PORT"], msg)
                except Exception as e:
                    print(f"Error sending AppendEntries to {node['ADDRESS']}::{node['PORT']}")
            
            sleep(1)
        sleep(1)

    def start_node(self):

        self.find_nodes()

        self.current_term = 0
        self.current_role = 'FOLLOWER'
        self.log = []
        self.votes_recieved = []
        self.voted_for = None

        threading.Thread(target=self.listen, daemon=False).start()

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
        msg["TIMESTAMP"] = str(datetime.now())
        return json.dumps(msg).encode("utf-8")