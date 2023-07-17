from flask import Flask
from waitress import serve
from connectors.db_connector import DBConnector

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    DBConnector()
    serve(app, host="0.0.0.0", port=8080)
