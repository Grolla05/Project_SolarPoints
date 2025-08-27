import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Funções do Banco de Dados ---
def setup_database():
    """Cria a pasta e a tabela do banco de dados se não existirem."""
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
        print("Banco de dados e tabela configurados com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Erro ao configurar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

def salvar_ou_atualizar_dados(Dado1, latitude, longitude):
    """
    Verifica se um registro com a mesma localização já existe no banco.
    Se existir, atualiza o 'Dado1' com a soma. Caso contrário, insere um novo registro.
    """
    conn = None
    try:
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()
        
        # 1. Tenta encontrar um registro com a mesma latitude e longitude
        cursor.execute("SELECT Dado1 FROM dados_esp32 WHERE latitude = ? AND longitude = ?", (latitude, longitude))
        registro_existente = cursor.fetchone()

        if registro_existente:
            # 2. Se o registro existir, atualiza o valor de Dado1
            dado1_atual = registro_existente[0]
            novo_dado1 = dado1_atual + Dado1
            
            cursor.execute('''
                UPDATE dados_esp32
                SET Dado1 = ?
                WHERE latitude = ? AND longitude = ?
            ''', (novo_dado1, latitude, longitude))
            
            print(f"Registro atualizado no banco de dados. Dado1 agora é: {novo_dado1}")
        else:
            # 3. Se o registro não existir, insere uma nova linha
            cursor.execute('''
                INSERT INTO dados_esp32 (Dado1, latitude, longitude)
                VALUES (?, ?, ?)
            ''', (Dado1, latitude, longitude))
            
            print("Novo registro inserido no banco de dados.")

        conn.commit()

    except sqlite3.Error as e:
        print(f"Erro ao salvar/atualizar os dados no banco de dados: {e}")
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

        localizacao = dados_recebidos['localizacao']
        latitude = localizacao['latitude']
        longitude = localizacao['longitude']
        
    except KeyError as e:
        return jsonify({"erro": f"Chave JSON faltando: {e}"}), 400

    # 3. Processamento dos dados recebidos
    print("\nDados processados:")
    print(f"Latitude: {latitude}")
    print(f"Longitude: {longitude}")
    print(f"Dado1: {Dado1}")

    # 4. Chamar a nova função para salvar ou atualizar os dados
    salvar_ou_atualizar_dados(Dado1, latitude, longitude)

    # 5. Responde ao ESP32 com sucesso
    return jsonify({
        "mensagem": "Dados recebidos e processados com sucesso!",
        "status": "OK"
    }), 200

# Executa o servidor Flask
if __name__ == '__main__':
    # Para criação do banco antes do envio dos dados
    setup_database()
    app.run(host='0.0.0.0', port=3000, debug=True)