from ep_sock.socket_client_raspberry import ClientSendSignalRaspberry
from ep_sock.socket_client_raspberry import RunClientRaspberryThread
from ep_sock import constant

# SERVER_URL = '52.78.77.85'
# SERVER_PORT = 55642
SERVER_URL = constant.SERVER_URL
SERVER_PORT = constant.SERVER_PORT


def main():
    test_num = int(input('Input Num : '))
    send_signal = ClientSendSignalRaspberry('rasp_id_' + str(test_num), 'rasp_group_' + str(test_num))
    run_client_raspberry_thread = RunClientRaspberryThread(send_signal, debug=True, host=SERVER_URL, port=SERVER_PORT)
    run_client_raspberry_thread.start()

    while True:
        print('') if False else None


if __name__ == "__main__":
    main()
