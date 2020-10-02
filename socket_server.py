import asyncio
import payload
import client
import constant


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
            print(f'[S] notice : client{peer_name} closed')
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
                print(f'[S] registered : new client{peer_name} - CLIENT_TYPE_RASPBERRY({payload_data.raspberry_id, payload_data.raspberry_group})')
                continue

        if payload_data.client_type == constant.CLIENT_TYPE_API:
            target = client.get_client(constant.CLIENT_TYPE_RASPBERRY, payload_data.raspberry_id,
                                       payload_data.raspberry_group)
            if target is None:
                print(f'[S] error : get_client(CLIENT_TYPE_RASPBERRY, {payload_data.raspberry_id}, {payload_data.raspberry_group}) fails')
                await req_chk_payload.err_write(writer)
                continue
            await payload_data.write(target.writer, to_raspberry=True)
            continue
        elif payload_data.client_type == constant.CLIENT_TYPE_RASPBERRY:
            target = client.get_client(constant.CLIENT_TYPE_API)
            if target is None:
                print('[S] error : get_client(CLIENT_TYPE_API) fails')
                await req_chk_payload.err_write(writer)
                continue
            await payload_data.write(target.writer, to_sock=True)
            continue


async def run_server():
    # 서버를 생성하고 실행
    print('[S] RUN_SERVER')
    server = await asyncio.start_server(handler, host=constant.SERVER_URL, port=constant.SERVER_PORT)
    async with server:
        # serve_forever()를 호출해야 클라이언트와 연결을 수락합니다.
        await server.serve_forever()


async def main(debug=False):
    from socket_client_api import run_client_api
    await asyncio.wait([run_server(), run_client_api(debug=debug)])


if __name__ == "__main__":
    asyncio.run(main(debug=True))
