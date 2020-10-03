from ep_sock.client import ClientSendSignal
from ep_sock.socket_client_api import RunClientApiThread


def main():
    send_signal = ClientSendSignal()
    run_client_api_thread = RunClientApiThread(send_signal)
    run_client_api_thread.start()
    while True:
        test_num = int(input('Input Num : '))
        if test_num == -1:
            send_signal.close = True
            while True:
                if not send_signal.close:
                    break
            break
        send_signal.raspberry_id = 'rasp_id_' + str(test_num)
        send_signal.raspberry_group = 'rasp_group_' + str(test_num)
        send_signal.device_id = 'device_id_' + str(test_num)
        send_signal.device_type = 'device_type_' + str(test_num)
        send_signal.unit_index = 0
        send_signal.on_off = True
        send_signal.send = True
        while True:
            if not send_signal.send:
                break
        print('REQ OK : ', send_signal.req_ok)


if __name__ == "__main__":
    main()
