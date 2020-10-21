from ep_sock.client import ClientSendSignal
from ep_sock.socket_client_api import RunClientApiThread
from ep_sock import constant

# SERVER_URL = '52.78.77.85'
# SERVER_PORT = 55642
SERVER_URL = '13.209.17.106'
SERVER_PORT = 59721

def main():
    send_signal = ClientSendSignal()
    run_client_api_thread = RunClientApiThread(send_signal, host=SERVER_URL, port=SERVER_PORT,
                                               debug=True)
    run_client_api_thread.start()
    while True:
        test_num = int(input('Input Num : '))
        if test_num == -1:
            run_client_api_thread.stop()
            # stop() 메서드가 아래와 같은 역할을 수행함
            # send_signal.close = True
            # while True:
            #     if not send_signal.close:
            #         break
            break
        unit_index = int(input('Input Unit_index : '))
        on_off = int(input('Input State : ')) == 1
        send_signal.raspberry_id = 'rasp_id_' + str(test_num)
        send_signal.raspberry_group = 'rasp_group_' + str(test_num)
        send_signal.device_id = 'device_id_' + str(test_num)
        send_signal.device_type = 'plug'
        send_signal.unit_index = unit_index
        send_signal.on_off = on_off
        send_signal.send = True
        while True:
            if not send_signal.send:
                break
        print('REQ OK : ', send_signal.req_ok)


if __name__ == "__main__":
    main()
