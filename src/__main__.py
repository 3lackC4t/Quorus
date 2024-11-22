from FireTeam.BaseServer import Node

def main() -> None:

    native_node1 = Node()
    native_node1.default_port = 50516
    native_node2 = Node()
    native_node2.default_port = 50515

    native_node1.start_node()
    native_node2.start_node()

if __name__ == "__main__":
    main()