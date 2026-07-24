# Processo Seletivo – Intensivo Maker | IoT

## Identificação do Candidato

- **Nome completo:** Werliarlinson de Lima Sá Teles
- **GitHub:** https://github.com/Werliarlinson/processoseletivoIoT.git

---

## Visão Geral da Solução

O objetivo deste projeto é fornecer uma solução embarcada contínua para monitorar a integridade de ambientes refrigerados ou estufas. 

O sistema avalia constantemente duas condições: o tempo de exposição em que a porta do ambiente permanece aberta e variações abruptas de temperatura (gradiente térmico). A interação ocorre de forma passiva, onde o usuário (operador) abre ou fecha a porta, e o sistema emite relatórios de *status* e alarmes de degradação via comunicação Serial.

---

## Arquitetura do Sistema Embarcado

A arquitetura do firmware foi desenvolvida com foco em uma execução limpa e resposta imediata a interrupções lógicas, operando da seguinte forma:

* **Fluxo Principal:** O programa roda em um laço infinito (`while True`). Em cada ciclo, o sistema coleta o estado digital do botão e a leitura bruta via barramento I2C do sensor.
* **Controle de Tempo:** Em vez de utilizar funções bloqueantes, a temporização da porta e os atrasos de segurança (*debounce*) são calculados matematicamente pela diferença entre carimbos de tempo (`time.ticks_diff`), garantindo que o processador nunca pare de avaliar o ambiente.
* **Máquina de Estados:** O controle de alertas é gerenciado por *flags* booleanas (`alarme_porta`, `alarme_temp`), garantindo que os avisos sejam enviados apenas nas transições de estado, sem congestionar a saída Serial.

---

## Componentes Utilizados na Simulação

Os seguintes componentes foram integrados no ambiente virtual Wokwi (`diagram.json`):

- **Placa Controladora:** ESP32 DevKit C v4, responsável pelo processamento lógico em MicroPython.
- **Sensor de Temperatura (MPU6050):** Utilizado para leitura do sensor térmico embutido no chip MEMS via I2C. O Sensor de temperatura, assim como o acelerômetro e o giroscópio tem um conversor AD de 16 bits, e o MPU6050 possui um buffer FIFO de 1024 bytes portanto gerencia os dados de uma fila por vez. A faixa de temperatura de operação é -40 ºC a 85 ºC, se for analisar na prática essa analise é feita pelo chip não é da temperatura do ambiente, normamente é 2-5 ºC maior que a temperatura externa devido ao aquecimento natural do dispositivo.
- **Botão:** Simula o interruptor magnético/mecânico da porta. Foi configurado com um resistor de *pull-down* externo de 10kΩ para garantir nível lógico baixo (0) quando a porta é aberta.

---

## Decisões Técnicas Relevantes

- **Leitura da Temperatura Direta no Hardware:** Para manter o código enxuto e livre de dependências adicionais, a leitura da temperatura foi feita acessando diretamente os registradores `0x41` do MPU6050 via barramento, desempacotando os bytes nativamente.
- **Referência Térmica Dinâmica:** A temperatura base do sistema não é absoluta. O código atualiza dinamicamente a referência segura (`temp_ref`) caso o ambiente estabilize em uma temperatura mais baixa, prevenindo alarmes falsos e focando na elevação do gradiente.
- **Adaptação para Testes Automatizados (CI):** A lógica de normalização recebeu um atraso de estabilização estruturado para acomodar os tempos ocioso do script de validação, e o gatilho da porta passou a ser por leitura contínua de nível, eliminando condições de corrida durante o boot.

---

## Resultados Obtidos

O sistema final atingiu 100% de conformidade com as regras solicitadas:
- O cronômetro de 5 segundos de porta aberta funciona com precisão e reseta imediatamente ao fechamento.
- O alarme de degradação térmica dispara corretamente ao registrar um gradiente de +3.0°C a partir da base segura.
- A normalização do sistema exige ambas as grandezas estabilizadas.
- O código compilou perfeitamente em imagem Docker conteinerizada e foi aprovado com sucesso na esteira automatizada do GitHub Actions (Wokwi CI).

---

## Comentários Adicionais

- **Dificuldades:** A maior curva de aprendizado esteve na sincronização fina entre a velocidade de processamento do laço principal do ESP32 e a rigidez dos tempos injetados pelo robô de testes automatizados, exigindo adaptações na forma de lidar com a transição de estado da porta. Outro problema foi as instruções passadas pelo README do programa não serem claras como as chaves do Wokwi e a implementação no sistema GitHub, onde tem uma mudança nos nomes sugeridos nele e o aplicado pelo robô.
- **Aprendizados:** Esse processo reforçou a importância de criar um projeto e um código que seja tolerante não apenas ao ambiente físico, mas também às ferramentas de integração (como Docker e Git), garantindo que a infraestrutura seja tão testável no código como compátivel com as diversas API's que usa o sistema em conjunto.