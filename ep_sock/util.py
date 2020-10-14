from functools import reduce
from ep_sock import constant


def is_not_empty(arr):
    return len(arr) is not 0


def print_client_type(client_type):
    print('client_type : ' + client_type) if is_not_empty(client_type) else None


def print_raspberry_info(raspberry_id='', raspberry_group=''):
    print('raspberry_id : ' + raspberry_id) if is_not_empty(raspberry_id) else None
    print('raspberry_group : ' + raspberry_group) if is_not_empty(raspberry_group) else None


def print_device_info(device_id, device_type):
    print('device_id : ' + device_id) if is_not_empty(device_id) else None
    print('device_type : ' + device_type) if is_not_empty(device_type) else None


def add_semicolons(string, word_list):
    return reduce(lambda ret, e: ret + e + ';', word_list, string)


def is_client_type_allowed(client_type: str) -> bool:
    if client_type == constant.CLIENT_TYPE_DEVICE or \
            client_type == constant.CLIENT_TYPE_RASPBERRY or \
            client_type == constant.CLIENT_TYPE_API:
        return True
    print(client_type)
    return False


def is_special_client_type(client_type: str) -> bool:
    if client_type == constant.CLIENT_TYPE_CLOSE or \
            client_type == constant.CLIENT_TYPE_REQ_OK or \
            client_type == constant.CLIENT_TYPE_REGISTER or \
            client_type == constant.CLIENT_TYPE_NONE:
        return True
    return False


def is_client_type_none(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_NONE


def is_client_type_req_ok(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_REQ_OK


def is_client_type_close(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_CLOSE


def is_client_type_register(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_REGISTER


def is_client_type_api(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_API


def is_client_type_raspberry(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_RASPBERRY


def is_client_type_device(client_type: str) -> bool:
    return client_type == constant.CLIENT_TYPE_DEVICE


def client_type_to_str(client_type):
    if client_type == constant.CLIENT_TYPE_CLOSE:
        return 'CLIENT_TYPE_CLOSE'
    elif client_type == constant.CLIENT_TYPE_REQ_OK:
        return 'CLIENT_TYPE_REQ_OK'
    elif client_type == constant.CLIENT_TYPE_REGISTER:
        return 'CLIENT_TYPE_REGISTER'
    elif client_type == constant.CLIENT_TYPE_API:
        return 'CLIENT_TYPE_API'
    elif client_type == constant.CLIENT_TYPE_RASPBERRY:
        return 'CLIENT_TYPE_RASPBERRY'
    elif client_type == constant.CLIENT_TYPE_DEVICE:
        return 'CLIENT_TYPE_DEVICE'
    return 'CLIENT_TYPE_NONE'


def is_device_req_packet(packet_string):
    ret = packet_string[:-1].split('`')
    return ret[len(ret) - 1] == 'REQ'
