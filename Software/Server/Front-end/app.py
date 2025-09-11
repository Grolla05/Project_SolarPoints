import os
import requests
from flask import Flask, render_template, request

# --- CONFIGURAÇÃO ---
# Esta é a URL da sua API de back-end que está rodando na Vercel.
# VERIFIQUE se 'solarpointsback' é o nome exato do seu projeto de back-end na Vercel.
DATA_SOURCE_URL = "https://solarpointsback.vercel.app/api/items"

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
    # NOVO: Captura os parâmetros de filtro da URL.
    # O 'type=int' tenta converter o valor para inteiro. Se falhar (ex: texto vazio), retorna None.
    min_flow = request.args.get('minFlow', default=None, type=int)
    max_flow = request.args.get('maxFlow', default=None, type=int)

    try:
        # 1. Faz uma requisição GET para a URL da sua API de back-end.
        #    O timeout é uma boa prática para evitar que a página fique esperando para sempre.
        response = requests.get(DATA_SOURCE_URL, timeout=20)
        
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
        
    # Lógica para filtrar os dados em Python
    filtered_items = []
    if items_data: # Apenas filtra se houver dados
        for item in items_data:
            # Pega o valor do contador, assumindo 0 se não existir para evitar erros
            contador = item.get('contador', 0)
            
            # Condições para o filtro
            keep_item = True # Começa assumindo que o item será mantido
            
            if min_flow is not None and contador < min_flow:
                keep_item = False
            
            if max_flow is not None and contador > max_flow:
                keep_item = False
            
            if keep_item:
                filtered_items.append(item)
    
    # MODIFICADO: A contagem de pontos agora é baseada nos itens filtrados.
    online_points_count = len(filtered_items)


    # 5. Renderiza o template 'index.html', passando os dados (ou uma lista vazia)
    #    e a contagem para serem usados na página.
    return render_template(
        "index.html", 
        items=filtered_items, 
        online_points_count=online_points_count, 
        error=error_message
    )
    
# --- PONTO DE ENTRADA DA APLICAÇÃO ---

if __name__ == "__main__":
    # Inicia o servidor para desenvolvimento local.
    app.run(debug=True)