import asyncio
from ep_sock import client, constant, payload, util
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

        self.device_read: bool = False
        self.device_req_ok: bool = False


async def run_client_raspberry(signal: ClientSendSignalRaspberry, host=constant.SERVER_URL, port=constant.SERVER_PORT,
                               debug=False):
    if debug:
        print('[C] RUN CLIENT_RASPBERRY')
    client_raspberry = ClientRaspberry(signal.raspberry_id, signal.raspberry_group, host, port)
    await client_raspberry.connect()
    await client.register_new_client_with_log(client_raspberry, debug=True)

    while True:
        # Device 에서 버튼이 눌렸을 때의 패킷 구조
        # 'OK;6;CTL;;unit_index;on_off;device_id;device_type;\n'
        await signal.recv_data.read(client_raspberry.reader)
        print('[C] received : ', signal.recv_data.data) if debug else None
        if util.is_device_req_packet(signal.recv_data.data):
            signal.device_req_ok = True
            while True:
                if not signal.device_req_ok:
                    break
        else:
            signal.device_read = True
            while True:
                if not signal.device_read:
                    break
        continue

    signal.req_ok = await client_raspberry.close()
    signal.close = False
    print('[C]', 'CLOSED' if signal.req_ok else 'FAILED TO CLOSE') if debug else None


class RunClientRaspberryThread(threading.Thread):
    def __init__(self, signal: ClientSendSignalRaspberry, host=constant.SERVER_URL, port=constant.SERVER_PORT,
                 debug=False):
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

    def stop(self):
        self.signal.close = True
        while True:
            if not self.signal.close:
                break
        self.join()


