# INICIO

# Importe o modulo machine para interagir com os GPIOs
# e o modulo time para adicionar atrasos.
import json
import ujson
import esp
import network
import micropython
from umqttsimple import MQTTClient
from machine import Pin
import machine
import time
import ubinascii
import onewire
# Para placas baseadas em ESP8266, antes de usar uma ferramenta como o ampy, por exemplo,
# voce pode precisar desativar a saida de depuracao na placa.
esp.osdebug(None)

ssid = "NOME-DA-REDE-WIFI"
password = "SENHA-DA-REDE-WIFI"
mqtt_server = "mqtt.prod.konkerlabs.net"

# Para criar um cliente MQTT, precisamos obter o ID exclusivo do ESP.
# Isso eh o que fazemos na linha a seguir (eh salvo na variavel client_id).
client_id = ubinascii.hexlify(machine.unique_id())

# Em seguida, crie o topico no qual deseja que seu ESP subscreva.
topic_sub_led = "data/USUARIO/sub/led"

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

# Cria uma variavel chamada led que se refere ao GPIO 02,
# o pino ao qual o led esta conectado. Determina o pino como saida.
led = Pin(2, Pin.OUT, value = 0)

def sub_cb(topic, msg):
    print(msg)

# A funcao connect_mqtt() cria um cliente MQTT e se conecta ao broker.
def connect_mqtt():
    global client_id, mqtt_server
    print("Cliente ID: %s" % (client_id))
    #client = MQTTClient(client_id, mqtt_server)
    client = MQTTClient(client_id, mqtt_server, 1883,
                        user="USUARIO", password="SENHA")
    # Esta funcao sera chamada quando uma mensagem for recebida.
    client.set_callback(sub_cb)
    client.connect()
    print("Conectado ao broker MQTT %s" % (mqtt_server))
    client.subscribe(topic_sub_led)
    return client

# A funcao restart_and_reconnect() redefine a placa ESP32.
# Esta funcao sera chamada se nao conseguirmos subscrever as leituras via MQTT
# no caso de o broker se desconectar.
def restart_and_reconnect():
    print("Falha ao conectar ao broker MQTT. Reconectando...")
    time.sleep(10)
    machine.reset()

def read_led():
    try:
        #json_string = client.wait_msg()
        json_string = client.check_msg()
        #print(json_string)
        parsed_json = json.loads(json_string)
        led = parsed_json["value"]
        print(led)
        if (isinstance(led, int)):
            mensagem = led
            return mensagem
        else:
            return("Leituras invalidas.")
    except OSError as e:
        return("Falha ao ler o valor.")


try:
    client = connect_mqtt()
except OSError as e:
    restart_and_reconnect()

while True:
    try:
        mensagem = read_led()

        if mensagem == 0:
            led.value(0)

        elif mensagem == 1:
            led.value(1)

    except OSError as e:
        restart_and_reconnect()

# FIM