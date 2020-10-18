from ep_sock.socket_server import SocketServer
from ep_sock import constant


def main():
    server = SocketServer('127.0.0.1', constant.SERVER_PORT, debug=True)
    server.run()


if __name__ == "__main__":
    main()
