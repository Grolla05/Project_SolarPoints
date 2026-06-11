/**
 * @file ESP32_Controle_Final_Com_API_e_GPS.cpp
 * @brief Código de controle para sistema de iluminação autônoma com ESP32.
 * * Este programa lê um sensor de movimento (PIR), um sensor de luz (LDR) e um módulo GPS.
 * Se o movimento for detectado E o ambiente estiver escuro, ele aciona um Módulo Relé.
 * * QUANDO a contagem de movimentos atingir 10, os dados (contagem e coordenadas GPS) 
 * são enviados para uma API via requisição POST.
 * * * Conexões de Hardware:
 * - Sensor PIR      -> GPIO 2
 * - Sensor LDR      -> GPIO 34
 * - Módulo Relé     -> GPIO 19
 * - GPS Module TX   -> ESP32 RX (GPIO 16)
 * - GPS Module RX   -> ESP32 TX (GPIO 17)
 */

// --- Bibliotecas Adicionadas para Wi-Fi, HTTP e GPS ---
#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>
#include <WiFiClientSecure.h>

// --- Configurações Adicionadas para o Módulo GPS ---
static const int GPS_RX_PIN = 16;                                                       // Pino GPIO para receber dados do GPS (conectar ao TX do GPS)
static const int GPS_TX_PIN = 17;                                                       // Pino GPIO para transmitir dados para o GPS (conectar ao RX do GPS)
static const uint32_t GPS_BAUD = 9600;                                                  // Baud rate padrão para a maioria dos módulos GPS
TinyGPSPlus gps;                                                                        // Cria um objeto da biblioteca TinyGPS++
HardwareSerial ss(1);                                                                   // Usa a Serial1 do ESP32 para comunicação com o GPS
double latitudeGlobal = 0.0;
double longitudeGlobal = 0.0;

// --- Credenciais de Rede e API ---
WiFiClientSecure wifiClientSecure;
const char* ssid = "NOME_DA_SUA_REDE_WIFI";                                             // Nome da rede Wi-fi no qual o ESP32 irá se conectar
const char* password = "SENHA_DA_SUA_REDE_WIFI";                                        // Senha da rede Wi-fi no qual o ESP32 irá se conectar
const char* apiUrl = "https://solarpointsback.vercel.app/receber-dados-esp";            // Endpoint da API para onde os dados serão enviados (Servidor Back-end)

// --- MAPEAMENTO DOS PINOS DE HARDWARE E VARIÁVEIS GLOBAIS E DE CONTROLE ---
const int pinoPIR = 2;                                                                  // Pino de sinal do sensor de movimento (PIR)
const int pinoLDR = 34;                                                                 // Pino de sinal do sensor de luz (LDR) - Deve ser um pino ADC
const int pinoRele = 19;                                                                // Pino que envia o sinal de controle para o Módulo Relé
bool movimentoDetectado = false;                                                        // "Trava" para garantir que o contador de movimento incremente apenas uma vez por evento
bool releEstaLigado = false;                                                            // Flag para otimizar a impressão no Monitor Serial, mostrando o estado apenas quando ele muda
int contadorMovimento = 0;                                                              // Contador para registrar o número de vezes que o movimento foi detectado

//================================================================================
// FUNÇÃO: PARA OBTER DADOS DO GPS
//================================================================================
void obterCoordenadasGPS(unsigned long timeout) {                                       // Função para obter as coordenadas GPS
  Serial.println("Tentando obter coordenadas do GPS...");
  unsigned long start = millis();                                                       // Marca o tempo de início

  bool gotFix = false;
  do {                                                                                  // Loop até obter um sinal válido ou até 1 segundo se passar
    while (ss.available() > 0) {                                                        // Lê os dados do GPS
      if (gps.encode(ss.read())) {                                                      // Decodifica os dados do GPS
        if (gps.location.isValid() && gps.location.isUpdated()) {                       // Verifica se a localização é válida e foi atualizada
          latitudeGlobal = gps.location.lat();                                          // Atualiza a latitude global
          longitudeGlobal = gps.location.lng();                                         // Atualiza a longitude global
          gotFix = true;
          break;                                                                        // sai do while(ss.available...) assim que tiver um fix atualizado
        }
      }
    }
    if (gotFix) break;                                                                  // sai do do-while se obteve fix
    delay(50);                                                                          // evita busy-loop intenso
  } while (millis() - start < 1000);                                                    // Continua o loop por até 1 segundo

  if (latitudeGlobal != 0.0) {                                                          // Verifica se uma coordenada válida foi obtida
      Serial.print("Coordenadas obtidas: ");
      Serial.print("Latitude= "); Serial.print(latitudeGlobal, 6);                      // Imprime a latitude com 6 casas decimais
      Serial.print(" Longitude= "); Serial.println(longitudeGlobal, 6);                 // Imprime a longitude com 6 casas decimais
  } else {
    Serial.println("Ainda nao foi possivel obter um sinal de GPS valido.");
  }
}

