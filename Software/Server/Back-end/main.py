import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Funções do Banco de Dados ---
def setup_database():
    # Cria a pasta 'database' se ela ainda não existir
    os.makedirs('database', exist_ok=True)
    conn = None
    try:
        # Conecta ao banco de dados (o arquivo será criado se não existir)
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        
        # Cria a tabela 'dados_esp32'
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dados_esp32 (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Dado1 INTEGER NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        # Mensagem de que ocorreu tudo certo na criação do banco
        print("Banco de dados e tabela configurados com sucesso!")
        
    # Mensagem de erro caso por algum motivo não seja possível criar ou configurar o database.db
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

def salvar_dados(Dado1, latitude, longitude):
    conn = None
    try:
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        # Insere os dados obtidos na API do ESP32 na tabela do database
        # A instrução INSERT utiliza '?' para segurança, evitando SQL Injection
        cursor.execute('''
            INSERT INTO dados_esp32 (Dado1, latitude, longitude)
            VALUES (?, ?, ?)
        ''', (Dado1, latitude, longitude))

        conn.commit()
        print("Dados salvos no banco de dados com sucesso!")

    # Mensagem de erro caso por algum motivo não seja possível salvar os dados no banco
    except sqlite3.Error as e:
        print(f"Erro ao salvar os dados no banco de dados: {e}")
    finally:
        if conn:
            conn.close()

# Função da Rota API para obter os dados do ESP32
# Define a rota para receber os dados. Está sendo utilizado o método POST.
# O ESP32 deverá enviar a requisição para "http://seu-endereco-ip:3000/Back-end"
@app.route('/Back-end', methods=['POST'])
def receber_dados():
    # 1. Verifica se a requisição é do tipo JSON
    if not request.json:
        return jsonify({"erro": "Requisição deve ser JSON"}), 400

    dados_recebidos = request.json
    print("Dados brutos recebidos do ESP32:")
    print(dados_recebidos)

    # 2. Extrai os dados do JSON
    try:
        Dado1 = dados_recebidos['Dado1']

        # Extrai os dados do objeto chamado 'localizacao'
        localizacao = dados_recebidos['localizacao']
        latitude = localizacao['latitude']
        longitude = localizacao['longitude']
        
    except KeyError as e:
        # Se alguma chave estiver faltando, retorna um erro específico
        return jsonify({"erro": f"Chave JSON faltando: {e}"}), 400

    # 3. Processamento dos dados recebidos
    print("\nDados processados:")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    print(f"Dado1: {Dado1}")

    # 4. Salvar dados no database
    salvar_dados(Dado1, latitude, longitude)

    # 5. Responde ao ESP32 com sucesso
    return jsonify({
        "mensagem": "Dados recebidos e processados com sucesso!",
        "status": "OK"
    }), 200

    # Exemplo: Você pode agora salvar esses dados em um banco de dados,
    # um arquivo de log ou realizar outra ação.
    # Ex: salvar_em_banco_de_dados(latitude, longitude, Dado1)

# Executa o servidor Flask
if __name__ == '__main__':
    # Para criação do banco antes do envio dos dados
    setup_database()
    app.run(host='0.0.0.0', port=3000, debug=True)