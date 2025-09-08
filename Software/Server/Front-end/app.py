import os
import requests
from flask import Flask, render_template

# --- CONFIGURAÇÃO ---
# Esta é a URL da sua API de back-end que está rodando na Vercel.
# VERIFIQUE se 'solar-points-back' é o nome exato do seu projeto de back-end na Vercel.
DATA_SOURCE_URL = "https://solar-points-back.vercel.app/api/items"

# Configuração para encontrar as pastas 'templates' e 'static'.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__,
    template_folder=os.path.join(basedir, 'templates'),
    static_folder=os.path.join(basedir, 'static')
)

# --- ROTA PRINCIPAL ---

@app.route("/")
def index():
    """
    Renderiza a página inicial. Busca os dados da API do back-end
    para popular o mapa.
    """
    items_data = []
    online_points_count = 0
    error_message = None

    try:
        # 1. Faz uma requisição GET para a URL da sua API de back-end.
        #    O timeout é uma boa prática para evitar que a página fique esperando para sempre.
        response = requests.get(DATA_SOURCE_URL, timeout=10)
        
        # 2. Levanta um erro se a resposta da API não for bem-sucedida (ex: 404, 500).
        response.raise_for_status()
        
        # 3. Extrai os dados em formato JSON da resposta.
        items_data = response.json()
        
        # 4. A contagem de pontos é simplesmente o número de itens na lista recebida.
        online_points_count = len(items_data)

    except requests.exceptions.RequestException as e:
        # Captura erros de conexão, timeout, DNS, ou status de erro HTTP.
        print(f"Erro ao buscar dados da API: {e}")
        error_message = "Não foi possível carregar os pontos no mapa. O serviço pode estar temporariamente indisponível."
    except Exception as e:
        # Captura outros erros (ex: JSON inválido na resposta da API).
        print(f"Erro ao processar dados da API: {e}")
        error_message = "Ocorreu um erro ao processar os dados recebidos."

    # 5. Renderiza o template 'index.html', passando os dados (ou uma lista vazia)
    #    e a contagem para serem usados na página.
    return render_template(
        "index.html", 
        items=items_data, 
        online_points_count=online_points_count, 
        error=error_message
    )
    
# --- PONTO DE ENTRADA DA APLICAÇÃO ---

if __name__ == "__main__":
    # Inicia o servidor para desenvolvimento local.
    app.run(debug=True)