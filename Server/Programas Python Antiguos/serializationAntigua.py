import serial
import time
import csv

ser = serial.Serial('/dev/cu.usbserial-0001', 115200)
ser.flushInput()
counter = 0
divPaquetes = 128  # Debe ser el mismo que en Main.cpp del Client
temporizador = time.perf_counter()


with open("test_data.csv", "a") as f:  # Crea archivo o lo abre
    pass
with open("test_data.csv", "r") as f:  # Lee cuantas lineas tiene el archivo csv
    reader = csv.reader(f)
    lines = len(list(reader))

while True:
    try:
        ser_bytes = ser.readline()  # Lee la linea serial
        # print(ser_bytes)
        decoded_bytes = str(
            ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))  # decodifica
        # Divide cada que encuentra un espacio y lo envia a un arreglo
        decoded_bytes = decoded_bytes.split(" ")

        print(decoded_bytes)

        if time.perf_counter() - temporizador > 8:
            counter = 0

        with open("test_data.csv", "a") as f:  # Abre el archivo en modo append
            # Crea un objeto para escribir en csv
            writer = csv.writer(f, delimiter=",")
            for index in range(len(decoded_bytes)):
                try:
                    if counter < divPaquetes:
                        # Unicamente envia al archivo los numeros flotantes
                        if(index % 2) == 0:
                            writer.writerow(
                                [float(decoded_bytes[index]), float(decoded_bytes[index+1])])
                    # elif counter < (divPaquetes*2):
                    #     if (index % 2) == 0:
                    #         writer.writerow(
                    #             [time.time(), None, None, float(decoded_bytes[index]), float(decoded_bytes[index+1])])
                    # else:
                        # if (index % 2) == 0:
                        #     if decoded_bytes[index+1] != "":
                        #         writer.writerow([time.time(), None, None, None, None, float(decoded_bytes[index]), float(
                        #             decoded_bytes[index + 1])])  # Unicamente envia al archivo los numeros flotantes
                            # else:
                            #     # Unicamente envia al archivo los numeros flotantes
                            #     writer.writerow(
                            #         [time.time(), None, None, None, None, None, None, float(decoded_bytes[index])])
                except:
                    pass  # Pasa los strings o cualquier otro dato
                    # writer.writerow([time.time(),decode])
        with open("test_data.csv", "r") as f:  # Leemos cuantas lineas existen
            reader = csv.reader(f)
            linesn = len(list(reader))
        if linesn > lines:  # comparamos para saber si se escribio o solo fueron strings
            temporizador = time.perf_counter()
            counter = counter + 1  # Se incrementa contador
            if counter >= (divPaquetes * 2) + 1:
                counter = 0
            lines = linesn
        # print(counter)
    except UnicodeDecodeError:
        print("Wrong Data")
        counter = counter+1
    except:
        print("Bye Bye")
        break
