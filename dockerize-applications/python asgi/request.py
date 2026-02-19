from collections import namedtuple


Request = namedtuple(
            'Request', ['headers', 'body', 'method', 'path', 'query_string']
          )


class HttpProcessor:
    def __init__(self, asgi_scope, body):
        self.__asgi_scope = asgi_scope
        self.__body = body

    def get_parsed_headers(self):
        headers = {
           header_name: header_value
           for header_name, header_value in self.__asgi_scope['headers']
        }
        return headers

    def get_parsed_body(self):
        return self.__body.decode('utf-8')

    def get_parsed_query(self):
        return self.__asgi_scope['query_string'].decode('utf-8')

    def get_parsed_method(self):
        return self.__asgi_scope['method']

    def get_parsed_path(self):
        return self.__asgi_scope['path']

    def get_request(self):
        headers = self.get_parsed_headers()
        body = self.get_parsed_body()
        method = self.get_parsed_method()
        path = self.get_parsed_path()
        query_string = self.get_parsed_query()
        return Request(
            headers,
            body,
            method,
            path,
            query_string
        )
