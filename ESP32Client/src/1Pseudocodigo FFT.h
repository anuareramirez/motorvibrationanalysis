COMIENZA/MAIN
    Crea un objeto FFT
    Inicializa arreglo vReal[i]
    Inicializa arreglo vImag[i]
    Comienza comunicación Serial

    HACER MIENTRAS la comunicación Serial no sea iniciada
    TERMINA MIENTRAS

    Imprime "Ready"

    HACER POR SIEMPRE

        HACER MIENTRAS el número de samples a adquirir
            SI el tiempo que transcurrió desde la última adquisición de datos >= el intervalo de muestras ENTONCES
                Ingresa valor al arreglo vReal desde una lectura con ADC del Pin 32
                Ingresa valor al arreglo vReal igual a 0
        TERMINA HACER MIENTRAS

        Imprime los datos del arreglo vReal en el dominio del tiempo.
        Calcula la ventana de tipo Hann
        Imprime los datos del arreglo vReal con la ventana calculada en el dominio del tiempo.
        Computa la FFT
        Imprime los datos del arreglo vReal con la FFT computada en el dominio de las muestras adquiridas
        Imprime los datos del arreglo vImag con la FFT computada en el dominio de las muestras adquiridas
        Computa las magnitudes de la FFT
        Imprime los datos del arreglo vReal con las magnitudes de la FFT computada en el dominio de la frecuencia
        Calcula el pico mas alto de magnitud en el dominio de la frecuencia.
        Imprime el pico mas alto de magnitud en el dominio de la frecuencia.
    TERMINA 
