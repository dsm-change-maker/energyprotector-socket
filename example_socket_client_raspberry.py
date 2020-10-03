from ep_sock.socket_client_raspberry import ClientSendSignalRaspberry
from ep_sock.socket_client_raspberry import RunClientRaspberryThread


def main():
    test_num = int(input('Input Num : '))
    send_signal = ClientSendSignalRaspberry('rasp_id_' + str(test_num), 'rasp_group_' + str(test_num))
    run_client_raspberry_thread = RunClientRaspberryThread(send_signal, debug=True)
    run_client_raspberry_thread.start()

    while True:
        print('') if False else None


if __name__ == "__main__":
    main()
