

class Response:

    def __init__(self, body, status=200, content_type='text/plain'):
        self.body = body
        self.status = status
        self.content_type = content_type

    @property
    def headers(self):
        return [
            (b'content_type', self.content_type.encode('utf-8'))
        ]
