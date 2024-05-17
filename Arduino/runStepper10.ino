// 16/04/2024
// Louis Huygens
// runStepper10 Program

// Program runs stepper motor for 10s with specified pulse delay

//Declare variables
float time;
float startTime;

void setup() {

  Serial.begin(9600);
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

  //Start timer
  time = 10 * 1000;
  startTime = millis();

}

void loop() {
  float elapsedTime = millis() - startTime;

  //Pulse at constant rate for 10s
  if(elapsedTime < time){
    digitalWrite(5, LOW);
    delay(8.72);  //12.787
    digitalWrite(5, HIGH);

  }
  else {
    digitalWrite(5, LOW);
  }
}