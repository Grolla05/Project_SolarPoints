import os
import sqlalchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS NA NUVEM ---
# A URL de conexão DEVE ser configurada como uma variável de ambiente na Vercel.
# Exemplo de URL: "postgresql://user:password@host:port/database"
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa a extensão SQLAlchemy
db = SQLAlchemy(app)


# --- ROTA PARA O ESP32 ENVIAR DADOS ---
@app.route('/receber-dados-esp', methods=['POST'])
def receber_dados_esp():
    """Recebe dados do ESP32 e salva/atualiza no banco de dados na nuvem."""
    if not request.json:
        return jsonify({"erro": "A requisição deve ser no formato JSON"}), 400

    dados = request.json
    print(f"Dados recebidos do ESP32: {dados}")

    try:
        contador = int(dados['Contador'])
        latitude = float(dados['localizacao']['latitude'])
        longitude = float(dados['localizacao']['longitude'])
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"erro": f"Dados JSON inválidos ou faltando: {e}"}), 400

    try:
        # Usando a engine do SQLAlchemy para executar SQL puro com segurança
        engine = db.get_engine()
        with engine.connect() as connection:
            # 1. Verifica se já existe um registro para esta localização
            result = connection.execute(
                text("SELECT \"Contador\" FROM dados_esp32 WHERE latitude = :lat AND longitude = :lon"),
                {"lat": latitude, "lon": longitude}
            ).fetchone()

            if result:
                # 2. Se existe, atualiza o contador somando o valor recebido
                contador_atual = result[0]
                novo_contador = contador_atual + contador
                connection.execute(
                    text("UPDATE dados_esp32 SET \"Contador\" = :novo_cont WHERE latitude = :lat AND longitude = :lon"),
                    {"novo_cont": novo_contador, "lat": latitude, "lon": longitude}
                )
                print(f"Registro atualizado. Novo contador: {novo_contador}")
            else:
                # 3. Se não existe, insere um novo registro
                connection.execute(
                    text("INSERT INTO dados_esp32 (\"Contador\", latitude, longitude) VALUES (:cont, :lat, :lon)"),
                    {"cont": contador, "lat": latitude, "lon": longitude}
                )
                print("Novo registro inserido.")
            
            # Efetiva a transação
            connection.commit()

        return jsonify({"mensagem": "Dados processados com sucesso!"}), 200

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"Erro de banco de dados: {e}")
        return jsonify({"erro": "Ocorreu um erro ao interagir com o banco de dados."}), 500
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return jsonify({"erro": "Ocorreu um erro inesperado no servidor."}), 500


# --- ROTA PARA O FRONT-END OBTER OS DADOS ---
@app.route('/api/items', methods=['GET'])
def get_items_for_frontend():
    """Exporta todos os dados do banco para serem consumidos pelo front-end."""
    try:
        engine = db.get_engine()
        with engine.connect() as connection:
            # Seleciona todos os registros da tabela
            result = connection.execute(text("SELECT id, \"Contador\", latitude, longitude FROM dados_esp32")).fetchall()
            
            # Converte o resultado em uma lista de dicionários (formato JSON)
            items_data = [
                {"id": row[0], "contador": row[1], "latitude": row[2], "longitude": row[3]}
                for row in result
            ]
            
            return jsonify(items_data)
            
    except Exception as e:
        print(f"Erro ao buscar dados para o front-end: {e}")
        return jsonify({"erro": "Não foi possível obter os dados."}), 500


# O if __name__ == '__main__' é útil para testes locais, mas não é executado na Vercel.
if __name__ == '__main__':
    # Para testes locais, você pode usar um arquivo .env para definir DATABASE_URL
    # from dotenv import load_dotenv
    # load_dotenv()
    app.run(host='0.0.0.0', port=3000, debug=True)
