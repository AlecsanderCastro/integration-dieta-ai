from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BEARER_TOKEN = os.getenv("BEARER_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

#Criar usuário
def create_user():
    data = request.json

    payload = {
        "groupId": GROUP_ID,
        "userPhone": data['userPhone'],
        "email": data['email'],
        "expireAt": data.get('expireAt'),
        "removeAt": data.get('removeAt')   
    }

    headers = {
      "Authorization": "Bearer {BEARER_TOKEN}",
      "Content-type":"application/json"
    }

    response = request.post(
        "https://api.dieta.ai/v1/groups/users/add",
        json=payload,
        headers=headers
    )

    return jsonify(response.json()), response.status_code

app.run(port=5000, host='localhost', debug=True)