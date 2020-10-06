import asyncio
from ep_sock import constant


class Payload:
    def __init__(self, client_type=constant.CLIENT_TYPE_NONE, raspberry_id='', raspberry_group='', device_id='',
                 device_type='', unit_index=0, on_off=False):
        self.status = False
        self.client_type = client_type
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
        if len(self.client_type) is not 0:
            print('client_type : ' + self.client_type)
        if len(self.raspberry_id) is not 0:
            print('raspberry_id : ' + self.raspberry_id)
        if len(self.raspberry_group) is not 0:
            print('raspberry_group : ' + self.raspberry_group)

        if len(self.device_id) is not 0:
            print('device_id : ' + self.device_id)
        if len(self.device_type) is not 0:
            print('device_type : ' + self.device_type)
        print('unit_index :', self.unit_index)
        print('on_off :', self.on_off)

    def encode(self, to_sock: bool = True, to_raspberry: bool = False, to_device: bool = False):
        payload_string = ''
        if self.client_type == constant.CLIENT_TYPE_CLOSE or\
           self.client_type == constant.CLIENT_TYPE_REQ_OK or\
           self.client_type == constant.CLIENT_TYPE_NONE:
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
            payload_string = constant.STATUS_OK + ';3;'
        if to_raspberry:
            to_sock = False
            to_device = True
            payload_string = constant.STATUS_OK + ';5;'
        if to_sock:
            to_device = True
            to_raspberry = True
            payload_string = constant.STATUS_OK + ';7;'

        payload_string += self.client_type + ';'

        if to_device:
            payload_string += str(self.unit_index) + ';' + \
                              str(int(self.on_off)) + ';'
        if to_raspberry:
            payload_string += self.device_id + ';' + \
                              self.device_type + ';'
        if to_sock:
            payload_string += self.raspberry_id + ';' + \
                              self.raspberry_group + ';'
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
        self.unit_index = int(data[3]) if data_len >= 2 else self.unit_index
        self.on_off = int(data[4]) == 1 if data_len >= 3 else self.on_off
        self.device_id = data[5] if data_len >= 4 else self.device_id
        self.device_type = data[6] if data_len >= 5 else self.device_type
        self.raspberry_id = data[7] if data_len >= 6 else self.raspberry_id
        self.raspberry_group = data[8] if data_len >= 7 else self.raspberry_group

    async def err_write(self, writer: asyncio.StreamWriter):
        self.__init__()
        await self.write(writer)

    async def req_ok_write(self, writer: asyncio.StreamWriter):
        self.__init__(client_type=constant.CLIENT_TYPE_REQ_OK)
        await self.write(writer)

    async def write(self, writer: asyncio.StreamWriter, to_sock: bool = True, to_raspberry: bool = False,
                    to_device: bool = False):
        writer.write(self.encode(to_sock=to_sock, to_raspberry=to_raspberry, to_device=to_device))
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
