from flask import Flask, jsonify, request

app = Flask(__name__)


app.run(port=5000, host='localhost', debug=True)