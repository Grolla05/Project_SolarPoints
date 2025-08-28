// --- Configurações dos Pinos de Hardware & Variáveis Globais ---
const int pirPin = 2;       // Sinal do sensor PIR
const int ldrPin = 34;      // Sinal do sensor de luz (LDR)
const int ledPin = 18;      // Pino de controle do LED
int contadorMovimento = 0; 
bool movimentoDetectado = false; 

// --- Configurações do LED PWM no ESP32 ---
const int ledChannel = 0;
const int ledFreq = 5000;
const int ledResolution = 8;

// --- Função para controle de PWM no ESP32 ---
void setLedBrightness(int duty) {
  ledcWrite(ledChannel, duty);
}

void setup() {
  Serial.begin(115200);
  
  pinMode(pirPin, INPUT);
  
  // Configura os pinos PWM uma única vez no setup()
  ledcSetup(ledChannel, ledFreq, ledResolution);
  ledcAttachPin(ledPin, ledChannel);
  
  analogReadResolution(12);

  Serial.println("Sistema de Iluminação Autonoma (Versao Simplificada) Iniciado!");
}

void loop() {
  
  // Lê o estado do sensor PIR
  int estadoPIR = digitalRead(pirPin);
  
  // Apenas detecta novas detecções para o contador
  if (estadoPIR == HIGH) {
    if (!movimentoDetectado) {
      movimentoDetectado = true;
      contadorMovimento++;
      Serial.print("Movimento detectado! Contagem: ");
      Serial.println(contadorMovimento);
    }
  } else {
    movimentoDetectado = false;
  }
  
  // Lê o valor do LDR
  int valorLDR = analogRead(ldrPin);
  
  // Define o limite de escuridão
  const int limiteEscuridao = 1000;
  
  // Condições para acender a luz: Movimento E Escuridão
  if (movimentoDetectado && (valorLDR > limiteEscuridao)) {
    // Mapeia o LDR para o brilho do LED e liga o LED
    int valorBrilho = map(valorLDR, limiteEscuridao, 4095, 0, 255);
    setLedBrightness(valorBrilho);
    Serial.print("Movimento e escuridao detectados. Brilho do LED: ");
    Serial.println(valorBrilho);
  } else {
    // Apaga o LED
    setLedBrightness(0);
  }

  // Pequeno atraso para não sobrecarregar
  delay(500);
}