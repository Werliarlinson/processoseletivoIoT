import machine
import time
import struct

# Constantes 
LIMITE_TEMPO_X = 5000  # Tempo máximo de porta aberta (ms)
LIMITE_VARIACAO_Y = 3.0  # Máxima elevação térmica em Celsius

# Configuração dos Pinos
btn1 = machine.Pin(35, machine.Pin.IN)
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
MPU = 0x68

i2c.writeto_mem(MPU, 0x6B, b'\x00') # Inicializa o MPU6050
time.sleep_ms(100)

# Função para traduzir os bytes de temperatura do sensor para Celsius
def ler_temperatura():
    # Lê 2 bytes de temperatura do sensor e converte para Celsius
    temp_bytes = i2c.readfrom_mem(MPU, 0x41, 2)
    temp_raw = struct.unpack('>h', temp_bytes)[0]
    return (temp_raw / 340.0) + 36.53 # Fórmula de conversão do MPU6050 para Celsius

temp_ref = ler_temperatura()
print("Sistema de Monitoramento Inicializado")

# Variáveis Globais
tempo_abertura = 0
alarme_porta = False
alarme_temp = False

while True:
    estado_porta = btn1.value()
    temp_atual = ler_temperatura()    
    if temp_atual < temp_ref and not alarme_temp: # Se a estufa esfriar, o sistema assume esse novo valor seguro como base.
        temp_ref = temp_atual
    delta_t = temp_atual - temp_ref  # Variação térmica
    
    # Cenario B: Tempo de Porta Aberta
    if estado_porta == 0:  # Botão solto (0) indica porta aberta
        if tempo_abertura == 0:
            # Borda de descida detectada: guarda o exato momento em que abriu
            tempo_abertura = time.ticks_ms()
            if tempo_abertura == 0: 
                tempo_abertura = 1
        elif time.ticks_diff(time.ticks_ms(), tempo_abertura) >= LIMITE_TEMPO_X:
            # Verifica se o temporizador estourou
            if not alarme_porta:
                print("ALERTA: Porta aberta por muito tempo!")
                alarme_porta = True
    else:
        # Reseta o cronômetro para o próximo ciclo
        tempo_abertura = 0

    # Cenario C: Elevação Térmica e Degradação
    if delta_t >= LIMITE_VARIACAO_Y:
        if not alarme_temp:
            print("ALERTA: Degradacao termica detectada!")
            alarme_temp = True
            
    # O sistema só sai do estado de erro quando ambas as condições retornarem ao seguro
    if estado_porta == 1 and delta_t < LIMITE_VARIACAO_Y:
        if alarme_porta or alarme_temp:
            print("Status: Sistema Normalizado.")
            alarme_porta = False
            alarme_temp = False
            temp_ref = ler_temperatura()
    
    time.sleep_ms(50)