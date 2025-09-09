import os
import sqlalchemy
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÃO CORRETA DO BANCO DE DADOS ---
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- ROTA PARA O ESP32 ENVIAR DADOS ---
@app.route('/receber-dados-esp', methods=['POST'])
def receber_dados_esp():
    """Recebe dados do ESP32 e salva/atualiza no banco de dados na nuvem."""
    if not request.json:
        return jsonify({"erro": "A requisição deve ser no formato JSON"}), 400

    dados = request.json
    print(f"DADOS BRUTOS RECEBIDOS: {dados}")

    try:
        contador = int(dados['Contador'])
        latitude = float(dados['localizacao']['latitude'])
        longitude = float(dados['localizacao']['longitude'])
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"erro": f"Dados JSON inválidos ou faltando: {e}"}), 400

    try:
        engine = db.get_engine()
        with engine.connect() as connection:
            # --- INÍCIO DA MUDANÇA ---
            # Use um bloco de transação para garantir a atomicidade
            with connection.begin() as trans:
                result = connection.execute(
                    text("SELECT \"Contador\" FROM dados_esp32 WHERE latitude = :lat AND longitude = :lon"),
                    {"lat": latitude, "lon": longitude}
                ).fetchone()

                if result:
                    contador_atual = result[0]
                    novo_contador = contador_atual + contador
                    connection.execute(
                        text("UPDATE dados_esp32 SET \"Contador\" = :novo_cont WHERE latitude = :lat AND longitude = :lon"),
                        {"novo_cont": novo_contador, "lat": latitude, "lon": longitude}
                    )
                    print(f"LOG: Registro atualizado. Novo contador: {novo_contador}")
                else:
                    connection.execute(
                        text("INSERT INTO dados_esp32 (\"Contador\", latitude, longitude) VALUES (:cont, :lat, :lon)"),
                        {"cont": contador, "lat": latitude, "lon": longitude}
                    )
                    print("LOG: Novo registro inserido.")

        return jsonify({"mensagem": "Dados processados com sucesso!"}), 200

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"ERRO DE BANCO DE DADOS: {e}")
        return jsonify({"erro": "Ocorreu um erro ao interagir com o banco de dados."}), 500
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        return jsonify({"erro": "Ocorreu um erro inesperado no servidor."}), 500


# --- ROTA PARA O FRONT-END OBTER OS DADOS ---
@app.route('/api/items', methods=['GET'])
def get_items_for_frontend():
    """Exporta todos os dados do banco para serem consumidos pelo front-end."""
    print("\n--- INICIANDO REQUISIÇÃO EM /api/items ---")
    items_data = []  # Inicializa a variável para garantir que ela exista no 'finally'
    
    try:
        engine = db.get_engine()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT id, \"Contador\", latitude, longitude FROM dados_esp32")).fetchall()
            
            print(f"LOG: Dados brutos lidos do banco: {result}")

            items_data = [
                {"id": row[0], "contador": row[1], "latitude": row[2], "longitude": row[3]}
                for row in result
            ]
            
            print(f"LOG: Dados formatados com sucesso antes do envio.")
            
    except Exception as e:
        print(f"ERRO AO BUSCAR DADOS PARA FRONT-END: {e}")
        # Retorna uma lista vazia em caso de erro para não quebrar o front-end
        items_data = [] 
    
    finally:
        # LOG ADICIONADO: Este log será executado SEMPRE, mostrando o que está sendo enviado.
        print(f"LOG FINAL (Conteúdo do GET): {items_data}")
        print("--- FIM DA REQUISIÇÃO ---")
        # A resposta é movida para o bloco 'finally' para garantir que sempre aconteça.
        return jsonify(items_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)