/**
 * @file ESP32_Controle_Final.cpp
 * @brief Código de controle para sistema de iluminação autônoma com ESP32.
 * * Este programa lê um sensor de movimento (PIR) e um sensor de luz (LDR).
 * Se o movimento for detectado E o ambiente estiver escuro, ele aciona
 * um Módulo Relé para ligar uma lâmpada de 12V.
 * * Conexões de Hardware:
 * - Sensor PIR   -> GPIO 2
 * - Sensor LDR   -> GPIO 34
 * - Módulo Relé  -> GPIO 19
 */

// --- MAPEAMENTO DOS PINOS DE HARDWARE E VARIÁVEIS GLOBAIS E DE CONTROLE ---
const int pinoPIR = 2;                                                                  // Pino de sinal do sensor de movimento (PIR)
const int pinoLDR = 34;                                                                 // Pino de sinal do sensor de luz (LDR) - Deve ser um pino ADC
const int pinoRele = 19;                                                                // Pino que envia o sinal de controle para o Módulo Relé
bool movimentoDetectado = false;                                                        // "Trava" para garantir que o contador de movimento incremente apenas uma vez por evento
bool releEstaLigado = false;                                                            // Flag para otimizar a impressão no Monitor Serial, mostrando o estado apenas quando ele muda
int contadorMovimento = 0;                                                              // Contador para registrar o número de vezes que o movimento foi detectado


//================================================================================
// FUNÇÃO SETUP: Executada uma única vez quando o ESP32 é ligado
//================================================================================
void setup() {
  Serial.begin(115200);                                                                 // 1. Inicia a comunicação serial para permitir o envio de mensagens de status (debug)
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
    }
  } else {
    movimentoDetectado = false;                                                         // Libera a "trava" quando não há mais movimento
  }
  
  int valorLDR = analogRead(pinoLDR);                                                   // ETAPA 3: Ler o valor do sensor de luz (LDR)
  const int limiteEscuridao = 1500;                                                     // ETAPA 4: Definir o limite de escuridão, este valor é o ponto de corte. Leituras do LDR *ACIMA* dele são consideradas "escuras".
  
  if (movimentoDetectado && (valorLDR > limiteEscuridao)) {                             // ETAPA 5: Lógica principal de decisão. A lâmpada só será ligada se AMBAS as condições forem verdadeiras.
    digitalWrite(pinoRele, HIGH);                                                       // Liga a lâmpada enviando um sinal ALTO para o relé
    if (!releEstaLigado) {                                                              // Imprime a mensagem de status apenas na primeira vez que o estado muda
      Serial.println("STATUS: Condicoes atendidas -> Rele ACIONADO (Lampada LIGADA)");
      releEstaLigado = true;
    }

  } else {
    digitalWrite(pinoRele, LOW);                                                        // Desliga a lâmpada enviando um sinal BAIXO para o relé
    if (releEstaLigado) {                                                               // Imprime a mensagem de status apenas na primeira vez que o estado muda
      Serial.println("STATUS: Condicoes nao atendidas -> Rele DESLIGADO (Lampada APAGADA)");
      releEstaLigado = false;
    }
  }
  delay(250);                                                                           // Pequena pausa para estabilidade do loop
}
