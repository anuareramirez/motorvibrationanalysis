import os
import serial
import time
import csv
import datetime
import itertools
import pandas as pd
import plotly.express as px
import numpy as np
import scipy.integrate
import scipy.signal



def calc_rms(df):
    rms = df.copy()**2
    rms = rms.mean()**0.5
    return rms


def stat_calc(df):
    df_stats = pd.concat([df.abs().max(), calc_rms(df)], axis=1)
    df_stats.columns = ['Acceleration Peak (g)', 'Acceleration RMS (g)']
    df_stats['Crest Factor'] = df_stats['Acceleration Peak (g)'] / \
        df_stats['Acceleration RMS (g)']
    df_stats['Standard Deviation (g)'] = df.std()
    df_stats.index.name = 'Data Set'
    return df_stats


def _highpass(array, fs, cutoff=[1., 2000], axis=-1, filt_order=3):
    if cutoff[1] >= fs/2:
        cutoff[1] = fs/2.1
    if cutoff[0] == 0:
        return array
    """Apply a highpass filter to an array."""
    array = np.moveaxis(array, axis, -1)

    sos_coeffs = scipy.signal.butter(
        N=filt_order, Wn=cutoff, btype='bandpass', fs=fs, output='sos',
    )

    init_state = scipy.signal.sosfilt_zi(sos_coeffs)

    for _ in range(2):
        init_fwd = init_state * \
            array[(Ellipsis, 0) + ((None,)*init_state.ndim)]
        init_fwd = np.moveaxis(init_fwd, array.ndim-1, 0)
        array, _zo = scipy.signal.sosfilt(
            sos_coeffs, array, axis=-1, zi=init_fwd)
        array = array[..., ::-1]

    return np.moveaxis(array, -1, axis)


def _integrate(array, dt, axis=-1, cutoff=[1., 2000], filt_order=3, alpha=1):
    """Integrate data over an axis."""
    window = scipy.signal.tukey(len(array), alpha=alpha)
    array = np.transpose(window*np.transpose(array))

    result = scipy.integrate.cumtrapz(array, dx=dt, initial=0, axis=axis)

    result = _highpass(result, 1/dt, cutoff=cutoff,
                       axis=axis, filt_order=filt_order)

    return result


def iter_integrals(array, dt, axis=-1, cutoff=[1., 2000], filt_order=3, alpha=1):
    """Iterate over conditioned integrals of the given original data."""
    array = _highpass(array, fs=1/dt, cutoff=cutoff,
                      axis=axis, filt_order=filt_order)
    while True:
        array.setflags(write=False)  # should NOT mutate shared data
        yield array
        # array will be replaced below -> now ok to edit
        array.setflags(write=True)
        array = _integrate(array, dt, axis=axis, cutoff=cutoff,
                           filt_order=filt_order, alpha=alpha)


def build_df(df, array, scale):
    df[df.columns] = array*scale
    return df

ser = serial.Serial('/dev/cu.usbserial-0001', 115200)
ser.flushInput()
counter = 0
lines=0

samplingFrequency = 3000
samples = 4096
divPaquetes = samples/16  # Debe ser el mismo que en Main.ino del Client

temporizador = time.perf_counter()
fechaYHora = datetime.datetime.now()

vFrec = []
vTime = []
for i in range(samples):
    vTime.append((i * 1.0) / samplingFrequency)
for i in range(int(samples / 2)):
    vFrec.append((i * 1.0 * samplingFrequency) / samples)
if lines == 0:
    with open("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "a") as f:   # Leemos cuantas lineas existen
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["Time", "ADXL345", "Frequency", "Amplitude"])

