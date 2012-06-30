#include <OneWire.h>

// For every sensor found it outputs to serial:
// SensorID,CurrentTemp,Readout time,Current time
 


OneWire ds(10);  // on pin 10

struct SensorData {
  byte addr[8];
  float temp;
  unsigned long time;
};

SensorData Senzori[8];
byte currentSensor = 0;
byte attachedSensors = 0;

void setup(void) {
  Serial.begin(9600);
}

void loop(void) {
  byte i;
  byte present = 0;
  byte data[12];
  byte addr[8];
  float celsius;

  //Search for the sensors  
  if ( !ds.search(addr)) {
    currentSensor = 0;
    ds.reset_search();
    delay(250);
    return;
  }
 
  //CRC is not valid exit loop
  if (OneWire::crc8(addr, 7) !=   addr[7]) {
      return;
  }

  ds.reset();
  ds.select(addr);
  ds.write(0x44,1);         // start conversion, with parasite power on at the end
  
  delay(1000);                          // maybe 750ms is enough, maybe not
  
  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);                       // Read Scratchpad

  //Get the temperature
  for ( i = 0; i < 9; i++) {            // we need 9 bytes
    data[i] = ds.read();
  }
  

  // convert the data to actual temperature
  unsigned int raw = (data[1] << 8) | data[0];
  byte cfg = (data[4] & 0x60);
  if (cfg == 0x00) raw = raw << 3;  // 9 bit resolution, 93.75 ms
  else if (cfg == 0x20) raw = raw << 2; // 10 bit res, 187.5 ms
  else if (cfg == 0x40) raw = raw << 1; // 11 bit res, 375 ms
   
  celsius = (float)raw / 16.0;
  
  Senzori[currentSensor].time = millis();
  Senzori[currentSensor].temp = celsius;
  memcpy(Senzori[currentSensor].addr, addr, 8);
  currentSensor++;
  if (attachedSensors < currentSensor)
    attachedSensors = currentSensor;
  
  if (Serial.available()) {
    byte a = Serial.read();
    for (i=0; i<attachedSensors; i++) {
      // First line is the address
      for( byte j = 0; j < 8; j++) {
        Serial.print(Senzori[i].addr[j], HEX);
      }
      Serial.print(',');
      Serial.print(Senzori[i].temp);
      Serial.print(',');
      Serial.print(Senzori[i].time);
      Serial.print(',');      
      Serial.print(millis());
      Serial.println();          
    }
    Serial.println(); 
  }
}