//================================================================================
// FUNÇÃO ENVIO DE DADOS (REQUISIÇÃO HTTP POST PARA A API)
//================================================================================
void envioDeDados() {
  if (WiFi.status() == WL_CONNECTED) {                                                  // Verifica se o ESP32 está conectado ao Wi-Fi
    HTTPClient http;
    Serial.println("Iniciando envio de dados para a API...");
    int contadorParaEnviar = contadorMovimento;                                         // Captura local do contador para evitar que ele seja alterado por outro trecho do código durante o envio
    obterCoordenadasGPS(2000);                                                          // Chama a função para obter as coordenadas GPS
    String url(apiUrl);                                                                 // Escolhe cliente adequado conforme protocolo (HTTP vs HTTPS)
    WiFiClient wifiClient;
    WiFiClientSecure wifiClientSecure;
    if (url.startsWith("https://")) {
      wifiClientSecure.setInsecure();                                                   // CUIDADO: setInsecure() desativa verificação TLS — ok para desenvolvimento/testes, em produção prefira validar o certificado ou usar certificate pinning.
      http.begin(wifiClientSecure, url);
    } else {
      http.begin(wifiClient, url);
    }
    http.addHeader("Content-Type", "application/json");                                 // Define o cabeçalho para indicar que estamos enviando dados em formato JSON
    String jsonPayload = "{\"Contador\":" + String(contadorParaEnviar) +                // Cria o corpo (payload) da requisição em formato JSON exatamente no formato exigido
                         ",\"localizacao\":{\"latitude\":" + String(latitudeGlobal, 6) +
                         ",\"longitude\":" + String(longitudeGlobal, 6) + "}}";

    Serial.print("Payload a ser enviado: ");
    Serial.println(jsonPayload);                                                        // Exibe o payload no Monitor Serial para verificação
    int httpResponseCode = http.POST(jsonPayload);                                      // Envia a requisição POST e obtém o código de resposta do servidor
    if (httpResponseCode > 0) {
      Serial.print("Requisicao POST enviada. Codigo de resposta: ");
      Serial.println(httpResponseCode);
      String response = http.getString();                                               // Pega a resposta do servidor
      Serial.print("Resposta do servidor: ");
      Serial.println(response);
    } else {
      Serial.print("Falha ao enviar requisicao POST. Codigo de erro: ");
      Serial.println(httpResponseCode);
    }
    http.end();                                                                         // Libera os recursos do cliente HTTP
  } else {
    Serial.println("ERRO: Nao foi possivel enviar os dados. ESP32 desconectado");
  }
}

//================================================================================
// FUNÇÃO SETUP: Executada uma única vez quando o ESP32 é ligado
//================================================================================
void setup() {
  Serial.begin(115200);                                                                 // 1. Inicia a comunicação serial para permitir o envio de mensagens de status (debug)
  ss.begin(GPS_BAUD, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);                               // Inicia a Serial1 para comunicação com o GPS  
  Serial.println("Inicializando comunicacao com o Modulo GPS...");                      // Mensagem de status com o Módulo GPS
  Serial.print("Conectando a rede Wi-Fi: ");
  Serial.println(ssid);                                                                 // Mensagem de status com a rede Wi-Fi                  
  WiFi.begin(ssid, password);                                                           // Inicia a conexão Wi-Fi       
  while (WiFi.status() != WL_CONNECTED) {                                               // Aguarda até que a conexão seja estabelecida     
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi Conectado!");                                                 // Mensagem de status
  Serial.print("Endereco IP: ");
  Serial.println(WiFi.localIP());                                                       // Exibe o endereço IP atribuído ao ESP32
  pinMode(pinoPIR, INPUT);                                                              // 2. Configura os pinos dos sensores como ENTRADA (INPUT)
  pinMode(pinoRele, OUTPUT);                                                            // 3. Configura o pino do relé como SAÍDA (OUTPUT)
  digitalWrite(pinoRele, LOW);                                                          // 4. Garante que o relé (e a lâmpada) comece no estado DESLIGADO
  analogReadResolution(12);                                                             // 5. Define a resolução da leitura analógica para 12 bits (valores de 0 a 4095)
  Serial.println("\n>>> Sistema de Iluminacao Autonoma com Rele INICIADO <<<");
  Serial.println("Aguardando condicoes para acionar a lampada...");
}


//================================================================================
// FUNÇÃO LOOP: Executada repetidamente em um ciclo infinito
//================================================================================
void loop() {
  int estadoPIR = digitalRead(pinoPIR);                                                 // ETAPA 1: Ler o estado do sensor de movimento
  if (estadoPIR == HIGH) {                                                              // ETAPA 2: Lógica para contar o movimento apenas na "borda de subida" do sinal
    if (!movimentoDetectado) {
      movimentoDetectado = true;                                                        // Ativa a "trava"
      contadorMovimento++;
      Serial.print("EVENTO: Movimento detectado! Contagem total: ");
      Serial.println(contadorMovimento);
      if (contadorMovimento >= 10) {
        Serial.println("Preparando para enviar dados...");
        envioDeDados(contadorMovimento, latitudeGlobal, longitudeGlobal);               // Chama a função para enviar os dados via API
        contadorMovimento = 0;                                                          // Zera o contador para iniciar uma nova contagem
        Serial.println("Contador de movimento zerado.");
      }
    }
  } else {
    movimentoDetectado = false;                                                         // Libera a "trava" quando não há mais movimento
  }
  
  int valorLDR = analogRead(pinoLDR);                                                   // ETAPA 3: Ler o valor do sensor de luz (LDR)
  const int limiteEscuridao = 1500;                                                     // ETAPA 4: Definir o limite de escuridão
  
  if (movimentoDetectado && (valorLDR > limiteEscuridao)) {                             // ETAPA 5: Lógica principal de decisão
    digitalWrite(pinoRele, HIGH);                                                       // Liga a lâmpada
    if (!releEstaLigado) {
      Serial.println("STATUS: Condicoes atendidas -> Rele ACIONADO");
      releEstaLigado = true;
    }

  } else {
    digitalWrite(pinoRele, LOW);                                                        // Desliga a lâmpada
    if (releEstaLigado) {
      Serial.println("STATUS: Condicoes nao atendidas -> Rele DESLIGADO");
      releEstaLigado = false;
    }
  }
  delay(250);                                                                           // Pequena pausa para estabilidade do loop
}