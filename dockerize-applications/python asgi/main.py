import re

from response import Response
from app import urls


async def main(request):
    for path, view in urls:
        path_to_match = request.path.lstrip('/')
        if re.match(path, path_to_match):
            return await view(request)
    return Response('Not Found', status=404, content_type='text/plain')

