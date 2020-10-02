import asyncio
import constant
import client

_port = 7770


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


async def run_client_api(debug=False):
    if debug:
        print('[C] RUN CLIENT_API')
    client_api = ClientApi(constant.SERVER_URL, constant.SERVER_PORT)
    await client_api.connect()
    while True:
        if await client_api.write_control('test_r_id', 'test_r_group', 'test_d_id', 'test_d_type', 0, True):
            if debug:
                print('[C] request Success')
            await client_api.read()
            if debug:
                print('[C] recived : ', client_api.recv_data.data)
            if client_api.recv_data.status and client_api.recv_data.client_type == constant.CLIENT_TYPE_REQ_OK:
                if debug:
                    print('[C] registered as a new client')
                continue
            break
        if debug:
            print('[C] Request failed')

    is_closed = await client_api.close()
    if debug:
        print('[C]', 'CLOSED' if is_closed else 'FAILED TO CLOSE')


async def main(debug=False):
    await asyncio.wait([run_client_api(debug=debug)])


if __name__ == "__main__":
    asyncio.run(main(debug=True))
