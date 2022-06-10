# motorvibrationanalysis
## Instalar
VS CODE

PlatformIO

Python3


## Para utilizar ESP32Client se instala en ESP32 conectado a sensor ADXL345

Configurar platformio.ini con lo siguiente

	[env:esp32dev]
	platform = espressif32
	board = esp32dev
	framework = arduino
	upload_port = /dev/cu.usbserial-0001 <-- En windows este puerto puede cambiar a un puerto COM (ejemplo COM5, COM6, etc.)
	monitor_speed = 115200
	lib_deps =  <-- Estas son las librerias que se necesitan para el proyecto LoRa, FFT, ADXL345
	sandeepmistry/LoRa@^0.8.0
	kosme/arduinoFFT@^1.5.6
	sparkfun/SparkFun ADXL345 Arduino Library@^1.0.0


## Para utilizar ESP32Server se instala en ESP32 conectado al Servidor

Configurar platformio.ini con lo siguiente

	[env:esp32dev]
	platform = espressif32
	board = esp32dev
	framework = arduino
	upload_port = /dev/cu.usbserial-4 <-- En windows este puerto puede cambiar a un puerto COM (ejemplo COM5, COM6, etc.)
	monitor_speed = 115200
	lib_deps = <-- Estas son las librerias que se necesitan para el proyecto LoRa
	sandeepmistry/LoRa@^0.8.0 



## Para utilizar Server/serialization.py se instala en el Servidor

Se deben correr los siguientes comandos de instalación en el servidor

	pip install pandas
	pip install plotly-express
	pip install numpy
	pip install scipy
