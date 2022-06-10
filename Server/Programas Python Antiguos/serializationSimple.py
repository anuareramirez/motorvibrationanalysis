import serial
import time
import csv

ser = serial.Serial('/dev/cu.usbserial-0001', 115200)
ser.flushInput()

with open("PRUEBALOCAL.csv", "a") as f:  # Crea archivo o lo abre
    pass
with open("PRUEBALOCAL.csv", "r") as f:  # Lee cuantas lineas tiene el archivo csv
    reader = csv.reader(f)
    lines = len(list(reader))

while True:
    try:
        ser_bytes = ser.readline()  # Lee la linea serial
        decoded_bytes = str(
            ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))  # decodifica
        print(decoded_bytes)

        # Abre el archivo en modo append
        with open("PRUEBALOCAL.csv", "a") as f:
            # Crea un objeto para escribir en csv
            writer = csv.writer(f, delimiter=",")
            try:
                writer.writerow([time.time(), (decoded_bytes)])
            except:
                pass  # Pasa los strings o cualquier otro dato
                # writer.writerow([time.time(),decode])
    except UnicodeDecodeError:
        print("Wrong Data")
    except:
        print("byebye")
        break
