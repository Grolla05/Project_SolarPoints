# Documentação de Hardware - Projeto de Iluminação Autônoma Solar

## Visão Geral do Projeto

Este projeto consiste em um sistema de iluminação autônoma e inteligente, projetado para operar com energia solar. Ele carrega uma bateria interna e acende uma lâmpada LED ao detectar movimento, mas apenas quando a luz ambiente estiver baixa. A arquitetura de hardware é dividida em blocos funcionais para garantir eficiência, segurança e robustez.

-----

## 1. Arquitetura do Circuito

O circuito é centrado em um chip de **Gerenciamento de Energia** (Power Management) que controla o fluxo entre as fontes de energia, a bateria e o sistema lógico. A principal característica do design é a separação entre o **circuito de controle de baixa tensão (5V)** e o **circuito de potência de alta tensão (12V)**, isolados por um Módulo Relé.

### Diagrama de Blocos do Circuito Completo

```
+------------------------------------------------------------------------------------------------------------------------------+
|                            Gerenciamento de Energia (Ex: BQ25881)                                                            |
|                                                                                                                              |
|   Entrada 12V (Vin) do Painel Solar        Saída ~12V (SYS) para o Sistema                                                   |
|              ▼                                            ▼                                                                  |
|       +------+--------------------------------------------+------------------------------------------------------------------+
|       |      |                                            |                                                                  |
|       |      | Carrega/Descarrega (BAT)                     |                                                                |
|       |      |                                            |                                                                  |
|       ▼      ▼                                            ▼                                                                  |
|  +----------+----------+                        +-------------------------+                                                  |
|  |  Bateria 12V + BMS  |                        | Conversor DC-DC (5V)    |                                                  |
|  +---------------------+                        +-----------+-------------+                                                  |
|          ^                                                  |                                                                |
|          |                                                  | (Alimentação Lógica 5V e GND)                                  |
|          +--------------------------------------------------+-------------------------------+                                |
|                                                             |                               |                                |
|  (Circuito de Controle - 5V)                                ▼                               |                                |
|                                                  +--------------------+                     |                                |
|                     +----------------------------+  Microcontrolador  |                     |                                |
|                     |                            |      (ESP32)       |                     |                                |
|                     |                            +--+------+-------+--+                     |                                |
|                     |                               |      |       |                        |                                |
|                 Módulo GPS               (Sinal IN) |      |       | (Sinal OUT)            |                                |
|                                                     ▼      ▼       ▼                        |                                |
|                                                +----------+-+-+----------+       +-------------------+                       |
|                                                | Sensor PIR | |Sensor LDR|       | Módulo Relé 5V    |                       |
|                                                +------------+ +----------+       |                   |                       |
|                                                                                  | VCC | GND | IN    |                       |
|                                                                                  +--+----+-----------+                       |
|                                                                                  |  |    |                                   |
|                                                                                  |  |    |                                   |
| (Circuito de Potência - 12V, chaveado pelo Relé)                                 |  |    | (do pino GPIO)                    |
|                                                                                  |  |    |                                   |
|   +---------------------+                                                        |  +----+ (do GND)                          |
|   | Fonte de Energia    |                                                        +-------+ (do 5V)                           |
|   | (Bateria/SYS ~12V)  |                                                                |                                   |
|   +----------+----------+                                                                |                                   |
|              | (+)                                                                       |                                   |
|              |                                                                           |                                   |
|              +---------------------------------------------------------------------------+ (Terminal COM)                    |
|                                                                                             (Terminal NO)                    |
|                                                                                                   |                          |
|                                                                                                   | (+)                      |
|                                                                                                   ▼                          |
|                                                                                            +---------------+                 |
|                                                                                            | Lâmpada LED   |                 |
|                                                                                            |     12V       |                 |
|                                                                                            +-------+-------+                 |
|                                                                                                    | (-)                     |
|                                                                                                    ▼                         |
|                                                                                             (GND da Fonte 12V)               |
|                                                                                                                              |
+------------------------------------------------------------------------------------------------------------------------------+
```

-----

## 2. Seleção de Componentes e Justificativa

A escolha de cada componente foi pensada para garantir segurança, eficiência e funcionalidade.

