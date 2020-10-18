import asyncio
from ep_sock import client, constant
import threading


class ClientApi(client.Client):
    def __init__(self, host, port):
        super().__init__(client_type=constant.CLIENT_TYPE_API, host=host, port=port)

    async def write_control(self, rasp_id, rasp_group, d_id, d_type, unit_index, on_off):
        self.client_type = constant.CLIENT_TYPE_API
        self.recv_client_type = constant.CLIENT_TYPE_DEVICE
        self.raspberry_id = rasp_id
        self.raspberry_group = rasp_group

        self.send_data.device_id = d_id
        self.send_data.device_type = d_type
        self.send_data.unit_index = unit_index
        self.send_data.on_off = on_off
        return await self.write()

    async def write(self, **kwargs):
        return await super().write(to_sock=True)


async def run_client_api(signal: client.ClientSendSignal, host=constant.SERVER_URL, port=constant.SERVER_PORT, debug=False):
    print('[C] RUN CLIENT_API') if debug else None
    client_api = ClientApi(host, port)
    await client_api.connect()
    await client.register_new_client_with_log(client_api, debug=True)

    while True:
        if signal.close:
            break
        if signal.send:
            if await client_api.write_control(signal.raspberry_id, signal.raspberry_group,
                                              signal.device_id,
                                              signal.device_type, signal.unit_index, signal.on_off):
                print('[C] request Success') if debug else None
                await client_api.read()
                print('[C] received : ', client_api.recv_data.data) if debug else None
                signal.req_ok = client_api.recv_data.status
                signal.send = False
                continue
            print('[C] Request failed') if debug else None
            signal.req_ok = False
            signal.send = False
            continue

    signal.req_ok = await client_api.close()
    signal.close = False
    if debug:
        print('[C] CLOSED') if signal.req_ok else print('[C] FAILED TO CLOSE')


class RunClientApiThread(threading.Thread):
    def __init__(self, signal: client.ClientSendSignal, host=constant.SERVER_URL, port=constant.SERVER_PORT, debug=False):
        threading.Thread.__init__(self)
        self.signal = signal
        self.debug = debug
        self.daemon = True
        self.host = host
        self.port = port

    async def main(self):
        await asyncio.wait([run_client_api(self.signal, self.host, self.port, self.debug)])

    def run(self):
        asyncio.run(self.main())

    def stop(self):
        self.signal.close = True
        while True:
            if not self.signal.close:
                break
        self.join()

