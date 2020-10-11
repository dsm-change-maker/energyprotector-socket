from ep_sock.socket_client_raspberry import ClientSendSignalRaspberry
from ep_sock.socket_client_raspberry import RunClientRaspberryThread
from ep_sock import constant

# SERVER_URL = '52.78.77.85'
# SERVER_PORT = 55642
SERVER_URL = constant.SERVER_URL
SERVER_PORT = constant.SERVER_PORT


def main():
    test_num = int(input('Input Num : '))
    signal = ClientSendSignalRaspberry('rasp_id_' + str(test_num), 'rasp_group_' + str(test_num))
    run_client_raspberry_thread = RunClientRaspberryThread(signal, debug=True, host=SERVER_URL, port=SERVER_PORT)
    run_client_raspberry_thread.start()

    while True:
        if signal.device_read:
            print(f'DEVICE{signal.recv_data.device_id, signal.recv_data.device_type} READ : ', signal.recv_data.unit_index, signal.recv_data.on_off)
            signal.device_read = False
        elif signal.device_req_ok:
            print(f'DEVICE{signal.recv_data.device_id, signal.recv_data.device_type} REQ : ',
                  signal.recv_data.unit_index, signal.recv_data.on_off)
            signal.device_req_ok = False

if __name__ == "__main__":
    main()
