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
  /// magnetique 
  while (!Serial);

  int8_t status = magSens.initialize();
  if (status != 0) {
    Serial.println("BMM150 initialization failed!");
    while (1);
  }
  Serial.println("BMM150 initialized.");
}


float readFiltered(int pin) {
  long sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    sum += analogRead(pin);
    delay(2); // Petit délai pour la stabilité
  }
  float meanRaw = sum / (float)NUM_SAMPLES;
  return meanRaw * (3.3 / 4095.0); // Convertit en volts
}

void loop() {
  float I[numFaces];
  float numerator[3] = {0, 0, 0}; // vecteur N numérateur
  float denominator = 0;

  // Lecture filtrée de chaque photodiode
  for (int i = 0; i < numFaces; i++) {
    I[i] = readFiltered(adcPins[i]);

    // Si la lumière est négligeable (< 0.1 V), on ignore la face
    if (I[i] < 0.1) continue;

    // Calcul du numérateur : somme (ni * Ii)
    for (int j = 0; j < 3; j++) {
      numerator[j] += normals[i][j] * I[i];
    }

    // Calcul du dénominateur : somme (Ii)
    denominator += I[i];
  }

  // Si aucune face n’a reçu de lumière : vecteur nul
  if (denominator == 0) {
    Serial.println("Aucune face éclairée.");
  } else {
    float N[3];
    for (int i = 0; i < 3; i++) {
      N[i] = numerator[i] / denominator;
    }

    Serial.print("Vecteur Soleil-Satellite (N) : ");
    Serial.print("X: "); Serial.print(N[0], 3);
    Serial.print(" Y: "); Serial.print(N[1], 3);
    Serial.print(" Z: "); Serial.println(N[2], 3); // Z = 0 ici
  }




  ///magnetique 
  magSens.read_mag_data();  // reads and compensates the data

  Serial.print("Vecteur Magnetique       (B) : ");

  Serial.print("X: "); Serial.print(magSens.mag_data.x);
  Serial.print(" Y: "); Serial.print(magSens.mag_data.y);
  Serial.print(" Z: "); Serial.println(magSens.mag_data.z);
  Serial.println("-------------------------");
  Serial.println("-------------------------");


  



  delay(1000);
}
