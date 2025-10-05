import smbus 
import time
from datetime import datetime

# Endereço I2C do BH1750
BH1750_ADDR = 0x37  
I2C_BUS = 1 

# Comando para modo contínuo de alta resolução
CONT_H_RES_MODE = 0x10 

# Caminho do arquivo de log no microSD
CAMINHO_ARQUIVO = "/media/caninos/8053-D444/luminus/lux_log.txt"
DADOS_CAMINHO = "  "

try:
    bus = smbus.SMBus(I2C_BUS)
except FileNotFoundError:
    print(f"Erro: Não foi possível abrir o barramento I2C {I2C_BUS}. Verifique se ele existe.")
   
    bus = None


def classificar_luminosidade(lux):
    """Classifica o nível de luz em categorias."""
    if lux is None:
        return "INDEFINIDO"
    elif lux < 5:
        return "ESCURO"
    elif lux < 50:
        return "LUZ FRACA"
    elif lux < 500:
        return "LUZ NORMAL"
    elif lux < 15000:
        return "LUZ FORTE"
    else:
        return "LUZ MUITO FORTE"

def ler_lux():
    # Verifica se o barramento foi inicializado com sucesso
    if bus is None:
        return None#se o barramento não foi inicializado, retorna None
        
    try:
        bus.write_byte(BH1750_ADDR, CONT_H_RES_MODE)#inicia a medição com o comando CONT_H_RES_MODE que é 0x10 e o endereço do sensor que é BH1750_ADDR, ou seja, 0x23
        time.sleep(0.2)
        data = bus.read_i2c_block_data(BH1750_ADDR, 0x00, 2)#lê 2 bytes de dados do sensor pois a luminosidade é representada por 2 bytes
        raw = (data[0] << 8) | data[1] #combina os 2 bytes em um valor bruto, precisamos fazer um shift do primeiro byte 8 bits para a esquerda e fazer um OR com o segundo byte

        lux = raw / 1.2 #converte o valor bruto para lux, dividindo por 1.2 conforme o datasheet do BH1750
        return lux
    except Exception as e:#se ocorrer algum erro na leitura do sensor
        print(f"Erro ao ler BH1750 no barramento {I2C_BUS}:", e)
        return None

if __name__ == "__main__":#se o script for executado diretamente ou seja, não for importado como módulo, esse __name__ é uma variável especial que contém o nome do módulo atual
    print("Iniciando leitura e salvamento de luminosidade em .txt...")

    try:
        while True:
            lux = ler_lux()
            
            
            status_luz = classificar_luminosidade(lux)
            
            if lux is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
          
                linha = f"[{timestamp}] Luminosidade: {lux:.2f} lux | Status: {status_luz}\n"
                print(f"[{timestamp}] Luminosidade: {lux:.2f} lux | Status: {status_luz}")
                
                # Salva no arquivo .txt
                try:
                    with open(DADOS_CAMINHO, "a") as f:
                        f.write(linha)
                except Exception as e:
                    print(f"Erro ao escrever no arquivo {DADOS_CAMINHO}:", e)

            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
              
                
                linha_erro = f"[{timestamp}] Erro na leitura do sensor.\n"
                print(f"[{timestamp}] Erro na leitura do sensor.")
                
                # Salva a linha de erro no arquivo também
                try:
                    with open(DADOS_CAMINHO, "a") as f:
                        f.write(linha_erro)
                except Exception as e:
                    # Se não conseguir ler nem escrever, apenas imprime
                    print(f"Erro ao escrever no arquivo {DADOS_CAMINHO}:", e)


            time.sleep(2)

    except KeyboardInterrupt:

        print("\nFinalizado.")