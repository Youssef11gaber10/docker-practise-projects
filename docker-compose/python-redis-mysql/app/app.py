from flask import Flask, jsonify
import redis
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT' )),
    db=0
)

# MySQL configuration
def get_db_connection():
    return mysql.connector.connect(
        #os .getenv is go inside machine and looking for env variable with name MYSQL_ROOT_PASSWORD in env file 
        #so you must set these enviroment vairable with dockerfile or dockercompse or docker run -e  
        host=os.getenv('MYSQL_HOST'), # so the app gets this enviromental vairable throw envrioments for example will be mysql and this name of the servcie will resolve to the ip address of mysql container and this is how the app will connect to mysql container
        # when you run mysql container give it -e  with docker file give it ENV in compose give it enviroments 
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE')
    )

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Flask application!"})

@app.route('/redis')
def redis_test():
    try:
        redis_client.set('test_key', 'Hello from Redis!')
        value = redis_client.get('test_key')
        return jsonify({"redis_value": value.decode('utf-8')})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mysql')
def mysql_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({"mysql_status": "Connected successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)

