import requests
import json
import psycopg2
import pandas as pd
import time
from datetime import datetime
from pytz import timezone

last_message = 0
message_interval = 300

while True:
    try:
        if (time.time() - last_message) > message_interval:

            conn = psycopg2.connect(
                host="localhost", database="database", user="user", password="password")
            cur = conn.cursor()

            request = requests.get(
                "https://api.hgbrasil.com/weather?woeid=456524&fields=only_results,temp,city,humidity,wind_speedy&key=KEY")
            dados = json.loads(request.content)
            print("")
            print(dados)
            print("")

            temperatura = dados['temp']
            umidade = dados['humidity']
            vento = dados['wind_speedy']

            velocidadeVento = ""
            for caractere in vento:
                if(caractere.isdigit() or caractere == "."):
                    velocidadeVento = velocidadeVento + caractere

            print(temperatura)
            print(umidade)
            print(velocidadeVento)
            print("")

            data_e_hora_atuais = datetime.now()
            fuso_horario = timezone('America/Sao_Paulo')
            data_e_hora_sao_paulo = data_e_hora_atuais.astimezone(fuso_horario)
            data_e_hora = data_e_hora_sao_paulo.strftime('%Y-%m-%d %H:%M:%S')
            print(data_e_hora)

            sql = """INSERT INTO matheus (sensor_id, sensor_name, sensor_value, pub_date) VALUES (%s, %s, %s, %s)"""
            cur.execute(sql, (111, "TEMPERATURA", temperatura, data_e_hora))
            cur.execute(sql, (222, "UMIDADE", umidade, data_e_hora))
            cur.execute(sql, (333, "VENTO", velocidadeVento, data_e_hora))

            conn.commit()

            table = pd.read_sql_query(
                """SELECT * FROM public.matheus WHERE sensor_name = 'TEMPERATURA' ORDER BY pub_date DESC LIMIT 9""", con=conn)
            print("")
            print(table)
            print("")
            datahora = table['pub_date']
            tempValue = table['sensor_value']

            datahora8 = """ " """ + str(datahora[8]) + """ " """
            datahora7 = """ " """ + str(datahora[7]) + """ " """
            datahora6 = """ " """ + str(datahora[6]) + """ " """
            datahora5 = """ " """ + str(datahora[5]) + """ " """
            datahora4 = """ " """ + str(datahora[4]) + """ " """
            datahora3 = """ " """ + str(datahora[3]) + """ " """
            datahora2 = """ " """ + str(datahora[2]) + """ " """
            datahora1 = """ " """ + str(datahora[1]) + """ " """
            datahora0 = """ " """ + str(datahora[0]) + """ " """

            tempValue8 = tempValue[8]
            tempValue7 = tempValue[7]
            tempValue6 = tempValue[6]
            tempValue5 = tempValue[5]
            tempValue4 = tempValue[4]
            tempValue3 = tempValue[3]
            tempValue2 = tempValue[2]
            tempValue1 = tempValue[1]
            tempValue0 = tempValue[0]

            arquivo = open("/var/www/html/matheus.html", "w")
            arquivo.close()
            arquivo = open("/var/www/html/matheus.html", "a")

            linha_arq = "<!DOCTYPE html>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "<html>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "<head>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <title>Meteorologia SLS</title>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <meta http-equiv = 'refresh' content = '60'>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <script src = 'https://cdn.plot.ly/plotly-latest.min.js'></script>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "</head>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "<body>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <h2>Temperatura (Celsius)</h2>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <div id = 'grafico' style = 'width: 800px;'></div>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   <script>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "       var graf1 = {" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "           x: [" + str(datahora8) + ", " + str(datahora7) + ", " + str(datahora6) + ", " + str(datahora5) + ", " + str(
                datahora4) + ", " + str(datahora3) + ", " + str(datahora2) + ", " + str(datahora1) + ", " + str(datahora0) + "]," + "\n"
            arquivo.write(linha_arq)
            linha_arq = "           y: [" + str(tempValue8) + ", " + str(tempValue7) + ", " + str(tempValue6) + ", " + str(tempValue5) + ", " + str(
                tempValue4) + ", " + str(tempValue3) + ", " + str(tempValue2) + ", " + str(tempValue1) + ", " + str(tempValue0) + "]," + "\n"
            arquivo.write(linha_arq)
            linha_arq = "           mode: 'lines+markers'," + "\n"
            arquivo.write(linha_arq)
            linha_arq = "           type: 'scatter'," + "\n"
            arquivo.write(linha_arq)
            linha_arq = "       };" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "       var data = [graf1];" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "       Plotly.newPlot('grafico', data);" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "   </script>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "</body>" + "\n"
            arquivo.write(linha_arq)
            linha_arq = "</html>"
            arquivo.write(linha_arq)

            arquivo.close()
            cur.close()
            conn.close()

            last_message = time.time()

    except Exception:

        print("=-=-=-=-=-=-=-=-=-= ERROR =-=-=-=-=-=-=-=-=-=")
