import os
import pymysql
import requests
from dotenv import load_dotenv

# Apenas útil em testes locais
load_dotenv()

# Variáveis de ambiente
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
OWNER_ID = 5511915229818

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-type": "application/json"
}

def formatar_telefone(telefone):
    telefone = ''.join(filter(str.isdigit, telefone))
    if not telefone.startswith("55"):
        telefone = "55" + telefone
    return telefone

def create_user(userPhone, email):
    payload = {
        "groupId": GROUP_ID,
        "userPhone": userPhone,
        "email": email
    }

    create_response = requests.post(
        "https://api.dieta.ai/v1/groups/users/add",
        json=payload,
        headers=HEADERS
    )

    att_payload = {
        "groupId": GROUP_ID,
        "userPhone": userPhone,
        "email": email,
        "ownerId": OWNER_ID,
        "set": {
            "preferences": {
                "reminders": False
            }
        }
    }

    update_response = requests.post(
        "https://api.dieta.ai/v1/groups/users/update",
        json=att_payload,
        headers=HEADERS
    )

    return {
        "userPhone": userPhone,
        "email": email,
        "create_status": create_response.status_code,
        "update_status": update_response.status_code
    }

def lambda_handler(event, context):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        cursorclass=pymysql.cursors.DictCursor
    )

    my_cursor = conn.cursor()
    my_cursor.execute("""
        SELECT 
    p.id_paciente,
    p.nome,
    p.telefone,
    p.email,
    t.item
FROM pacientes p
JOIN tratamentos t 
    ON t.id_paciente = p.id_paciente
WHERE (t.item LIKE '%app%')
  AND t.etapa IN ('COMPLETED', 'SHIPMENT', 'CONTRACT')

    """)
    pacientes = my_cursor.fetchall()

    resultados = []

    for paciente in pacientes:
        telefone = formatar_telefone(paciente['telefone'])
        email = paciente.get('email') or "sememail@teste.com"

        try:
            resultado = create_user(telefone, email)
            resultados.append(resultado)

            # Marca como enviado
            my_cursor.execute(
                "UPDATE tratamentos SET enviado_dieta = TRUE WHERE id = %s",
                (paciente['id'],)
            )
            conn.commit()
        except Exception as e:
            resultados.append({"erro": str(e), "paciente": paciente["nome"]})

    my_cursor.close()
    conn.close()

    return {
        "statusCode": 200,
        "body": {
            "mensagem": f"{len(resultados)} pacientes processados",
            "resultados": resultados
        }
    }
