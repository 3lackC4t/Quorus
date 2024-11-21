from FireTeam.BaseServer import Node

import threading
from time import sleep

def main() -> None:
    server1 = Node()
    server1.default_port = 50515
    server2 = Node()
    server2.default_port = 50516

    threading.Thread(target=server1.listen, daemon=False).start()
    threading.Thread(target=server2.send_msg(server1.address, server1.default_port, {
        "ID": server2.id,
        "ADDRESS": server2.address,
        "PORT": server2.default_port,
        "ROLE": server2.current_role,
        "MSG_TYPE": "TEST"
    }), daemon=False).start()
    sleep(1)
    threading.Thread(target=server2.send_msg(server1.address, server1.default_port, {
        "ID": server2.id,
        "ADDRESS": server2.address,
        "PORT": server2.default_port,
        "ROLE": server2.current_role,
        "MSG_TYPE": "TEST"
    }), daemon=False).start()
    sleep(1)
    threading.Thread(target=server2.send_msg(server1.address, server1.default_port, {
        "ID": server2.id,
        "ADDRESS": server2.address,
        "PORT": server2.default_port,
        "ROLE": server2.current_role,
        "MSG_TYPE": "TEST"
    }), daemon=False).start()
    sleep(1)
    threading.Thread(target=server2.send_msg(server1.address, server1.default_port, {
        "ID": server2.id,
        "ADDRESS": server2.address,
        "PORT": server2.default_port,
        "ROLE": server2.current_role,
        "MSG_TYPE": "TEST"
    }), daemon=False).start()


if __name__ == "__main__":
    main()