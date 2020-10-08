import asyncio
from ep_sock import payload


async def handler(_, writer: asyncio.StreamWriter):
    send_payload: payload.Payload = payload.Payload()
    print('[S] Request Handler function does not exist')
    await send_payload.err_write(writer)


async def run_server(host, port, handler_func=handler, debug=False):
    print('[S] RUN_SERVER') if debug else None
    server = await asyncio.start_server(handler_func, host=host, port=port)
    async with server:
        await server.serve_forever()


class Server:
    def __init__(self, host, port, handler_func=handler, debug=False):
        self.host = host
        self.port = port
        self.handler_func = handler_func
        self.debug = debug

    async def _run(self):
        await asyncio.wait([run_server(self.host, self.port, handler_func=self.handler_func, debug=self.debug)])

    def run(self):
        asyncio.run(self._run())
