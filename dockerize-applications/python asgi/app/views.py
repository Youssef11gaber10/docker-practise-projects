from urllib.parse import parse_qs

from app import connection
from response import Response



async def set(request):
    query_string = request.query_string
    if query_string:
        data = parse_qs(query_string)
    else:
        data = {}

    if 'key' in data and 'value' in data:
        key = data['key'][0]
        value = data['value'][0]
        await connection('execute', 'set', key, value)
    return Response('OK', status=200, content_type='text/plain')


async def get(request):
    query_string = request.query_string
    if query_string:
        data = parse_qs(query_string)
    else:
        data = {}

    if 'key' in data:
        key = data['key'][0]
        value = await connection('execute', 'get', key)
    return Response(value, status=200, content_type='text/plain')

