from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Docker! 🐳'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)


# this is flask app it run with gunicorn not uvicorn cause it's wsgi app not asgi app and we need to bind it to the port to make it accessible from outside the container and we need to specify the host to