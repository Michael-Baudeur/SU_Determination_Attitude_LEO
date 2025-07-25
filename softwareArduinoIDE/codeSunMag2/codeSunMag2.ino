#include <bmm150.h>
#include <Wire.h>

BMM150 magSens;

const int NUM_SAMPLES = 10;
const int numFaces = 4;
const int adcPins[numFaces] = {32, 33, 34, 35}; // Pins des 4 photodiodes

// Normaux des 4 faces (X+, X−, Y+, Y−)
const float normals[numFaces][3] = {
  {1, 0, 0},   // +X
  {-1, 0, 0},  // -X
  {0, 1, 0},   // +Y
  {0, -1, 0}   // -Y
};

void setup() {
  Serial.begin(9600);
  while (!Serial);

  int8_t status = magSens.initialize();
  if (status != 0) {
    Serial.println("BMM150 initialization failed!");
    while (1);
  }
}

float readFiltered(int pin) {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(pin);
    delay(2);
  }
  float meanRaw = sum / (float)NUM_SAMPLES;
  return meanRaw * (3.3 / 4095.0); // en volts
}

void loop() {
  float I[numFaces];
  float numerator[3] = {0, 0, 0};
  float denominator = 0;

  // Lecture des photodiodes
  for (int i = 0; i < numFaces; i++) {
    I[i] = readFiltered(adcPins[i]);

    if (I[i] < 0.1) continue;

    for (int j = 0; j < 3; j++) {
      numerator[j] += normals[i][j] * I[i];
    }

    denominator += I[i];
  }

  float N[3] = {0, 0, 0};
  if (denominator != 0) {
    for (int i = 0; i < 3; i++) {
      N[i] = numerator[i] / denominator;
    }
  }

  // Lecture du capteur magnétique
  magSens.read_mag_data();

  float B[3];
  B[0] = magSens.mag_data.x;
  B[1] = magSens.mag_data.y;
  B[2] = magSens.mag_data.z;

  // Envoi pour Python : N.x, N.y, N.z, B.x, B.y, B.z
  Serial.print(N[0], 6); Serial.print(",");
  Serial.print(N[1], 6); Serial.print(",");
  Serial.print(N[2], 6); Serial.print(",");
  Serial.print(B[0], 6); Serial.print(",");
  Serial.print(B[1], 6); Serial.print(",");
  Serial.println(B[2], 6);

  delay(1000);
}
