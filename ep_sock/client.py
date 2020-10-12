import asyncio
from ep_sock import constant, payload, util

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
                 raspberry_id='', raspberry_group='', device_id='', device_type='', host=constant.SERVER_URL,
                 port=constant.SERVER_PORT, recv_client_type=constant.CLIENT_TYPE_NONE):
        self.reader = reader
        self.writer = writer
        self.host = host
        self.port = port

        self.client_type = client_type
        self.recv_client_type = recv_client_type
        self.raspberry_id = raspberry_id
        self.raspberry_group = raspberry_group
        self.device_id = device_id
        self.device_type = device_type

        self.send_data = payload.Payload(client_type=self.client_type)
        self.recv_data = payload.Payload()

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)

    def print(self, newline=False):
        print('') if newline else None
        print('--Client--')
        util.print_client_type(self.client_type)
        util.print_raspberry_info(self.raspberry_id, self.raspberry_group)
        util.print_device_info(self.device_id, self.device_type)

    async def write(self, to_sock: bool = True, to_raspberry: bool = False, to_device: bool = False):
        self.send_data.client_type = self.client_type
        self.send_data.raspberry_id = self.raspberry_id
        self.send_data.raspberry_group = self.raspberry_group
        await self.send_data.write(self.writer, to_sock=to_sock, to_raspberry=to_raspberry, to_device=to_device,
                                   recv_client_type=self.recv_client_type)
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
        util.print_raspberry_info(self.raspberry_id, self.raspberry_group)
        util.print_device_info(self.device_id, self.device_type)
        print('unit_index :', self.unit_index)
        print('on_off :', self.on_off)


def _get_client(client_type=constant.CLIENT_TYPE_NONE, client_id='', client_group=''):
    if client_type == constant.CLIENT_TYPE_API:
        api_clients = list(filter(lambda c: c.client_type == constant.CLIENT_TYPE_API, clients))
        if len(api_clients) is 0:
            return None
        return api_clients[0]
    elif client_type == constant.CLIENT_TYPE_RASPBERRY:
        raspberry_clients = list(filter(lambda c:
                                        c.client_type == constant.CLIENT_TYPE_RASPBERRY and
                                        c.raspberry_id == client_id and
                                        c.raspberry_group == client_group, clients))
        if len(raspberry_clients) is 0:
            return None
        return raspberry_clients[0]
    elif client_type == constant.CLIENT_TYPE_DEVICE:
        devices_clients = list(filter(lambda c:
                                      c.client_type == constant.CLIENT_TYPE_DEVICE and
                                      c.device_id == client_id and
                                      c.device_type == client_group, clients))
        if len(devices_clients) is 0:
            return None
        return devices_clients[0]
    return None


def get_client(client_type=constant.CLIENT_TYPE_NONE, client_id='', client_group=''):
    ret = [False, None, f'[S] error : get_client{util.client_type_to_str(client_type), client_id, client_group}']
    target = _get_client(client_type, client_id, client_group)
    if target is not None:
        ret[0] = True
        ret[1] = target
        ret[2] = f'[S] Successfully fetched client information - {client_id, client_group}'
        if util.is_client_type_api(client_type):
            ret[2] = f'[S] Successfully fetched client information - {util.client_type_to_str(client_type)}'
    return ret


async def register_new_client(client_someone: Client):
    client_someone.recv_client_type = constant.CLIENT_TYPE_REGISTER
    if await client_someone.write(to_sock=True):
        await client_someone.read()
        if client_someone.recv_data.status and client_someone.recv_data.client_type == constant.CLIENT_TYPE_REQ_OK:
            return True
    return False


async def register_new_client_with_log(client_someone: Client, debug=False):
    print(f'[C] Request client registration to remote server') if debug else None
    is_registered = await register_new_client(client_someone)
    print(f'[C] received : {len(client_someone.recv_data.data)} bytes') if debug else None
    print('[C] registered as a new client') if is_registered and debug else None
    print('[C] Already registered') if not is_registered and debug else None
    return is_registered
