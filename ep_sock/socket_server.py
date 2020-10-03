import asyncio
from ep_sock import client, constant, payload


async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        payload_data: payload.Payload = payload.Payload()
        req_chk_payload: payload.Payload = payload.Payload()
        await payload_data.read(reader)

        peer_name = writer.get_extra_info('peername')
        if not payload_data.status:
            print(f'[S] error : request failed from {peer_name}')
            await req_chk_payload.err_write(writer)
            return
        if payload_data.client_type == constant.CLIENT_TYPE_CLOSE:
            print(f'[S] closed : client{peer_name}')
            await req_chk_payload.req_ok_write(writer)
            return

        await req_chk_payload.req_ok_write(writer)

        print(f"[S] received: {len(payload_data.data)} bytes from {peer_name}")
        if client.get_client(payload_data.client_type, payload_data.raspberry_id, payload_data.raspberry_group) is None:
            if payload_data.client_type == constant.CLIENT_TYPE_API:
                client.clients.append(client.Client(reader, writer, client_type=payload_data.client_type))
                await req_chk_payload.req_ok_write(writer)
                print(f'[S] registered : new client{peer_name} - CLIENT_TYPE_API')
                continue
            elif payload_data.client_type == constant.CLIENT_TYPE_RASPBERRY:
                client.clients.append(client.Client(reader, writer, payload_data.client_type, payload_data.raspberry_id,
                                                    payload_data.raspberry_group))
                await req_chk_payload.req_ok_write(writer)
                print(
                    f'[S] registered : new client{peer_name} - CLIENT_TYPE_RASPBERRY({payload_data.raspberry_id, payload_data.raspberry_group})')
                continue

        if payload_data.client_type == constant.CLIENT_TYPE_API:
            target = client.get_client(constant.CLIENT_TYPE_RASPBERRY, payload_data.raspberry_id,
                                       payload_data.raspberry_group)
            if target is None:
                print(
                    f'[S] error : get_client(CLIENT_TYPE_RASPBERRY, {payload_data.raspberry_id}, {payload_data.raspberry_group})')
                await req_chk_payload.err_write(writer)
                continue
            await payload_data.write(target.writer, to_raspberry=True)
            continue
        elif payload_data.client_type == constant.CLIENT_TYPE_RASPBERRY:
            target = client.get_client(constant.CLIENT_TYPE_API)
            if target is None:
                print('[S] error : get_client(CLIENT_TYPE_API)')
                await req_chk_payload.err_write(writer)
                continue
            await payload_data.write(target.writer, to_sock=True)
            continue


async def run_server(host, port):
    print('[S] RUN_SERVER')
    server = await asyncio.start_server(handler, host=host, port=port)
    async with server:
        await server.serve_forever()


class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def _run(self):
        await asyncio.wait([run_server(self.host, self.port)])

    def run(self):
        asyncio.run(self._run())


if __name__ == "__main__":
    server = SocketServer(constant.SERVER_URL, constant.SERVER_PORT)
    server.run()
