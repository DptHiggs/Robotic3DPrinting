//Louis Huygens
//28/02/2024


// Program for running the print head of 6DoF robotic 3D printer
// Takes a demand speed in the form of binary input on pins 6-12
// Ouputs speed to stepper driver in the form of a pulsed signal
//  performs retraction when direction pin changes bit

//Declare variables
int A, B, C, D, E, F, G, H;
int Bin;
unsigned long previousMillis = 0;
float Delay = 50;
bool State = 0;
bool lastState = 0;

//Assign IO
void setup() {
  Serial.begin(9600);
  pinMode(13, INPUT_PULLUP);
  pinMode(4, OUTPUT);         //Direction Out Pin
  pinMode(5, OUTPUT);         //Pulse Out Pin
  pinMode(6, INPUT_PULLUP);   //1 In Pin
  pinMode(7, INPUT_PULLUP);   //2 In Pin
  pinMode(8, INPUT_PULLUP);   //4 In Pin
  pinMode(9, INPUT_PULLUP);   //8 In Pin
  pinMode(10, INPUT_PULLUP);  //16 In Pin
  pinMode(11, INPUT_PULLUP);  //32 In Pin
  pinMode(12, INPUT_PULLUP);  //64 In Pin
}

void loop() {
  State = digitalRead(13);

  //Perform retraction upon change of pin state
  if (State != lastState) {
    if (digitalRead(13) == LOW) {
      digitalWrite(30, HIGH);
      for (int i = 0; i <= 3; i++) {
        digitalWrite(5, HIGH);
        digitalWrite(5, LOW);
        delay(17.44);
      }
    }
  }

  //Convert to binary
  Bin = InToBinary();
  //Calculate pulse delay
  Delay = 1 / (Bin * 0.9 * 1.638) * 1000;

  //Account for infinite pulse
  if (Bin == 0) {
    Bin = Bin + 0.001;
  }


  //Output pulse signal
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= Delay) {
    // save the last time you blinked the LED

    previousMillis = currentMillis;
    digitalWrite(4, LOW);
    digitalWrite(5, HIGH);
    digitalWrite(5, LOW);
  }

  lastState = State;
}

//Calculate input in binary
int InToBinary() {
  int Sum = 0;

  if (digitalRead(6) == LOW) {
    Sum += 1;
  }
  if (digitalRead(7) == LOW) {
    Sum += 2;
  }
  if (digitalRead(8) == LOW) {
    Sum += 4;
  }
  if (digitalRead(9) == LOW) {
    Sum += 8;
  }
  if (digitalRead(10) == LOW) {
    Sum += 16;
  }
  if (digitalRead(11) == LOW) {
    Sum += 32;
  }
  if (digitalRead(12) == LOW) {
    Sum += 64;
  }
  return (Sum);
}