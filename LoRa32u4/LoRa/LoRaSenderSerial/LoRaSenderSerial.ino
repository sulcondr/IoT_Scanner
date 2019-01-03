#include <SPI.h>
#include <LoRa.h>

// uncomment the section corresponding to your board
// BSFrance 2017 contact@bsrance.fr 

//  //LoR32u4 433MHz V1.0 (white board)
//  #define SCK     15
//  #define MISO    14
//  #define MOSI    16
//  #define SS      1
//  #define RST     4
//  #define DI0     7
//  #define BAND    433E6 
//  #define PABOOST true

//  //LoR32u4 433MHz V1.2 (white board)
//  #define SCK     15
//  #define MISO    14
//  #define MOSI    16
//  #define SS      8
//  #define RST     4
//  #define DI0     7
//  #define BAND    433E6 
//  #define PABOOST true 

  //LoR32u4II 868MHz or 915MHz (black board)
  #define SCK     15
  #define MISO    14
  #define MOSI    16
  #define SS      8
  #define RST     4
  #define DI0     7
  #define BAND    868E6  // 915E6
  #define PABOOST true 

int counter = 0;
long int freq[8] = {868.1E6, 868.3E6, 868.5E6, 867.1E6, 867.3E6, 867.5E6, 867.7E6, 867.9E6};
long frequency = 868E6;
int sf[6] = {7, 8, 9, 10, 11, 12};
int power[13] = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
String message = "";

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("LoRa Sender");
  LoRa.setPins(SS,RST,DI0);
  if (!LoRa.begin(BAND,PABOOST)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }
  LoRa.setFrequency(868100000);
  LoRa.setSpreadingFactor(7);
}

void loop() {
//  frequency = freq[counter%8];
//  Serial.println("Setting freq to: " + String(frequency));
//  LoRa.setFrequency(frequency);
  
  message = Serial.readString();
  if (message != ""){
  Serial.print("Sending packet: ");
  Serial.print(message);
  // send packet
  LoRa.beginPacket();
  
  LoRa.print(message);
//  LoRa.print("Sending LoRa packet kmllukyjtrfdxstdryftugyihuoijkpjouhiygutfyrdt cfyvtubyiunouniybutvyrc vgbhnnbvgyfctdxerxtrcytvunumber: ");
//  LoRa.print(counter);
//  LoRa.print("at freq: ");
//  LoRa.print(frequency);
  LoRa.endPacket();
  counter++;
  delay(1000);

  Serial.println("Setting sf to: " + String(sf[counter%2]));
  LoRa.setSpreadingFactor(sf[counter%2]);
  //Serial.println("Setting power to: " + String(counter%20));
  }
  
}
