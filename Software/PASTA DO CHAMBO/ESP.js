// Função assíncrona para enviar dados de acionamento e localização para o backend.
async function enviarDadosParaBackend(acionamento, localizacao) {

    // 1. Defina o endereço IP e a porta do seu backend.
    //    IMPORTANTE: Substitua 'IP_DO_SEU_BACKEND' e 'PORTA_DO_SEU_BACKEND' pelos valores corretos.
    const backendIP = 'IP_DO_SEU_BACKEND';
    const backendPort = 'PORTA_DO_SEU_BACKEND'; // Exemplo: 3000, 8080, etc.
    const endpoint = '/api/receber-dados'; // Substitua pelo endpoint correto da sua API

    // 2. Crie o objeto com os dados que você deseja enviar.
    const dadosParaEnviar = {
        acionamento: acionamento,
        localizacao: localizacao,
        timestamp: new Date().toISOString() // Adiciona um timestamp para registro
    };

    // 3. Monte a URL completa do endpoint.
    const url = `http://${backendIP}:${backendPort}${endpoint}`;

    try {
        // 4. Use a função 'fetch' para fazer a requisição HTTP POST.
        const response = await fetch(url, {
            method: 'POST', // Define o método da requisição como POST
            headers: {
                // Informa ao servidor que o corpo da requisição é um JSON
                'Content-Type': 'application/json'
            },
            // Converte o objeto JavaScript em uma string JSON para envio
            body: JSON.stringify(dadosParaEnviar)
        });

        // 5. Verifique se a requisição foi bem-sucedida (código de status 200-299).
        if (response.ok) {
            console.log('Dados enviados com sucesso para o backend!');
            const resultado = await response.json(); // Tenta ler a resposta JSON do servidor
            console.log('Resposta do servidor:', resultado);
            return resultado;
        } else {
            // Se a resposta não for 'ok', significa que houve um erro no servidor.
            console.error('Falha ao enviar dados. Status:', response.status);
            const erro = await response.text(); // Tenta ler a mensagem de erro
            console.error('Mensagem de erro do servidor:', erro);
            throw new Error(`Erro do servidor: ${response.status}`);
        }

    } catch (error) {
        // 6. Trata erros de rede, como falha de conexão.
        console.error('Erro ao fazer a requisição:', error);
        alert(`Erro de conexão com o backend: ${error.message}`);
    }
}

// =========================================================================
// Exemplo de como usar a função
// =========================================================================

// Simule o acionamento e a obtenção de localização do ESP
const tipoDeAcionamento = 'Sensor_Movimento'; // Exemplo: 'Botao_Pressionado', 'Sensor_Temperatura', etc.
const latitude = -23.55052; // Exemplo de latitude
const longitude = -46.633308; // Exemplo de longitude

// Chama a função para enviar os dados
enviarDadosParaBackend(tipoDeAcionamento, { latitude: latitude, longitude: longitude });