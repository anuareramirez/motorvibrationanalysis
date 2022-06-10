#include <Arduino.h>
#include <SparkFun_ADXL345.h>
#include "arduinoFFT.h"
#include <SPI.h>
#include <LoRa.h>
//***************************************** DEFINE *****************************************//
//FFT
#define SAMPLE_INTERVAL 333  //Velovidad de envio en microsegundos
#define SCL_INDEX 0x00
#define SCL_TIME 0x01
#define SCL_FREQUENCY 0x02
#define SCL_PLOT 0x03
//LoRa

#define ss 15
#define rst 17
#define dio0 2

//************************************** CREATE OBJECTS **************************************//

arduinoFFT FFT = arduinoFFT(); /* Create FFT object */

//***************************************** VARIABLES ****************************************//

//FFT
const uint16_t samples = 4096; //This value MUST ALWAYS be a power of 2
const double samplingFrequency = 3000;
double vReal[samples];
double vFrec[samples];
// double vTime[samples];
double vImag[samples];

//LoRa
const int divPaquetes = samples/16; //Debe de ser el mismo que en el Serialization.py
int counter = 0;

//******************************************* SETUP *******************************************//

void setup() {
  Serial.begin(115200);
  while(!Serial);


  Serial.println("Setup complete");
}

//******************************************** LOOP *******************************************//

void loop() {
  
ADXL345 adxl = ADXL345(5);     // USE FOR SPI COMMUNICATION, ADXL345(CS_PIN);
ADXL345PowerOn(adxl);
delay(500);

uint16_t i=0;
unsigned long sampling = micros();
int x,y,z;// init variables hold results

Serial.println(sampling);
while(i < samples) 
  {
    if ((micros() - sampling) >= SAMPLE_INTERVAL) //333 son los microsegundos
    {
      sampling = micros();
      adxl.readAccel(&x, &y, &z);// Read the accelerometer values and store in variables x,y,z
      vReal[i] = z; // Se adquiere en 2^10
      vImag[i] = 0.0;
      i++;
    }
  }
  Serial.println(sampling);
  
  ADXL345PowerOff();
  LoRaPowerOn();

  for (int i = 0; i < samples; i++)
  {
    vReal[i] = vReal[i] * 4 / 511; //Conversión a g's
    // vFrec[i] = ((i * 1.0 * samplingFrequency) / samples);
    // vTime[i] = ((i * 1.0) / samplingFrequency);
  }
  
  Serial.println("Data:");
  PrintVector(vReal, samples, SCL_TIME);

    //Envio de Datos LoRa
  for (int i = 0; i < divPaquetes; i++)
  {
    // send packet
    LoRa.beginPacket(); 
    int tPack = samples/divPaquetes;
    for (int j = 0; j < (tPack); j++)
    {
      // LoRa.print(vTime[j+(i*(samples) / divPaquetes)], 6);
      // LoRa.print(" ");
      LoRa.print(vReal[j+(i * tPack)], 6);
      LoRa.print(" ");  
    }
    LoRa.endPacket();
  } 

  FFT.Windowing(vReal, samples, FFT_WIN_TYP_HANN, FFT_FORWARD);	/* Weigh data */
  FFT.Compute(vReal, vImag, samples, FFT_FORWARD); /* Compute FFT */
  FFT.ComplexToMagnitude(vReal, vImag, samples); /* Compute magnitudes */

  Serial.println("Computed magnitudes:");
  PrintVector(vReal, (samples >> 1), SCL_FREQUENCY);

 
  
  LoRaPowerOff();
  
  double a = FFT.MajorPeak(vReal, samples, samplingFrequency);
  Serial.println(a, 6);

  // while(true);
  delay(60000); /* Repeat after delay */
}


//************************************** OTHER FUNCTIONS **************************************//

void ADXL345PowerOn(ADXL345 adxl)
{

  adxl.powerOn();                   // Enciende ADXL345
  adxl.setRangeSetting(4);          // Give the range settings
  adxl.setSpiBit(0);                // Configure the device: 4 wire SPI mode = '0' or 3 wire SPI mode = 1
  adxl.set_bw(ADXL345_BW_1600);     // BW a 1600 adquiere a 3200HZ
  Serial.println("ADXL345 Initializing OK!");

}

void ADXL345PowerOff()
{
  SPI.endTransaction();
  Serial.println("ADXL OFF");
}

void LoRaPowerOn()
{
  LoRa.setPins(ss, rst, dio0);      // Setup LoRa transceiver module
  if (!LoRa.begin(915E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setSyncWord(0xF8);
  Serial.println("LoRa Initializing OK!");
}

void LoRaPowerOff()
{
  LoRa.end();
  Serial.println("LoRa OFF");
}

void PrintVector(double *vData, uint16_t bufferSize, uint8_t scaleType)
{
  for (uint16_t i = 0; i < bufferSize; i++)
  {
    double abscissa;
    /* Print abscissa value */
    switch (scaleType)
    {
      case SCL_INDEX:
        abscissa = (i * 1.0);
	break;
      case SCL_TIME:
        abscissa = ((i * 1.0) / samplingFrequency);
	break;
      case SCL_FREQUENCY:
        abscissa = ((i * 1.0 * samplingFrequency) / samples);
	break;
    }
    Serial.print(abscissa, 6);
    if(scaleType==SCL_FREQUENCY)
      Serial.print("Hz");
    Serial.print(" ");
    Serial.println(vData[i], 6);
  }
  Serial.println();
}