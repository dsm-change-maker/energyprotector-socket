import asyncio
from ep_sock import client, server, constant, payload, util

# 서버의 Handler 에서 로그 출력 여부를 결정함. True 일 경우 로그 출력
_debug = False


async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    # 만약 _debug 가 True 라면 요청에 대한 로그 출력
    global _debug

    while True:
        # 요청마다 한 줄씩 띄어서 로그 출력
        print() if _debug else None

        # payload_data : 실제 데이터 통신
        # req_chk_payload : 요청 성공/오류 여부 통신
        payload_data: payload.Payload = payload.Payload()
        req_chk_payload: payload.Payload = payload.Payload()

        # 데이터를 클라이언트로부터 읽어옴
        await payload_data.read(reader)

        # 요청 보낸 클라이언트의 정보 저장
        # peer_name : 클라이언트의 ip, port 저장
        # client_type : 클라이언트의 유형 저장
        # recv_client_type : 클라이언트가 데이터를 보내고자 하는 다른 클라이언트의 유형
        # 만약 recv_client_type의 값이 빈 문자열이고 요청한 클라이언트의 타입이
        # - CLIENT_TYPE_API 일 경우 라즈베리파이와 디바이스에 데이터 전달
        # - CLIENT_TYPE_RASPBERRY 일 경우 API 서버와 디바이스에 데이터 전달
        # - CLIENT_TYPE_DEVICE 일 경우 라즈베리파이와 API 서버에 데이터 전달
        peer_name = writer.get_extra_info('peername')
        client_type = payload_data.client_type
        recv_client_type = payload_data.recv_client_type

        # if not payload_data.status:
        #     # 만약 요청 상태가 False 라면 Error 전송
        #     print(f'[S] error : request failed from {peer_name}') if _debug else None
        #     await req_chk_payload.err_write(writer)
        #     return
        if util.is_client_type_close(client_type):
            # 만약 client_type 이 CLIENT_TYPE_CLOSE 라면 클라이언트와의 연결을 종료함
            print(f'[S] closed : client{peer_name}') if _debug else None
            await req_chk_payload.req_ok_write(writer)
            return
        # 만약 클라이언트 타입이 허용되지 않은 값(or 정의되지 않은 값)이라면 Error 전송
        if not util.is_client_type_allowed(client_type):
            print(f'[S] error : disallowed client type - {payload_data.data}') if _debug else None
            print(f'[S] error : disallowed client type - {peer_name}') if _debug else None
            await req_chk_payload.err_write(writer)
            continue

        # 요청을 정상적으로 읽었다면 요청 상태가 정상임을 클라이언트에 전송함
        await req_chk_payload.req_ok_write(writer)
        print(
            f"[S] received: {len(payload_data.data)} bytes - {payload_data.data} from {peer_name}") if _debug else None

        # 현재 클라이언트 정보를 가져와 클라이언트 정보를 가져오는 데 성공하면 reader 와 writer 를 현재의 값으로 변경한다.
        if util.is_client_type_device(client_type):
            client_info = client.get_client(client_type, payload_data.device_id, payload_data.device_type)
        else:
            client_info = client.get_client(client_type, payload_data.raspberry_id, payload_data.raspberry_group)
        client_is_exist = client_info[0]
        if client_is_exist:
            client_info[1].reader = reader
            client_info[1].writer = writer

        # 만약 클라이언트 정보를 가져오는 데 실패한다면(client_is_exist : False) clients 리스트에 현재 클라이언트에 대한 정보를 추가함
        if not client_is_exist:
            if util.is_client_type_device(client_type):
                new_client = client.Client(reader, writer, client_type, device_id=payload_data.device_id,
                                           device_type=payload_data.device_type)
            elif util.is_client_type_api(client_type):
                new_client = client.Client(reader, writer, client_type)
            else:
                new_client = client.Client(reader, writer, client_type, raspberry_id=payload_data.raspberry_id,
                                           raspberry_group=payload_data.raspberry_group)
            client.clients.append(new_client)
            # 등록 성공되었음을 클라이언트에게 알림
            await req_chk_payload.req_ok_write(writer)

            # 새로운 클라이언트가 등록되었음을 로그로 남김
            client_info_str = ''
            if util.is_client_type_raspberry(client_type):
                client_info_str = '(' + payload_data.raspberry_id + ', ' + payload_data.raspberry_group + ')'
            elif util.is_client_type_device(client_type):
                client_info_str = '(' + payload_data.device_id + ', ' + payload_data.device_type + ')'
            print(f'[S] registered : new client{peer_name} - {util.client_type_to_str(client_type)}',
                  client_info_str) if _debug else None
            continue
        elif util.is_client_type_register(recv_client_type):
            await req_chk_payload.err_write(writer)
            print(f'[S] err : Client already registered')
            continue

        # 등록된 클라이언트의 정보를 가져온 결과에 대한 로그 출력
        print(client_info[0], client_info[2]) if _debug else None

        # recv_client_type 에 따라 데이터를 전달할 클라이언트의 정보를 가져옴
        # - recv_client_type 이 CLIENT_TYPE_API 이면 API 서버에 대한 정보
        # - recv_client_type 이 CLIENT_TYPE_DEVICE 이면 디바이스에 대한 정보
        # - recv_client_type 이 CLIENT_TYPE_RASPBERRY 이면 라즈베리파이에 대한 정보
        # - recv_client_type 이 빈 문자열이면 디바이스와 라즈베리파이에 대한 정보
        target_client_info_1 = [False, None, '']
        target_client_info_2 = [False, None, '']
        if util.is_client_type_api(recv_client_type):
            target_client_info_1 = client.get_client(constant.CLIENT_TYPE_API)
        elif util.is_client_type_device(recv_client_type):
            target_client_info_1 = client.get_client(constant.CLIENT_TYPE_DEVICE, payload_data.device_id,
                                                     payload_data.device_type)
        elif util.is_client_type_raspberry(recv_client_type):
            target_client_info_1 = client.get_client(constant.CLIENT_TYPE_RASPBERRY, payload_data.raspberry_id,
                                                     payload_data.raspberry_group)
        elif len(recv_client_type) is 0:
            if util.is_client_type_api(client_type) or util.is_client_type_raspberry(client_type):
                target_client_info_1 = client.get_client(constant.CLIENT_TYPE_DEVICE, payload_data.device_id,
                                                         payload_data.device_type)
            elif util.is_client_type_device(client_type):
                target_client_info_1 = client.get_client(constant.CLIENT_TYPE_API)
            target_client_info_2 = client.get_client(constant.CLIENT_TYPE_RASPBERRY, payload_data.raspberry_id,
                                                     payload_data.raspberry_group)

        # 데이터를 전달할 클라이언트의 정보를 가져오지 못할 경우 오류 전송
        if not target_client_info_1[0]:
            await req_chk_payload.err_write(writer)
            if util.is_client_type_device(recv_client_type) or len(recv_client_type) is 0:
                print(
                    f'[S] error : {util.client_type_to_str(recv_client_type)} not found - {payload_data.device_id, payload_data.device_type}') if _debug else None
            elif util.is_client_type_raspberry(recv_client_type):
                print(
                    f'[S] error : {util.client_type_to_str(recv_client_type)} not found - {payload_data.raspberry_id, payload_data.raspberry_group}') if _debug else None
            else:
                print(
                    f'[S] error : Target not specified - {util.client_type_to_str(recv_client_type)}') if _debug else None
            continue
        if len(recv_client_type) is 0 and not target_client_info_2[0]:
            await req_chk_payload.err_write(writer)
            print(
                f'[S] error : Target not found - {payload_data.raspberry_id, payload_data.raspberry_group}') if _debug else None
            continue

        # 요청 내용에 따른 동작 수행
        if util.is_client_type_api(client_type):
            # API 서버 클라이언트는 디바이스와 통신
            # API Server -> Device
            if util.is_client_type_device(recv_client_type):
                # 디바이스에 모든 정보를 전달하고
                # 디바이스에서는 요청을 성공적으로 처리하면 그 결과를 라즈베리파이에도 전달함.
                await payload_data.write(target_client_info_1[1].writer, to_sock=True)
                print(
                    f'[S] OK : API Server -> Device{payload_data.device_id, payload_data.device_type}') if _debug else None
                continue
            # elif util.is_client_type_raspberry(recv_client_type):
            #     await payload_data.write(target_client_info_1[1].writer, to_raspberry=True)
            #     print(
            #         f'[S] OK : API Server -> Raspberry{payload_data.raspberry_id, payload_data.raspberry_group}') if _debug else None
            #     continue
            # elif len(recv_client_type) is 0:
            #     await payload_data.write(target_client_info_1[1].writer, to_device=True)
            #     await payload_data.write(target_client_info_2[1].writer, to_raspberry=True)
            #     print(
            #         f'[S] OK : API Server -> Device{payload_data.device_id, payload_data.device_type}&Raspberry{payload_data.raspberry_id, payload_data.raspberry_group}') if _debug else None
            #     continue
            await req_chk_payload.err_write(writer)
            print(f'[S] error : Undefined - {util.client_type_to_str(recv_client_type)}') if _debug else None
        elif util.is_client_type_raspberry(client_type):
            # 라즈베리파이 클라이언트는 데이터를 받기만 함
            continue
        elif util.is_client_type_device(client_type):
            # 디바이스는 API 서버와 라즈베리파이와 통신
            # Device -> API Server
            # Device -> Raspberry
            if util.is_client_type_api(recv_client_type):
                await payload_data.write(target_client_info_1[1].writer, without_change=True)
                print(f'[S] OK : Device -> API Server') if _debug else None
                continue
            elif util.is_client_type_raspberry(recv_client_type):
                await payload_data.write(target_client_info_1[1].writer, without_change=True)
                print(
                    f'[S] OK : Device -> Raspberry{payload_data.raspberry_id, payload_data.raspberry_group}') if _debug else None
                continue
            await req_chk_payload.err_write(writer)
            print(f'[S] error : Undefined - {util.client_type_to_str(recv_client_type)}') if _debug else None
            continue


class SocketServer(server.Server):
    def __init__(self, host, port, debug=False):
        global _debug
        super().__init__(host, port, handler_func=handler, debug=debug)
        _debug = debug


if __name__ == "__main__":
    server = SocketServer(constant.SERVER_URL, constant.SERVER_PORT)
    server.run()
