#include <Arduino.h>
#include <SparkFun_ADXL345.h>

#define SAMPLE_INTERVAL 333  //Velocidad de envio en us, equivalente a 3000Hz

double vReal[samples];

void ADXL345PowerOn(ADXL345 adxl)
{

  adxl.powerOn();          // Enciende ADXL345
  adxl.setRangeSetting(4); // Give the range settings
  adxl.setSpiBit(0);       // Configura el dispositivo: en modo 4 cables SPI = '0'
  adxl.set_bw(ADXL345_BW_1600);     // BW a 1600 adquiere a 3200HZ
  Serial.println("ADXL345 Initializing OK!");

}
void setup() {
  Serial.begin(115200);
  while(!Serial);
  Serial.println("Setup complete");
}

void loop() {
ADXL345 adxl = ADXL345(5) // Se declara el Pin CS de SPI, ADXL345(CS_PIN);
ADXL345PowerOn(adxl);
delay(500);

uint16_t i=0;
unsigned long sampling = micros();
int x,y,z;// Se inicializan variables para almacenar lecturas del sensor

while(i < samples) 
  {
    if ((micros() - sampling) >= SAMPLE_INTERVAL) //Se asegura que pasaron 333 us
    {
      sampling = micros();
      adxl.readAccel(&x, &y, &z);// Se leen los valores de ADXL345 y se almacenan
      vReal[i] = z; // Se almacena en el arreglo vReal
      i++;
    }
  }

  for (int i = 0; i < samples; i++)
  {
    vReal[i] = vReal[i] * 4 / 511; //Conversión a g's
  }
}
