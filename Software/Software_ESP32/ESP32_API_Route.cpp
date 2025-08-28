#include <WiFi.h>
#include <HTTPClient.h>
#include <TinyGPS++.h>
#include <HardwareSerial.h>

// --- Configurações de Rede ---
const char* ssid = "NOME_DA_SUA_REDE_WIFI";       // Coloque o nome da sua rede Wi-Fi aqui
const char* password = "SENHA_DA_SUA_REDE_WIFI"; // Coloque a senha da sua rede aqui
const char* serverUrl = "http://SEU_IP_DO_COMPUTADOR:3000/Back-end"; // Altere para o IP da máquina onde o back-end está rodando

// --- Configurações dos Pinos e Variáveis Globais ---
const int pirPin = 2;
const int ldrPin = 34;
const int ledPin = 18;
int contadorMovimento = 0; 
bool movimentoDetectado = false; 

// --- Configurações do Módulo GPS ---
HardwareSerial gpsSerial(1);
TinyGPSPlus gps;

// --- Configurações do LED PWM no ESP32 ---
const int ledChannel = 0;
const int ledFreq = 5000;
const int ledResolution = 8;

// --- Funções para controle de PWM no ESP32 ---
void setLedBrightness(int duty) {
  ledcWrite(ledChannel, duty);
}

// --- Funções para ler os dados do GPS ---
void lerDadosGPS() {
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }
}

// --- Função que envia os dados para o back-end via API ---
void EnviarDados() {
  // 1. Verifica se o ESP32 está conectado ao Wi-Fi
  if (WiFi.status() == WL_CONNECTED) {
    
    // 2. Monta o corpo da requisição (payload) no formato JSON
    String jsonPayload = "{";
    jsonPayload += "\"Contador\":";
    jsonPayload += contadorMovimento;
    jsonPayload += ",";
    jsonPayload += "\"localizacao\":{";

    if (gps.location.isValid()) {
      jsonPayload += "\"latitude\":";
      jsonPayload += String(gps.location.lat(), 6);
      jsonPayload += ",";
      jsonPayload += "\"longitude\":";
      jsonPayload += String(gps.location.lng(), 6);
    } else {
      jsonPayload += "\"latitude\":null,";
      jsonPayload += "\"longitude\":null";
    }
    jsonPayload += "}}";

    Serial.println("--- Enviando Dados para o Back-end ---");
    Serial.print("JSON a ser enviado: ");
    Serial.println(jsonPayload);

    // 3. Inicia a requisição HTTP
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json"); // Informa que o conteúdo é JSON

    // 4. Envia a requisição POST com o payload JSON
    int httpResponseCode = http.POST(jsonPayload);

    // 5. Verifica a resposta do servidor
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("Código de resposta HTTP: ");
      Serial.println(httpResponseCode);
      Serial.print("Resposta do servidor: ");
      Serial.println(response);
    } else {
      Serial.print("Erro no envio. Código: ");
      Serial.println(httpResponseCode);
    }
    // 6. Libera os recursos
    http.end();

  } else {
    Serial.println("Erro: Wi-Fi não conectado. Não foi possível enviar os dados.");
  }
  contadorMovimento = 0;
}

void setup() {
  Serial.begin(115200);
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWi-Fi conectado!");
  Serial.print("Endereço IP: ");
  Serial.println(WiFi.localIP())
  pinMode(pirPin, INPUT);
  ledcSetup(ledChannel, ledFreq, ledResolution);
  ledcAttachPin(ledPin, ledChannel);
  analogReadResolution(12);
  gpsSerial.begin(9600);
  Serial.println("Sistema de Iluminação Autonoma Iniciado!");
}

void loop() {
  lerDadosGPS();
  int estadoPIR = digitalRead(pirPin);
  if (estadoPIR == HIGH) {
    if (!movimentoDetectado) {
      movimentoDetectado = true;
      contadorMovimento++;
      Serial.print("Movimento detectado! Contagem: ");
      Serial.println(contadorMovimento);

      // A contagem para o envio pode ser ajustada para testes
      if (contadorMovimento == 1) { 
        EnviarDados();
      }
    }
  } else {
    movimentoDetectado = false;
  }
  
  int valorLDR = analogRead(ldrPin);
  const int limiteEscuridao = 1000;
  
  if (movimentoDetectado && (valorLDR > limiteEscuridao)) {
    int valorBrilho = map(valorLDR, limiteEscuridao, 4095, 0, 255);
    setLedBrightness(valorBrilho);
  } else {
    setLedBrightness(0);
  }
  
  delay(500);
}