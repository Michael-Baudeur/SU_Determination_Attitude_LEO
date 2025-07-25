const int photodiodes[] = {32, 33, 34, 35};
const int numDiodes = 4;

void setup() {
  Serial.begin(115200);
}

void loop() {
  //for (int i = 0; i < numDiodes; i++) {
    int raw = analogRead(34);
    float voltage = raw * 3.3 / 4095.0;

    //Serial.print("Photodiode ");
    //Serial.print(i);
    //Serial.print(": ");
    //Serial.print(voltage, 3);
    //Serial.println(" V");
  //}
  Serial.print(voltage, 3);
  Serial.println("--------------");
  delay(1000);
}
