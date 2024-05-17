/*
  16/04/2024
  Louis Huygens
  BLTouchBedLevel program

  Modified from code by jmcharg
  https://github.com/jmcharg/BLTouch-Tester/blob/master/BLTouch_Tester_v1.0.ino
  BLTouch Test sensor program
  Connect 5V to Red
  Connect Gnd to Brown
  Connect Pin 9 to Orange / Yellow
  Connect Pin 2 to White.

  Serial port to 9600 and dont send CR or LF

  Send 1 to Pin Down
  Send 2 to Pin Up
  Send 3 to Test
  Send 4 to Reset

*/

#include <Servo.h>

Servo myservo;  

int val;  
int incomingByte = 0;

const byte BLTouchPin = 2;  // Connect the white wire from the BLTouch to this pin
const byte BLTouchControl = 3;   // Connect the orange wire from the BLTouch sensor to this pin
volatile byte state = LOW;
volatile byte lastState = LOW;

void setup() {
  Serial.begin(9600);
  myservo.attach(BLTouchControl); 
  pinMode(2, INPUT_PULLUP);
  myservo.write(60);
  pinMode(A5, OUTPUT);
  digitalWrite(A5, LOW);
}

void loop() {
  //Set pin position down
  myservo.write(10);

  //If servo touched, lift pin, set output and reset
  if (digitalRead(2) == HIGH) {
    myservo.write(90);
    Serial.println("Resetting");
    digitalWrite(A5, HIGH);
    delay(1000);
    digitalWrite(A5, LOW);
    myservo.write(10);
  }
}