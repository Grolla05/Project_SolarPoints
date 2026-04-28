# 💡 Project Solar Points — Smart Lighting for Low-Infrastructure Areas

> Light where there’s no infrastructure. Safety through simplicity and efficiency.

![Status](https://img.shields.io/badge/status-complete-green)

---

## 🌙 O que é o Solar Points?

O **Solar Points** é um sistema de iluminação pública autônomo e inteligente pensado para locais com pouca ou nenhuma infraestrutura elétrica, como:

- Paradas de ônibus
- Vielas e ruas estreitas
- Praças públicas
- Regiões periféricas e isoladas
- Áreas externas de residências

O objetivo permanece o mesmo: aumentar a segurança e o bem-estar comunitário com uma solução de baixo custo, sustentável e de fácil manutenção.

---

## 🔁 Evolução do projeto: de totalmente analógico para arquitetura digital

Inicialmente o projeto foi concebido como **100% analógico** (apenas componentes discretos e circuitos analógicos). Com as necessidades de sensoriamento mais preciso, flexibilidade operacional e otimização de consumo, o projeto evoluiu para uma **arquitetura digital/híbrida** baseada em microcontrolador e periféricos.

Essa mudança preserva os princípios de simplicidade, robustez e baixo consumo, ao mesmo tempo que agrega capacidades importantes:

- **Leitura digital de sensores** (intensidade de luz, distância/presença)
- **Decisões e temporizações programáveis** via firmware leve
- **Gerenciamento inteligente de energia** (controle de conversores DC-DC, modos de sono)
- **Comunicação entre módulos** via I2C/GPIO quando necessário

> A imagem anexada ao repositório ilustra o bloco funcional do novo design: microcontrolador central, sensores de luz e distância, gerenciamento de energia, baterias e conversores DC-DC.

---

## ⚙️ Principais funcionalidades (atualizado)

- **Ativação automática** baseada em sensores de luminosidade e presença
- **Modos ajustáveis** via firmware (p.ex. sensibilidades, temporização)
- **Operação autônoma** com painéis solares e baterias
- **Gestão adequada de energia** com conversores DC-DC e técnicas de baixo consumo
- **Projeto modular e replicável** com possibilidade de atualização de firmware

---

## 🛠️ Tecnologias e componentes (atualizado)

- **Microcontrolador** (unidade central de controle) — responsável por leitura de sensores e lógica de acionamento
- **Sensor de luminosidade** (LDR/photodiode + ADC) — medida de intensidade luminosa
- **Sensor de distância/presença** (ultrassom/IR) — detectar passagem ou presença
- **Conversores DC-DC** (step-up/step-down) — fornecimento estável para LEDs e eletrônica
- **Gestão de energia / Power Management** (monitoramento de bateria, carregamento solar)
- **Bateria recarregável e painéis solares**
- **LEDs de potência** para iluminação pública
- **Interfaces**: GPIOs para sinalização/controle, I2C para sensores/power ICs quando aplicável

---

## 🔍 Diagrama funcional

O diagrama no repositório mostra os blocos principais interconectados:

- 1 — Baterias (alimentação)
- 4 — Power Management (monitoramento/carregador)
- 11 — Conversão DC-DC (alimentação dos LEDs e eletrônica)
- 2 — Microcontrolador (núcleo lógico)
- 5 — Medição de intensidade luminosa (sensor)
- 6 — Sensor de distância/presença
- 3 — LED de status / power

O microcontrolador realiza a lógica central: lê sensores (GPIOs/ADC/I2C), decide quando ligar os LEDs e controla os conversores para otimizar consumo.

---

## ✨ Aplicações no mundo real

O Solar Points continua ideal para iluminar pontos sem infraestrutura elétrica: pontos de ônibus, caminhos em áreas rurais, entradas de condomínios e outras localidades onde uma solução autônoma e resiliente faz diferença.

---

## 👥 Autores

Desenvolvido por:

- **Felipe Grolla Freitas** – Engenharia de Controle e Automação (PUC-Campinas)
- **Guilherme Oliveira Nogueira** – Engenharia de Controle e Automação (PUC-Campinas)
- **Giovanna Lima Salvagnini** – Engenharia de Controle e Automação (PUC-Campinas)
- **Henrique Spadaccia Chambó** – Engenharia de Controle e Automação (PUC-Campinas)

---

> 🧠 "A simplicidade, aliada a decisões digitais pontuais, amplia o impacto das soluções de engenharia em contextos reais."
