from ep_sock import constant
import socket

SERVER_URL = constant.SERVER_URL
SERVER_PORT = constant.SERVER_PORT

unit_data = [False, True, True]
device_id = 'device_id_1'
device_type = 'switch'


def press_button_interrupt(client_socket):
    print('INTERRUPT')
    unit_index = int(input('Input unit_index : '))
    on_off = int(input('Input on_off : '))
    # OK;4;CTL;;unit_index;on_off;device_id;device_type;\n
    req_for_raspberry = 'OK;6;CTL;;' + str(unit_index) + ';' + str(on_off) + str(device_id) + ';' + str(
        device_type) + ';\n'
    write_func(client_socket, req_for_raspberry.encode())
    print('[C] REQ OK (INTERRUPT)')


def read_line(client_socket):
    buffer = client_socket.recv(4096)

    buffering = True
    while buffering:
        if b'\n' in buffer:
            (line, buffer) = buffer.split(b'\n', 1)
            return line + b'\n'
        else:
            more = client_socket.recv(4096)
            if not more:
                buffering = False
            else:
                buffer += more
    if buffer:
        return buffer


def write_func(client_socket, encoded_data):
    client_socket.sendall(encoded_data)
    data = read_line(client_socket).decode()
    data_list = data.split(';')
    if data_list[0] == 'OK' and data_list[2] == '0':
        return True
    return False


def main(host=constant.SERVER_URL, port=constant.SERVER_PORT, debug=False):
    global device_id, device_type, unit_data

    print('[C] RUN CLIENT_DEVICE') if debug else None
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.setblocking(False) # Non Blocking Mode 로 설정

    register_data = 'OK;6;4;2;0;0;' + device_id + ';' + device_type + ';\n'
    if write_func(client_socket, register_data.encode()):
        data_list = read_line(client_socket).decode().split(';')
        if data_list[0] == 'OK' and data_list[2] == '0':
            print('[C] registered new device') if debug else None

    while True:
        print('')
        print('unit_data : ', unit_data)
        data = read_line(client_socket)
        data_list = data.decode().split(';')
        print('[C] received : ', data) if debug else None
        print(data_list)
        try:
            unit_data[int(data_list[4])] = int(data_list[5]) == 1
            req_ok_data = 'OK;6;4;2;0;0;' + str(device_id) + ';' + str(device_type) + ';\n'
            write_func(client_socket, req_ok_data.encode())
            req_data_for_raspberry = 'OK;8;4;3;' + data_list[4] + ';' + data_list[5] + ';' + data_list[6] + ';' + \
                                     data_list[7] + ';' + data_list[8] + ';' + data_list[9] + ';\n'
            write_func(client_socket, req_data_for_raspberry.encode())
            print('[C] REQ OK') if debug else None
        except:
            print('[C] error : set unit_data') if debug else None
            req_err_data = 'NO;6;4;2;0;0;' + device_id + ';' + device_type + ';\n'
            write_func(client_socket, req_err_data.encode())


if __name__ == "__main__":
    main(SERVER_URL, SERVER_PORT, debug=True)
