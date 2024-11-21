import FireTeam.BaseServer

def main() -> None:
    new_serv = FireTeam.BaseServer.Server()
    type = input("Server or client?: [s/c]")
    if type == 's':
        new_serv.recv_msg()

if __name__ == "__main__":
    main()