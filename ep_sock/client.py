import asyncio
from ep_sock import constant, payload

clients = []


class Client:
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter
    client_type: str
    raspberry_id: str
    raspberry_group: str

    send_data: payload.Payload
    recv_data: payload.Payload

    def __init__(self, reader: asyncio.StreamReader = None, writer: asyncio.StreamWriter = None, client_type='',
                 raspberry_id='', raspberry_group='', host=constant.SERVER_URL, port=constant.SERVER_PORT):
        self.reader = reader
        self.writer = writer
        self.host = host
        self.port = port

        self.client_type = client_type
        self.raspberry_id = raspberry_id
        self.raspberry_group = raspberry_group

        self.send_data = payload.Payload(client_type=self.client_type)
        self.recv_data = payload.Payload()

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    def print(self, newline=False):
        if newline:
            print('')
        print('--Client--')
        if len(self.client_type) is not 0:
            print('client_type : ' + self.client_type)
        if len(self.raspberry_id) is not 0:
            print('raspberry_id : ' + self.raspberry_id)
        if len(self.raspberry_group) is not 0:
            print('raspberry_group : ' + self.raspberry_group)

    async def write(self, to_sock: bool = True, to_raspberry: bool = False, to_device: bool = False):
        self.send_data.client_type = self.client_type
        self.send_data.raspberry_id = self.raspberry_id
        self.send_data.raspberry_group = self.raspberry_group
        await self.send_data.write(self.writer, to_sock=to_sock, to_raspberry=to_raspberry, to_device=to_device)
        await self.read()
        is_ok = self.recv_data.status and self.recv_data.client_type == constant.CLIENT_TYPE_REQ_OK
        self.recv_data.__init__()
        return is_ok

    async def close(self):
        self.send_data.client_type = constant.CLIENT_TYPE_CLOSE
        await self.send_data.write(self.writer)
        await self.read()
        if self.recv_data.status:
            self.writer.close()
            await self.writer.wait_closed()
            return True
        return False

    async def read(self):
        await self.recv_data.read(self.reader)


class ClientSendSignal:
    def __init__(self):
        self.close: bool = False
        self.send: bool = False
        self.req_ok: bool = False

        self.raspberry_id: str = ''
        self.raspberry_group: str = ''
        self.device_id: str = ''
        self.device_type: str = ''
        self.unit_index: int = 0
        self.on_off: bool = False

    def print(self, newline=False):
        if newline:
            print('')
        print('--ClientSendSignal--')
        print('close :', self.close)
        print('send :', self.send)
        print('req_ok :', self.req_ok)
        if len(self.raspberry_id):
            print('raspberry_id : ' + self.raspberry_id)
        if len(self.raspberry_group):
            print('raspberry_group : ' + self.raspberry_group)
        if len(self.device_id):
            print('device_id : ' + self.device_id)
        if len(self.device_type):
            print('device_type : ' + self.device_type)
        print('unit_index :', self.unit_index)
        print('on_off :', self.on_off)


def get_client(client_type=constant.CLIENT_TYPE_NONE, client_id='', client_group='') -> Client:
    if client_type == constant.CLIENT_TYPE_API:
        api_clients = list(filter(lambda c: c.client_type == constant.CLIENT_TYPE_API, clients))
        if len(api_clients) is 0:
            return Client()
        return api_clients[0]
    elif client_type == constant.CLIENT_TYPE_RASPBERRY:
        raspberry_clients = list(filter(lambda c:
                                        c.client_type == constant.CLIENT_TYPE_RASPBERRY and
                                        c.raspberry_id == client_id and
                                        c.raspberry_group == client_group, clients))
        if len(raspberry_clients) is 0:
            return Client()
        return raspberry_clients[0]
    return Client()


async def register_new_client(client_someone: Client):
    if await client_someone.write(to_sock=True):
        await client_someone.read()
        if client_someone.recv_data.status and client_someone.recv_data.client_type == constant.CLIENT_TYPE_REQ_OK:
            return True
    return False
