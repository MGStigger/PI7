# Referencias:
# https://randomnerdtutorials.com/micropython-ds18b20-esp32-esp8266/
# https://techtutorialsx.com/2017/05/27/esp32-micropython-encoding-json/
# https://randomnerdtutorials.com/micropython-mqtt-publish-ds18b10-esp32-esp8266/

# Importe o modulo machine para interagir com os GPIOs,
# os modulos onewire e ds18x20 para interagir com o sensor de temperatura DS18B20
# e o modulo time para adicionar atrasos.
import time
import machine
from machine import Pin
import onewire
import ds18x20
# O modulo gc eh um mecanismo de gerencia de memoria automatico que eh responsavel
# por alocar memoria para seus objetos e desaloca-la quando esses objetos
# nao possuem mais referencia para eles.
import gc
from umqttsimple import MQTTClient
# O modulo ubinascii implementa conversoes entre dados binarios e varias codificacoes deles
# em formato ASCII (em ambas as direcoes).
import ubinascii
import micropython
import ujson
import json
import network
import esp
# Para placas baseadas em ESP8266, antes de usar uma ferramenta como o ampy, por exemplo,
# voce pode precisar desativar a saida de depuracao na placa.
esp.osdebug(None)
gc.collect()

ssid = "NOME-DA-SUA-REDE-WI-FI"
password = "SENHA-DA-SUA-REDE-WI-FI"
mqtt_server = "mqtt.prod.konkerlabs.net"

# Para criar um cliente MQTT, precisamos obter o ID exclusivo do ESP.
# Isso eh o que fazemos na linha a seguir (eh salvo na variavel client_id).
client_id = ubinascii.hexlify(machine.unique_id())

# Em seguida, crie o topico no qual deseja que seu ESP publique.
topic_pub_temp = "data/USUARIO/pub/temperature"

# A variavel last_message mantera a ultima vez que uma mensagem foi enviada.
# O message_interval eh o tempo entre cada mensagem enviada.
# Aqui, estamos configurando para 5 segundos
# (isso significa que uma nova mensagem sera enviada a cada 5 segundos).
last_message = 0
message_interval = 5

# Depois disso, conecta a ESP a sua rede local.
# Podemos configurar o modulo para se conectar a sua propria rede usando a interface STA_IF.
station = network.WLAN(network.STA_IF)
# Ativa a interface da estacao.
station.active(True)
station.connect(ssid, password)

# Verifica se a conexao foi estabelecida.
# A instrucao pass permite lidar com a condicao sem que o loop seja impactado.
# Todo o codigo continuara sendo lido a menos que um break ou outra instrucao ocorra.
while station.isconnected() == False:
    pass

print("Conexao bem sucedida")

# Cria uma variavel chamada ds_pin que se refere ao GPIO 4,
# o pino ao qual o fio de dados do sensor de temperatura DS18B20 esta conectado.
ds_pin = machine.Pin(4)

# Cria um objeto ds18x20 chamado ds_sensor no ds_pin definido anteriormente.
# O barramento de 1 fio eh um barramento serial que usa apenas um unico fio
# para comunicacao (alem de fios para aterramento e alimentacao).
# O sensor de temperatura DS18B20 eh um dispositivo de 1 fio muito popular,
# e aqui mostramos como usar o modulo onewire para ler de tal dispositivo.
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))

# A funcao connect_mqtt() cria um cliente MQTT e se conecta ao broker.
def connect_mqtt():
    global client_id, mqtt_server
    print("Cliente ID: %s" % (client_id))
    #client = MQTTClient(client_id, mqtt_server)
    client = MQTTClient(client_id, mqtt_server, 1883,
                        user="USUARIO", password="SENHA")
    client.connect()
    print("Conectado ao broker MQTT %s" % (mqtt_server))
    return client

# A funcao restart_and_reconnect() redefine a placa ESP32.
# Esta funcao sera chamada se nao conseguirmos publicar as leituras via MQTT
# no caso de o broker se desconectar.
def restart_and_reconnect():
    print("Falha ao conectar ao broker MQTT. Reconectando...")
    time.sleep(10)
    machine.reset()

# Criamos uma funcao chamada read_sensor()
# que retorna a temperatura atual do sensor DS18B20
# e lida com quaisquer excecoes, caso nao possamos obter as leituras do sensor.
def read_sensor():
    try:
        # A linha a seguir usa a funcao scan() para procurar sensores DS18B20.
        # Os enderecos encontrados sao salvos na variavel roms
        # (a variavel roms eh do tipo lista).
        roms = ds_sensor.scan()
        # Imprime o endereco de cada sensor
        print("Sensores DS encontrados: ", roms)
        # Eh preciso acionar a funcao convert_temp() no objeto ds_sensor
        # cada vez que voce deseja obter uma amostra de temperatura.
        ds_sensor.convert_temp()
        # Adiciona um atraso para dar tempo suficiente para converter a temperatura
        time.sleep_ms(750)
        for rom in roms:
            print("Endereco do DS: %s" % (rom))
            deviceAddress = ("%s" % rom)
            # Depois disso, podemos ler a temperatura nos enderecos
            # encontrados anteriormente usando o metodo read_temp()
            # e passando o endereco como argumento
            # uncomment for Fahrenheit
            # temp = temp * (9/5) + 32.0
            # temp = ds_sensor.read_temp(rom)
            temp = round(ds_sensor.read_temp(rom), 1)
            mensagem = json.dumps(
                {"deviceType": "temperature", "deviceAddress": deviceAddress, "value": temp, "unit": "celsius"})
            # A funcao isinstance() verifica se o objeto (primeiro argumento) eh uma instancia
            # ou subclasse da classe classinfo (segundo argumento).
            if (isinstance(temp, float) or (isinstance(temp, int))):
                temp = mensagem
                return temp
            else:
                return("Leituras de sensor invalidas.")
    except OSError as e:
        return("Falha ao ler o sensor.")

try:
    client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        # Primeiro, verifique se eh hora de obter novas leituras
        # Em caso afirmativo, solicite uma nova leitura de temperatura
        # do sensor DS18B20 chamando a funcao read_sensor().
        # A temperatura eh salva na variavel temp.
        if (time.time() - last_message) > message_interval:
            temp = read_sensor()
            print(temp)
            # Por fim, publique a temperatura usando o metodo publish()
            # no objeto client. O metodo publish() aceita como argumentos
            # o topico e a mensagem
            client.publish(topic_pub_temp, temp)
            # Por fim, atualize a hora em que a ultima mensagem foi enviada
            last_message = time.time()
    # Caso a ESP32 se desconecte do broker e nao possamos publicar as leituras,
    # acione a funcao restart_and_reconnect() para redefinir a placa ESP
    # e tentar reconectar ao broker.
    except OSError as e:
        restart_and_reconnect()
