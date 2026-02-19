import asyncio
import inspect

from request import HttpProcessor, Request
from main import main


HTTP_REQUEST_EVENT = 'http.request'
HTTP_RESPONSE_START = 'http.response.start'
HTTP_RESPONSE_BODY = 'http.response.body'


class ASGIApplication:

    """ASGI Application"""

    def __init__(self, scope):
        self.scope = scope

    async def process_request(self, request):
        response = await main(request)
        return response

    async def start_response(self, response, send):
        await send({
            'type': HTTP_RESPONSE_START,
            'status': response.status,
            'headers': response.headers
        })

    async def send_body(self, response, send):
        if isinstance(response.body, str):
            await send({
                'type': HTTP_RESPONSE_BODY,
                'body': response.body.encode('utf-8')
            })
        elif inspect.isasyncgen(response.body):
            async for chunk in response.body:
                await send({
                    'type': HTTP_RESPONSE_BODY,
                    'body': response.body.encode('utf-8')
                })
        else:
            raise Exception('Cannot handle')

    async def get_request_body(self, recieve):
        end_of_body = False
        body = b''
        while not end_of_body:
            event = await recieve()
            if event['type'] == HTTP_REQUEST_EVENT:
                body += body
                end_of_body = not event['more_body']
        return body

    async def __call__(self, recieve, send):
        body = await self.get_request_body(recieve)
        http_processor = HttpProcessor(self.scope, body)
        request = http_processor.get_request()
        response = await self.process_request(request)
        await self.start_response(response, send)
        await self.send_body(response, send)

