import asyncio
from ep_sock import constant, util
from functools import reduce


class Payload:
    def __init__(self, client_type=constant.CLIENT_TYPE_NONE, raspberry_id='', raspberry_group='', device_id='',
                 device_type='', unit_index=0, on_off=False, recv_client_type=constant.CLIENT_TYPE_NONE):
        self.status = False
        self.client_type = client_type
        self.recv_client_type = recv_client_type
        self.raspberry_id = raspberry_id
        self.raspberry_group = raspberry_group
        self.device_id = device_id
        self.device_type = device_type
        self.unit_index = unit_index
        self.on_off = on_off

        self.data: bytes = bytes(0)

    def print(self, newline=False):
        if newline:
            print('')
        print('--Payload--')
        if len(self.data) is not 0:
            print('source_data :', self.data)
        print('status :', self.status)
        util.print_client_type(self.client_type)
        util.print_client_type(self.recv_client_type + '- (recv)')
        util.print_raspberry_info(self.raspberry_id, self.raspberry_group)
        util.print_device_info(self.device_id, self.device_type)
        print('unit_index :', self.unit_index)
        print('on_off :', self.on_off)

    def encode(self, to_sock: bool = True, to_raspberry: bool = False, to_device: bool = False, recv_client_type=constant.CLIENT_TYPE_NONE):
        payload_string = ''
        if util.is_special_client_type(self.client_type):
            to_sock = False
            to_raspberry = False
            to_device = False
            payload_string = ';1;'
            if self.client_type == constant.CLIENT_TYPE_NONE:
                payload_string = constant.STATUS_NO + payload_string
            else:
                payload_string = constant.STATUS_OK + payload_string
        if to_device:
            to_sock = False
            to_raspberry = False
            payload_string = constant.STATUS_OK + ';4;'
        if to_raspberry:
            to_sock = False
            to_device = True
            payload_string = constant.STATUS_OK + ';6;'
        if to_sock:
            to_device = True
            to_raspberry = True
            payload_string = constant.STATUS_OK + ';8;'

        payload_string += self.client_type + ';'
        payload_string = util.add_semicolons(payload_string, [recv_client_type])
        payload_string = util.add_semicolons(payload_string, [str(self.unit_index), str(int(self.on_off))]) if to_device else payload_string
        payload_string = util.add_semicolons(payload_string, [self.device_id, self.device_type]) if to_raspberry else payload_string
        payload_string = util.add_semicolons(payload_string, [self.raspberry_id, self.raspberry_group]) if to_sock else payload_string
        payload_string += '\n'
        self.data = payload_string.encode()
        return self.data

    def decode(self, encoded_string):
        data_len = 0
        data = encoded_string.decode()[:-2].split(';')

        if len(data) >= 1:
            self.status = data[0] == constant.STATUS_OK

        if len(data) >= 2:
            data_len = int(data[1])

        self.client_type = data[2] if data_len >= 1 else self.client_type
        self.recv_client_type = data[3] if data_len >= 2else self.recv_client_type
        self.unit_index = int(data[4]) if data_len >= 3 else self.unit_index
        self.on_off = int(data[5]) == 1 if data_len >= 4 else self.on_off
        self.device_id = data[6] if data_len >= 5 else self.device_id
        self.device_type = data[7] if data_len >= 6 else self.device_type
        self.raspberry_id = data[8] if data_len >= 7 else self.raspberry_id
        self.raspberry_group = data[9] if data_len >= 8 else self.raspberry_group

    async def err_write(self, writer: asyncio.StreamWriter):
        self.__init__()
        await self.write(writer)

    async def req_ok_write(self, writer: asyncio.StreamWriter, recv_client_type=''):
        self.__init__(client_type=constant.CLIENT_TYPE_REQ_OK)
        await self.write(writer, recv_client_type=recv_client_type)

    async def write(self, writer: asyncio.StreamWriter, to_sock: bool = True, to_raspberry: bool = False,
                    to_device: bool = False, recv_client_type='', without_change=False):
        if without_change:
            writer.write(self.data)
        else:
            writer.write(self.encode(to_sock=to_sock, to_raspberry=to_raspberry, to_device=to_device, recv_client_type=recv_client_type))
        await writer.drain()

    async def read(self, reader: asyncio.StreamReader):
        data: bytes = await reader.readline()
        self.data = data
        self.decode(data)


if __name__ == "__main__":
    # TEST
    send_payload = Payload(constant.CLIENT_TYPE_API, 'test_rasp_id', 'test_rasp_group', 'test_device_id',
                           'test_device_type', 4, True)
    recv_payload = Payload()
    recv_payload.print(newline=True)

    recv_payload.decode(send_payload.encode())
    recv_payload.print(newline=True)
    recv_payload.__init__()

    recv_payload.decode(send_payload.encode(to_raspberry=True))
    recv_payload.print(newline=True)
    recv_payload.__init__()

    recv_payload.decode(send_payload.encode(to_device=True))
    recv_payload.print(newline=True)
    recv_payload.__init__()
