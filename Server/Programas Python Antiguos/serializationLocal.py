import os
import serial
import time
import datetime
import csv

ser = serial.Serial('/dev/cu.usbserial-4', 115200)
ser.flushInput()
counter = 0
lines=0
divPaquetes = 128  # Debe ser el mismo que en Main.ino del Client

samplingFrequency = 3000
samples = 2048

temporizador = time.perf_counter()
fechaYHora = datetime.datetime.now()

vFrec = []
vTime = []
for i in range(samples):
    vTime.append((i * 1.0) / samplingFrequency)
for i in range(int(samples / 2)):
    vFrec.append((i * 1.0 * samplingFrequency) / samples)

# if time.perf_counter() - temporizador > 8: #Si pasan mas de 8 segundos sin recibir transmision se reinicia el contador y la fecha
while True:
    try:
        ser_bytes = ser.readline()  # Lee la linea serial

        
        if time.perf_counter() - temporizador > 20: #Si pasan mas de 8 segundos sin recibir transmision se reinicia el contador y la fecha
            print("ENTREEE")
            with open("test_data {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "r") as f:   # Leemos cuantas lineas existen
                reader = csv.reader(f)
                linesDoc = len(list(reader))
                print(linesDoc)
            if linesDoc < 3072:
                file = "test_data {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute)
                if(os.path.exists(file) and os.path.isfile(file)):
                    os.remove(file)
                    print("file deleted")
                else: 
                    print("file not found")

            counter = 0
            fechaYHora = datetime.datetime.now()
            lines=0



        decoded_bytes = str(
            ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))  # decodifica
        decoded_bytes = decoded_bytes.split(" ")  # Divide cada que encuentra un espacio y lo envia a un arreglo
        print(decoded_bytes)
        


        with open("test_data {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "a") as f:  # Abre el archivo en modo append
            # Crea un objeto para escribir en csv
            writer = csv.writer(f, delimiter=",")
            for index in range(len(decoded_bytes)):
                try:
                    if counter < divPaquetes:
                        writer.writerow(
                            [vTime[index + lines], float(decoded_bytes[index])]) # Unicamente envia al archivo los numeros flotantes
                    else:
                        writer.writerow(
                            ["","",vFrec[index + lines - 2048], float(decoded_bytes[index+1])]) # Unicamente envia al archivo los numeros flotantes
                except:
                    pass  # Pasa los strings o cualquier otro dato
        with open("test_data {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "r") as f:   # Leemos cuantas lineas existen
            reader = csv.reader(f)
            linesn = len(list(reader))

        if linesn > lines:  # comparamos para saber si se escribio o solo fueron strings
            temporizador = time.perf_counter()
            counter = counter + 1  # Se incrementa contador
            lines = linesn
    except UnicodeDecodeError:
        print("Wrong Data")
        counter = counter + 1
    except:
        print("Bye Bye")
        break
