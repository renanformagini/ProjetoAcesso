from flask import Flask, request, jsonify
import sqlite3
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

app = Flask(__name__)

config = PNConfiguration()
config.subscribe_key = 'sub-c-bd68d7b0-47d6-44c9-95db-a93d23712ab7'
config.publish_key = 'pub-c-eb54217e-3bfa-4f08-9990-4b9632e69e04'
pubnub = PubNub(config)

def connect_db():
    return sqlite3.connect('data.db')

def create_tables():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS colaboradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                permissao TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                colaborador_id INTEGER,
                data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                tipo TEXT,
                FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id)
            )
        """)
        conn.commit()

create_tables()

@app.route('/acesso', methods=['POST'])
def registrar_acesso():
    colaborador_id = request.json.get('colaborador_id')
    tipo = request.json.get('tipo') 
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO acessos (colaborador_id, tipo) VALUES (?, ?)", (colaborador_id, tipo))
        conn.commit()
    
    pubnub.publish().channel('meu_canal').message({"text": f"Colaborador {colaborador_id} registrou {tipo}."}).sync()
    
    return jsonify({"message": "Acesso registrado!"}), 201

@app.route('/colaboradores', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gerenciar_colaboradores():
    if request.method == 'POST':
        nome = request.json.get('nome')
        permissao = request.json.get('permissao')
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO colaboradores (nome, permissao) VALUES (?, ?)", (nome, permissao))
            conn.commit()
        return jsonify({"message": "Colaborador adicionado!"}), 201

    if request.method == 'GET':
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM colaboradores")
            colaboradores = cursor.fetchall()
        return jsonify([{"id": col[0], "nome": col[1], "permissao": col[2]} for col in colaboradores]), 200

    if request.method == 'PUT':
        id = request.json.get('id')
        nome = request.json.get('nome')
        permissao = request.json.get('permissao')
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE colaboradores SET nome = ?, permissao = ? WHERE id = ?", (nome, permissao, id))
            conn.commit()
        return jsonify({"message": "Colaborador atualizado!"}), 200

    if request.method == 'DELETE':
        id = request.json.get('id')
        with connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM colaboradores WHERE id = ?", (id,))
            conn.commit()
        return jsonify({"message": "Colaborador excluído!"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
