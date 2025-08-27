import os
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

basedir = os.path.abspath(os.path.dirname(__file__))

# Define o caminho para o arquivo do banco de dados SQLite.
db_path = os.path.abspath(os.path.join(basedir, "..", "Back-end", "database", "database.db"))
# Cria a URI de conexão com o banco de dados.
db_uri = f"sqlite:///{os.path.abspath(db_path)}"

# Inicializa a aplicação Flask.
# `template_folder` e `static_folder` são configurados para
# apontar para os diretórios corretos, permitindo que a aplicação
# encontre os arquivos HTML, CSS e JavaScript.
app = Flask(__name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static')
)

# Configura a aplicação para usar o banco de dados SQLite definido acima.
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
# Desabilita uma funcionalidade de rastreamento de modificações para otimizar o uso de recursos.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa a extensão SQLAlchemy, que gerencia a conexão com o banco de dados.
db = SQLAlchemy(app)


# --- Definição do Modelo do Banco de Dados ---
# Define a classe do modelo 'Item', que representa a tabela 'dados_esp32' no banco de dados.
# Cada objeto desta classe corresponderá a uma linha na tabela.
class Item(db.Model):
    # Define o nome da tabela no banco de dados.
    __tablename__ = 'dados_esp32'
    
    # Define as colunas da tabela. Cada uma representa um campo no banco.
    # 'id': Chave primária, auto-incrementada.
    id = db.Column('Id', db.Integer, primary_key=True)
    # 'dado1': Um campo para armazenar a contagem de pessoas.
    dado1 = db.Column('Dado1', db.Integer, nullable=False)
    # 'latitude': Um campo para a latitude, usando o tipo REAL (ponto flutuante).
    latitude = db.Column('Latitude', db.REAL, nullable=False)
    # 'longitude': Um campo para a longitude.
    longitude = db.Column('Longitude', db.REAL, nullable=False)

    # Converte um objeto da classe 'Item' em um dicionário Python.
    # Isso é essencial para converter os dados do banco para o formato JSON,
    # que é compreendido pelo navegador.
    def to_dict(self):
        return {
            'dado1': self.dado1,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'id': self.id,
        }

# --- Rotas da Aplicação (Endpoints da API) ---

# Rota de API para obter todos os itens do banco de dados em formato JSON.
# Esta rota é chamada por scripts JavaScript no frontend, por exemplo.
@app.route("/api/items", methods=['GET'])
def get_items():
    try:
        # Consulta todos os registros na tabela 'dados_esp32'.
        items = Item.query.all()
        # Converte a lista de objetos 'Item' em uma lista de dicionários.
        items_data = [item.to_dict() for item in items]
        # Retorna os dados como uma resposta JSON.
        return jsonify(items_data)
    except Exception as e:
        # Em caso de erro, retorna uma mensagem de erro com status 500.
        return jsonify({"error": str(e)}), 500

# Rota principal (página inicial) da aplicação web.
@app.route("/")
def index():
    # Consulta todos os registros na tabela 'dados_esp32'.
    items = Item.query.all()
    # Converte a lista de objetos 'Item' em uma lista de dicionários,
    # que será usada para popular o mapa.
    items_data = [item.to_dict() for item in items]

    # Realiza uma consulta ao banco de dados para contar a quantidade
    # de IDs distintos, ou seja, o número de pontos online.
    online_points_count = db.session.query(func.count(Item.id)).scalar()

    # Renderiza o template 'index.html', passando a lista de itens e a contagem.
    # As variáveis 'items' e 'online_points_count' se tornam disponíveis
    # no template para exibição.
    return render_template("index.html", items=items_data, online_points_count=online_points_count)
    
# --- Ponto de Entrada da Aplicação ---

# Garante que o servidor Flask só seja executado quando o script for
# iniciado diretamente (e não importado por outro script).
if __name__ == "__main__":
    # Inicia o servidor em modo de depuração. O servidor reinicia
    # automaticamente ao detectar mudanças no código, o que é útil
    # para o desenvolvimento.
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")