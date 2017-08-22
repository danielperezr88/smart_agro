#include <SimpleDHT.h>

#define BAUDRATE 115200
#define TEMPERATURE_MODE true
#define HUMIDITY_MODE false

const unsigned short upMoistPin   = (unsigned short) A12;
const unsigned short lowMoistPin  = (unsigned short) A13;
const unsigned short outDHTPin    = 7;
const unsigned short inDHTPin     = 6;
const unsigned short waterLvlPin  = (unsigned short) A10;
const unsigned short lightIntePin = (unsigned short) A11;
const unsigned short waterPumpPin = 22;
const unsigned short fanPin       = 23;

SimpleDHT11 dht11;

unsigned long pumpStoppingMillis = millis();
unsigned long fanStoppingMillis = millis();
int pumpState = LOW;
int fanState  = LOW;

void setup() {
  Serial1.begin(BAUDRATE);
  Serial.begin(BAUDRATE);
  Serial1.setTimeout(150);
  pinMode(waterPumpPin, OUTPUT);
  pinMode(fanPin,       OUTPUT);
}

void loop() {
  
  String option_str = "";
  long option = 0;
  
  if(Serial1.available()){
    //option_str = Serial1.readString();
    //Serial.println(option_str);
    //option = option_str.toInt();
    option = Serial1.parseInt();
    Serial.println(option);
    if(option == 1){
      readDHT(inDHTPin, TEMPERATURE_MODE, option);
    }else if(option == 2){
      readDHT(inDHTPin, HUMIDITY_MODE, option);
    }else if(option == 3){
      readDHT(outDHTPin, TEMPERATURE_MODE, option);
    }else if(option == 4){
      readDHT(outDHTPin, HUMIDITY_MODE, option);
    }else if(option == 5){
      readWaterLvl(option);
    }else if(option == 6){
      readLightInten(option);
    }else if(option == 7){
      readSoilMoist(upMoistPin, option);
    }else if(option == 8){
      readSoilMoist(lowMoistPin, option);
    }else if(option > 10000 && option < 30000){
      pumpWater(option - 10000, option);
    }else if(option == 30000){
      checkWaterPumpState(option);
    }else if(option > 30000 && option < 50000){
      activateFan(option - 30000, option);
    }else if(option == 50000){
      checkFanState(option);
    }else{
      Serial1.print("{\"o\":");
      Serial1.print(option);
      Serial1.print(",\"e\":");
      Serial1.print(1);
      Serial1.print(",\"v\":");
      Serial1.print(-1);
      Serial1.print("}\n");
    }
  }

  maybeStopPump();
  maybeStopFan();

}

void readDHT(int pin, bool mode, long option){

  byte temperature = 0;
  byte humidity = 0;
  bool result = true;
  unsigned short trials = 0;

  do{
    result = dht11.read(pin, &temperature, &humidity, NULL);
    trials++;
  }while(result && trials < 128);

  if(trials >= 128){
    Serial1.print("{\"o\":");
    Serial1.print(option);
    Serial1.print(",\"e\":");
    Serial1.print(1);
    Serial1.print(",\"v\":");
    Serial1.print(pin);
    Serial1.print("}\n");
    return;
  }

  if(mode == TEMPERATURE_MODE){
    Serial1.print("{\"o\":");
    Serial1.print(option);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print((int)temperature);
    Serial1.print("}\n");
  }else if(mode == HUMIDITY_MODE){
    Serial1.print("{\"o\":");
    Serial1.print(option);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print((int)humidity);
    Serial1.print("}\n");
  }
}

void readWaterLvl(long option){
  float lvl = analogRead(waterLvlPin);
  Serial1.print("{\"o\":");
  Serial1.print(option);
  Serial1.print(",\"e\":");
  Serial1.print(0);
  Serial1.print(",\"v\":");
  Serial1.print(lvl/1023*100);
  Serial1.print("}\n");
}

void readLightInten(long option){
  float inten = analogRead(lightIntePin);
  Serial1.print("{\"o\":");
  Serial1.print(option);
  Serial1.print(",\"e\":");
  Serial1.print(0);
  Serial1.print(",\"v\":");
  Serial1.print(inten/1023*100);
  Serial1.print("}\n");
}

void readSoilMoist(int pin, long option){
  float moist = analogRead(pin);
  Serial1.print("{\"o\":");
  Serial1.print(option);
  Serial1.print(",\"e\":");
  Serial1.print(0);
  Serial1.print(",\"v\":");
  Serial1.print((1023 - moist)/1023*100);
  Serial1.print("}\n");
}

void pumpWater(int ms, long option){
  pumpStoppingMillis = millis() + ms;
  if(pumpState == LOW) {
    pumpState = HIGH;
    digitalWrite(waterPumpPin, pumpState);
    Serial1.print("{\"o\":");
    Serial1.print(option);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print(1);
    Serial1.print("}\n");
  }
}

void activateFan(int ms, long option){
  fanStoppingMillis = millis() + ms;
  if(fanState == HIGH) {
    fanState = LOW;
    digitalWrite(fanPin, fanState);
    Serial1.print("{\"o\":");
    Serial1.print(option);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print(!fanState);
    Serial1.print("}\n");
  }
}

void maybeStopPump(){
  if(millis() >= pumpStoppingMillis && pumpState == HIGH){
    pumpState = LOW;
    digitalWrite(waterPumpPin, pumpState);
    Serial1.print("{\"o\":");
    Serial1.print(30000);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print(pumpState);
    Serial1.print("}\n");
  }
}

void maybeStopFan(){
  if(millis() >= fanStoppingMillis && fanState == LOW){
    fanState = HIGH;
    digitalWrite(fanPin, fanState);
    Serial1.print("{\"o\":");
    Serial1.print(50000);
    Serial1.print(",\"e\":");
    Serial1.print(0);
    Serial1.print(",\"v\":");
    Serial1.print(!fanState);
    Serial1.print("}\n");
  }
}

void checkWaterPumpState(long option){
  Serial1.print("{\"o\":");
  Serial1.print(option);
  Serial1.print(",\"e\":");
  Serial1.print(0);
  Serial1.print(",\"v\":");
  Serial1.print(pumpState);
  Serial1.print("}\n");
}

void checkFanState(long option){
  Serial1.print("{\"o\":");
  Serial1.print(option);
  Serial1.print(",\"e\":");
  Serial1.print(0);
  Serial1.print(",\"v\":");
  Serial1.print(!fanState);
  Serial1.print("}\n");
}