while True:
    try:
        ser_bytes = ser.readline()  # Lee la linea serial

        if time.perf_counter() - temporizador > 20: #Si pasan mas de 20 segundos sin recibir transmision se reinicia el contador y se procesa informaci??n
            with open("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "r") as f:   # Leemos cuantas lineas existen
                reader = csv.reader(f)
                linesDoc = len(list(reader))
                print(linesDoc)
            
            df = pd.read_csv("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), on_bad_lines='skip', usecols=['Time', 'ADXL345'])
            first_empty_row = df[df.isnull().all(axis=1) == True].index.tolist()[0]  # Adquiere los datos hasta encontrar datos vacios
            df = df.head(first_empty_row)
            df = df.set_index('Time')
            fs = len(df)/(df.index[-1]-df.index[1])
            accel, vel, displ = itertools.islice(iter_integrals(df.to_numpy(),
                                                    dt=1/fs,
                                                    cutoff=[5, fs/3],
                                                    filt_order=4,
                                                    alpha=.1,  # apply a taper at start and end, 1 is a hanning, 0 is a rectangular
                                                    axis=0), 3)

            df_vel = build_df(df.copy(), vel, 9810)  # Conversi??n de 9.81 a mm/s
            avRMS = calc_rms(df)
            vvRMS = calc_rms(df_vel)
            with open("vRMS.csv", "a") as f:   # Leemos cuantas lineas existen
                pass

            with open("vRMS.csv", "r") as f:   # Leemos cuantas lineas existen
                reader = csv.reader(f)
                linesDoc = len(list(reader))

            with open("vRMS.csv", "a") as f:   # Leemos cuantas lineas existen
                writer = csv.writer(f, delimiter=",")
                if linesDoc == 0:
                    writer.writerow(["Time", "vRMS (g)", "vRMS (mm/s)", "Estado"])
                if avRMS[0] > 0.9 or vvRMS[0] > 3:
                    writer.writerow(
                        [datetime.datetime.now(), avRMS[0], vvRMS[0], "Mal Estado aceleraci??n mayor que 0.9 o velocidad mayor a 3.0"])
                elif avRMS[0] > 0.5 or vvRMS[0] > 1.5:
                    writer.writerow(
                        [datetime.datetime.now(), avRMS[0], vvRMS[0], "Buen Estado"])
                else:
                    writer.writerow([datetime.datetime.now(), avRMS[0],
                                    vvRMS[0], "Excelente Estado"])

            counter = 0
            fechaYHora = datetime.datetime.now()
            lines=0
            if lines == 0:
                with open("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "a") as f:   # Leemos cuantas lineas existen
                    writer = csv.writer(f, delimiter=",")
                    writer.writerow(["Time", "ADXL345", "Frequency", "Amplitude"])


        decoded_bytes = str(
            ser_bytes[0:len(ser_bytes)-2].decode("utf-8"))  # decodifica
        decoded_bytes = decoded_bytes.split(" ")  # Divide cada que encuentra un espacio y lo envia a un arreglo
        print(decoded_bytes)



        with open("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "a") as f:  # Abre el archivo en modo append
            # Crea un objeto para escribir en csv
            writer = csv.writer(f, delimiter=",")
            for index in range(len(decoded_bytes)):
                try:
                    if counter < divPaquetes:
                        writer.writerow(
                            [vTime[index + lines], float(decoded_bytes[index])]) # Unicamente envia al archivo los numeros flotantes
                        print(lines)
                    else:
                        writer.writerow(
                            ["","",vFrec[index + int((counter - divPaquetes) * 8)], float(decoded_bytes[index])]) # Unicamente envia al archivo los numeros flotantes
                        print(lines)
                except:
                    pass
        # with open("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute), "r") as f:   # Leemos cuantas lineas existen
        #     reader = csv.reader(f)
        #     linesn = len(list(reader))
        results = pd.read_csv("test_motor {}-{}-{} {}-{}.csv".format(fechaYHora.day,fechaYHora.month,fechaYHora.year, fechaYHora.hour, fechaYHora.minute))
        linesn = len(results)
        if linesn > lines:  # comparamos para saber si se escribio o solo fueron strings
            temporizador = time.perf_counter()
            counter = counter + 1  # Se incrementa contador
            lines = linesn
    except UnicodeDecodeError:
        print("Wrong Data")
        counter = counter + 1
        temporizador = time.perf_counter()

    except KeyboardInterrupt:
        print("Bye Bye")
        break
