# Manual de Execução do Sistema Solar Points

Este manual fornece um guia passo a passo para configurar e executar os servidores de back-end e front-end do sistema Solar Points, além de demonstrar como simular o envio de dados usando o Postman.

### 1. Configuração Inicial

Antes de executar os servidores, garanta que você tenha o Python e as bibliotecas necessárias instaladas.

1. **Instalar Flask:** Abra o terminal e instale a biblioteca Flask.
    ```bash
    pip install Flask
    ```
2. **Organizar os Arquivos:** Certifique-se de que os seus arquivos estejam organizados nas seguintes pastas, conforme a estrutura do projeto:
    * `Back-end/main.py`
    * `Front-end/app.py`
    * `Front-end/templates/` (com `index.html` e `layout.html`)
    * `Front-end/static/` (com `Maps_API.js` e `global.css`)
    * `database/` (pasta que será criada automaticamente)

### 2. Executando o Servidor de Back-end

O servidor de back-end (`main.py`) é responsável por receber os dados enviados pelo ESP32 e salvá-los no banco de dados.

1. Abra um terminal e navegue até a pasta `Back-end`.
2. Execute o servidor com o seguinte comando:
    ```bash
    python main.py
    ```
3. Você verá uma mensagem no terminal indicando que o servidor está rodando. Por padrão, ele será executado na porta **3000**.
    ```
    * Running on [http://0.0.0.0:3000/](http://0.0.0.0:3000/)
    ```

### 3. Executando o Servidor de Front-end

O servidor de front-end (`app.py`) é responsável por consultar os dados do banco e exibi-los em uma página web com o mapa.

1. Abra um **segundo terminal** e navegue até a pasta `Front-end`.
2. Execute o servidor com o seguinte comando:
    ```bash
    python app.py
    ```
3. Você verá uma mensagem no terminal indicando que o servidor está rodando. Por padrão, ele será executado na porta **5000**.
    ```
    * Running on [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    ```
4. Abra seu navegador e acesse o endereço `http://localhost:5000` para ver a interface do mapa.

### 4. Simulação de Dados com Postman

Com os dois servidores rodando, você pode usar o Postman para simular o envio de dados do ESP32 para o back-end.

1. Abra o Postman e crie uma nova requisição.
2. Defina o método da requisição como **`POST`**.
3. No campo de URL, insira o endereço do seu servidor de back-end: `http://localhost:3000/Back-end`.
4. Vá para a aba **`Body`**, selecione a opção **`raw`** e escolha **`JSON`** no menu suspenso.
5. Insira o seguinte JSON no corpo da requisição:
    ```json
    {
      "Dado1": 150,
      "localizacao": {
        "latitude": -23.57,
        "longitude": -46.79
      }
    }
    ```
    * Você pode alterar os valores de `Dado1`, `latitude` e `longitude` para simular diferentes envios. Se você enviar dados com a mesma latitude e longitude, o valor de `Dado1` será somado.

6. Clique no botão **`Send`**.

### Verificação

* **No Postman:** Você deverá receber uma resposta com status **`200 OK`** e a mensagem `"Dados recebidos e processados com sucesso!"`.
* **No terminal do Back-end (`main.py`):** Você verá as mensagens de log confirmando que os dados foram recebidos e salvos (ou atualizados) no banco de dados.
* **No navegador (Front-end):** Atualize a página e você verá o novo ponto de dados aparecer no mapa.