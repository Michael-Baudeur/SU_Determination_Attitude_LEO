#include <Wire.h>
#include <bmm150.h>

BMM150 compass;

void setup() {
  Serial.begin(9600);
  Serial.println("Hello I'm working!");
  
  while (!Serial);

  int8_t status = compass.initialize();
  if (status != 0) {
    Serial.println("BMM150 initialization failed!");
    while (1);
  }
  Serial.println("BMM150 initialized.");
}

void loop() {
  compass.read_mag_data();  // reads and compensates the data

  Serial.print("X: "); Serial.print(compass.mag_data.x);
  Serial.print(" Y: "); Serial.print(compass.mag_data.y);
  Serial.print(" Z: "); Serial.println(compass.mag_data.z);

  delay(500);
}
