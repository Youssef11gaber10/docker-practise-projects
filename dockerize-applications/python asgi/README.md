Simple ASGI App
---------------

I created this to try out ASGI https://github.com/django/asgiref/blob/master/specs/asgi.rst

The app has two urls:

  /get
     params - key
     This get the value of the key from the redis

 /set
     params - key, value
     This sets the value of key from the redis

 *Note*: This assumes redis is running locally at default port


This can be run by `uvicorn --port <port> asgi_app:ASGIApplication` (uvicorn needs to installed.)
