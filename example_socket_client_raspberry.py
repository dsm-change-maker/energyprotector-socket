from ep_sock.socket_client_raspberry import ClientSendSignalRaspberry
from ep_sock.socket_client_raspberry import RunClientRaspberryThread

SERVER_URL = '13.125.119.4'
SERVER_PORT = 57211


def main():
    import ep_sock.constant as constant
    test_num = int(input('Input Num : '))
    send_signal = ClientSendSignalRaspberry('rasp_id_' + str(test_num), 'rasp_group_' + str(test_num))
    run_client_raspberry_thread = RunClientRaspberryThread(send_signal, debug=True, host=constant.SERVER_URL, port=constant.SERVER_PORT)
    run_client_raspberry_thread.start()

    while True:
        print('') if False else None


if __name__ == "__main__":
    main()
