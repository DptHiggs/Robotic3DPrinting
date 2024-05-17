// 16/04/2024
// Louis Huygens
// ReadThermistor program
// Based on program by Scott Campbell, 18/11/2015

// Program reads voltage across resistor, compares agains the known 5V input, and uses this to calculate the voltage dropped over the thermistor
// Thermal coefficients then used to relate resistance to temperature
// Results scaled appropriately


//Declare variables
int ThermistorPin = 0;
int Vo;
float R1 = 10000;
float logR2, R2, T, Tc, Tf;
float c1 = 1.009249522e-03, c2 = 2.378405444e-04, c3 = 2.019202697e-07;
float Tcc;
float Time;
float CurrentTime;

//Start timer
void setup() {
Serial.begin(9600);
Time = millis();
}

void loop() {

  //Calculate temperature
  Vo = analogRead(ThermistorPin);
  R2 = R1 * (1023.0 / (float)Vo - 1.0);
  logR2 = log(R2);
  T = (1.0 / (c1 + c2*logR2 + c3*logR2*logR2*logR2));
  Tc = T - 273.15;
  Tf = (Tc * 9.0)/ 5.0 + 32.0;
  //Scale
  Tcc = (-8.95 * Tc) + 745.79; 

  //Count time elapsed
  CurrentTime = millis() - Time;

  //Record temperatures for 160s period
  if (CurrentTime < 160000){
    Serial.println(Tcc);   
  }

  //Limit number of data points
  delay(50);
}