import asyncio
from ep_sock import client, constant
import threading


class ClientApi(client.Client):
    def __init__(self, host, port):
        super().__init__(client_type=constant.CLIENT_TYPE_API)
        self.host = host
        self.port = port

    async def connect(self, **kwargs):
        await super().connect(self.host, self.port)

    async def write_control(self, rasp_id, rasp_group, d_id, d_type, unit_index, on_off):
        self.send_data.client_type = constant.CLIENT_TYPE_API
        self.send_data.raspberry_id = rasp_id
        self.send_data.raspberry_group = rasp_group
        self.send_data.device_id = d_id
        self.send_data.device_type = d_type
        self.send_data.unit_index = unit_index
        self.send_data.on_off = on_off
        return await self.write()

    async def write(self, **kwargs):
        return await super().write(to_sock=True)


async def run_client_api(signal: client.ClientSendSignal, debug=False):
    if debug:
        print('[C] RUN CLIENT_API')
    client_api = ClientApi(constant.SERVER_URL, constant.SERVER_PORT)
    await client_api.connect()
    while True:
        if signal.close:
            break
        if signal.send:
            if await client_api.write_control(signal.raspberry_id, signal.raspberry_group,
                                              signal.device_id,
                                              signal.device_type, signal.unit_index, signal.on_off):
                if debug:
                    print('[C] request Success')
                await client_api.read()
                if debug:
                    print('[C] received : ', client_api.recv_data.data)
                if client_api.recv_data.status and client_api.recv_data.client_type == constant.CLIENT_TYPE_REQ_OK:
                    if debug:
                        print('[C] registered as a new client')
                    signal.send = True
                    continue
                signal.req_ok = True
                signal.send = False
            if debug:
                print('[C] Request failed')
            signal.req_ok = False
            signal.send = False
            continue

    is_closed = await client_api.close()
    signal.req_ok = True
    if not is_closed:
        signal.req_ok = False
    signal.close = False
    if debug:
        print('[C]', 'CLOSED' if is_closed else 'FAILED TO CLOSE')


class RunClientApiThread(threading.Thread):
    def __init__(self, signal: client.ClientSendSignal, debug=False):
        threading.Thread.__init__(self)
        self.signal = signal
        self.debug = debug
        self.daemon = True

    async def main(self):
        await asyncio.wait([run_client_api(self.signal, self.debug)])

    def run(self):
        asyncio.run(self.main())

