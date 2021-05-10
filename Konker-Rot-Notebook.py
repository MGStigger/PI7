# INICIO

import json
import time
import paho.mqtt.client as mqtt

mqtt_server = "mqtt.prod.konkerlabs.net"

# Em seguida, crie o topico no qual deseja que seu notebook publique.
topic_pub_value = "data/USUARIO/pub/button"

# A variavel last_message mantera a ultima vez que uma mensagem foi enviada.
# O message_interval eh o tempo entre cada mensagem enviada.
# Aqui, estamos configurando para 5 segundos
# (isso significa que uma nova mensagem sera enviada a cada 5 segundos).
last_message = 0
message_interval = 5

# A funcao connect_mqtt() cria um cliente MQTT e se conecta ao broker.
def connect_mqtt():
    try:
        client = mqtt.Client()
        client.username_pw_set("USUARIO", "SENHA")
        client.connect(mqtt_server, 1883)
        # print("")
        # print("Conectado ao broker MQTT mqtt.prod.konkerlabs.net")
        print("")
        return client
    except OSError as e:
        return("Dispositivo não conectado à Internet.")

def ligarLED():
    try:
        mensagem = json.dumps(
            {"deviceType": "notebook", "value": 1, "action": "ligar"})
        return mensagem
    except OSError as e:
        return("Falha no retorno da mensagem.")


def desligarLED():
    try:
        mensagem = json.dumps(
            {"deviceType": "notebook", "value": 0, "action": "desligar"})
        return mensagem
    except OSError as e:
        return("Falha no retorno da mensagem.")


client = connect_mqtt()

opcao = 0

while opcao != 3:
    try:
        if (time.time() - last_message) > message_interval:
            print('''
            [1] LIGAR LED
            [2] DESLIGAR LED
            [3] SAIR DO PROGRAMA
                                ''')

            opcao = int(input(">>>>>>>>>>> Qual é a sua opção? "))

            if opcao == 1:
                print("")
                mensagem = ligarLED()
                # Por fim, publique a mensagem usando o metodo publish()
                # no objeto client. O metodo publish() aceita como argumentos
                # o topico e a mensagem
                client.publish(topic_pub_value, mensagem)
                print("=-==-= LED Ligado =-==-=")
                print("")
                # Por fim, atualize a hora em que a ultima mensagem foi enviada
                last_message = time.time()

            elif opcao == 2:
                print("")
                mensagem = desligarLED()
                # Por fim, publique a mensagem usando o metodo publish()
                # no objeto client. O metodo publish() aceita como argumentos
                # o topico e a mensagem
                client.publish(topic_pub_value, mensagem)
                print("=-==-= LED Desligado =-==-=")
                print("")
                # Por fim, atualize a hora em que a ultima mensagem foi enviada
                last_message = time.time()

            elif opcao == 3:
                print("")
                print("Finalizando...")
                print("")

            else:
                print("")
                print("Opção inválida! Tente novamente.")
                print("")

            print("=-=" * 20)
    except OSError as e:
        print("Erro na execução do programa.")

time.sleep(2)
print("")
print("FIM DO PROGRAMA!")
print("")

# FIM
