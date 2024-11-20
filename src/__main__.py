import os
import sys
import socket
import threading
import pyaml
from time import sleep


"""
Quorus is an attempt at a lightweight and containerizable
quorum algorithm for use in high availability servers.
"""

GLOBALS = {
    "PORT": 50515,
    "ADDRESS": socket.gethostbyname(socket.gethostname)
}


# Wait for startup

# Initialize some settings

# Listen for a "Hello" message from something on the config file

# if no message then it promotes itself to a role on the config file 

# If message then it assigns itself a role according to the rules of the config file

def initialize() -> None:
    while True:
       s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       s.bind((GLOBALS["ADDRESS"], GLOBALS["PORT"]))
       s.listen()

def main() -> None:
    pass

if __name__ == "__main__":
    main()