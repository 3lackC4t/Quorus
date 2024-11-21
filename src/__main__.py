from FireTeam.BaseServer import Server


def main() -> None:
    server1 = Server()
    server1._name = "Server1"
    server1._default_port = 50515

    server2 = Server()
    server2._name = "Server2"
    server2._default_port = 50516

    server1.start()
    server2.start()

if __name__ == "__main__":
    main()