* **Painel Solar (12V):** Fonte de energia primária. Sua tensão de 12V é ideal para carregar diretamente a bateria de 12V e alimentar o circuito lógico.
* **Bateria de Lítio (12V 3S):** Fornece energia para o sistema durante a noite. Uma bateria de 3 células em série (3S) tem tensão nominal de 11.1V, compatível com a fonte solar.
* **Módulo BMS (Battery Management System):** **Componente crítico para a segurança**. O BMS protege a bateria contra sobrecarga, sobredescarga e curtos-circuitos, além de realizar o balanceamento de células, prolongando a vida útil do pacote de baterias.
* **Chip de Gerenciamento de Energia (Ex: BQ25881):** O cérebro do sistema de energia. Este chip implementa a funcionalidade de ***power path***, direcionando a energia da fonte solar para a carga e, em seguida, para a bateria, de forma automática e eficiente.
* **Conversor DC-DC (Step-down):** Essencial para a eficiência. Ele recebe a tensão variável da saída do gerenciador de energia e a converte para uma tensão estável de 5V, ideal para o microcontrolador e os sensores. A alta eficiência minimiza a perda de energia em forma de calor.
* **Microcontrolador (ESP32):** O controlador lógico. O ESP32 foi escolhido por sua versatilidade, baixo consumo de energia e capacidade de processar dados dos sensores.
* **Sensor PIR (Infravermelho Passivo):** Sensor de movimento. Envia um sinal digital `HIGH` para o ESP32 quando detecta presença, ativando a rotina de acionamento da luz.
* **Sensor de Luz (LDR):** Sensor de luminosidade. Através de um divisor de tensão, ele fornece um sinal analógico ao ESP32, permitindo que o sistema determine se a luz ambiente é suficiente para ligar a lâmpada.
* **Módulo Relé 5V com Optoacoplador:** Atua como um interruptor eletrônico seguro. Permite que o ESP32, com um sinal de baixa potência (5V), controle uma carga de alta potência (a lâmpada de 12V). O **optoacoplador** é fundamental, pois isola eletricamente o microcontrolador do circuito de potência, protegendo-o de ruídos e picos de tensão gerados pelo acionamento do relé.

-----

## 3. Fluxo de Operação do Circuito

O sistema opera em um ciclo contínuo, com a energia e a lógica seguindo um fluxo bem definido:

1. **Gerenciamento de Energia:** A energia do painel solar entra no chip de gerenciamento (`Vin`), que a direciona para a saída `SYS` (para alimentar o sistema) e para a porta `BAT` (para carregar a bateria via BMS).

2. **Alimentação Lógica:** O conversor DC-DC recebe a energia da saída `SYS` e a regula para 5V, alimentando o **ESP32**, os sensores e o Módulo Relé de forma estável.

3. **Lógica Condicional:** O **ESP32** continuamente lê a saída dos dois sensores:
    * O sinal **digital** do **sensor PIR** (HIGH se houver movimento).
    * O sinal **analógico** do **sensor de luz**.

4. **Acionamento da Lâmpada:** O **ESP32** só envia um sinal de ativação para o Módulo Relé se **ambas** as condições forem verdadeiras:
    * `(1)` **Há movimento detectado** (sinal PIR = HIGH).
    * `(2)` **A luz ambiente é insuficiente** (o valor analógico do sensor de luz está acima de um limite programado).

5. **Controle via Relé:** Se as condições forem atendidas, o **ESP32** envia um sinal digital `HIGH` para o Módulo Relé. O relé então atua como um interruptor, fechando o circuito de 12V e acendendo a Lâmpada LED em sua potência máxima. Quando as condições não são mais atendidas, um sinal `LOW` é enviado, abrindo o circuito e desligando a lâmpada.

-----

## 4\. Lista de Materiais

* Painel Solar 12V
* Bateria de Lítio (3S, 12V)
* <a href="https://www.handsontec.com/dataspecs/module/3S-10A-18650-Charger.pdf">Módulo BMS 3S</a>
* <a href="https://www.ti.com/lit/ug/sluuc12/sluuc12.pdf?ts=1757377702366">Chip de Gerenciamento de Bateria com ***Power Path*** (ex: BQ25881)</a>
* Conversor DC-DC Step-down (para 5V)
* <a href="https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf">**Microcontrolador ESP32**</a>
* <a href="https://www.handsontec.com/dataspecs/SR501%20Motion%20Sensor.pdf">Sensor de Movimento PIR (HC-SR501)</a>
* <a href="https://components101.com/sites/default/files/component_datasheet/LDR%20Datasheet.pdf">Sensor de Luz (LDR)</a>
* <a href="https://www.eletruscomp.com.br/arquivos/1488539846_dados_tecnicos_p9___gbk_rele_10a_simples.pdf">Relay</a>
* Lampada LED
* Resistores: 10kΩ, 1kΩ e 220Ω (ou 330Ω)

-----

## 5\. Esquemas e Layouts do Projeto

Esta seção é dedicada à documentação visual do projeto, fundamental para a construção e replicação.

### Diagrama Esquemático

* [Insira aqui a imagem do seu diagrama esquemático, mostrando as conexões de todos os componentes.]

### Layout da Placa de Circuito Impresso (PCB)

* [Insira aqui a imagem do layout da sua PCB, com as trilhas, componentes e silkscreen.]

### Imagens do Protótipo ou Produto Final

* [Insira aqui as fotos do seu projeto montado na protoboard ou na PCB final.]

-----

## 6\. Desenvolvedores do Projeto

**Felipe Grolla Freitas** – Engenharia de Controle e Automação (PUC-Campinas)<br>
**Guilherme Oliveira Nogueira** – Engenharia de Controle e Automação (PUC-Campinas)<br>
**Giovanna Lima Salvagnini** – Engenharia de Controle e Automação (PUC-Campinas)<br>
**Henrique Spadaccia Chambó** – Engenharia de Controle e Automação (PUC-Campinas)
