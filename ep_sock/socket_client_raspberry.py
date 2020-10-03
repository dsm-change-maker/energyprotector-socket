import asyncio
from ep_sock import client, constant, payload
import threading


class ClientRaspberry(client.Client):
    def __init__(self, raspberry_id, raspberry_group, host, port):
        super().__init__(raspberry_id=raspberry_id, raspberry_group=raspberry_group,
                         client_type=constant.CLIENT_TYPE_RASPBERRY, host=host, port=port)

    async def write_ok(self):
        await super().write()

    async def write_no(self):
        await self.send_data.err_write(self.writer)


class ClientSendSignalRaspberry(client.ClientSendSignal):
    def __init__(self, raspberry_id='', raspberry_group=''):
        super().__init__()
        self.raspberry_id = raspberry_id
        self.raspberry_group = raspberry_group
        self.recv_data: payload.Payload = payload.Payload()

        self.device_close: bool = False
        self.device_send: bool = False
        self.device_read: bool = False
        self.device_req_ok: bool = False


async def run_client_raspberry(signal: ClientSendSignalRaspberry, host=constant.SERVER_URL, port=constant.SERVER_PORT, debug=False):
    if debug:
        print('[C] RUN CLIENT_RASPBERRY')
    client_raspberry = ClientRaspberry(signal.raspberry_id, signal.raspberry_group, host, port)
    await client_raspberry.connect()

    is_registered = await client.register_new_client(client_raspberry)
    print(f'[C] received : {len(client_raspberry.recv_data.data)} bytes') if debug else None
    print('[C] registered as a new client') if is_registered and debug else None

    while True:
        if signal.close:
            break
        await signal.recv_data.read(client_raspberry.reader)
        print('[C] received : ', signal.recv_data.data) if debug else None
        signal.device_send = True
        # while True:
        #     if not signal.device_send:
        #         break
        if signal.device_read:
            if signal.device_req_ok:
                await client_raspberry.write_ok()
                continue
            print('[C] error : device_req_ok') if debug else None
            await client_raspberry.write_no()
            continue
        print('[C] error : device_read') if debug else None
        await client_raspberry.write_no()
        continue

    signal.req_ok = await client_raspberry.close()
    signal.close = False
    print('[C]', 'CLOSED' if signal.req_ok else 'FAILED TO CLOSE') if debug else None


class RunClientRaspberryThread(threading.Thread):
    def __init__(self, signal: ClientSendSignalRaspberry, host=constant.SERVER_URL, port=constant.SERVER_PORT, debug=False):
        threading.Thread.__init__(self)
        self.signal = signal
        self.debug = debug
        self.daemon = True
        self.host = host
        self.port = port

    async def main(self):
        await asyncio.wait([run_client_raspberry(self.signal, self.host, self.port, self.debug)])

    def run(self):
        asyncio.run(self.main())
