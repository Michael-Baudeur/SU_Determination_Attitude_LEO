@author: arujan ( le dieu grand seigneur)
"""

import serial
import time
import re
import numpy as np
import matplotlib.pyplot as plt

# --- Port série ---
port = '/dev/tty.usbserial-0001'   # adapte selon ton port
baudrate = 115200
ser = serial.Serial(port, baudrate, timeout=1)
time.sleep(2)

print("Lecture des données depuis l'Arduino...\n")

# --- Données temporaires ---
courants = {}
mag_data = {'x': None, 'y': None, 'z': None}

# --- Préparation du graphique ---
plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1, 1])
ax.set_ylim([-1, 1])
ax.set_zlim([-1, 1])
ax.set_xlabel('X (+/-)')
ax.set_ylabel('Y (+/-)')
ax.set_zlabel('Z (+/-)')
ax.set_title('Vecteurs : Soleil–Satellite (orange) et Champ magnétique (bleu)')
ax.view_init(elev=30, azim=-60)

try:
    while True:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue

        # --- Lecture du magnétomètre ---
        if line.startswith("X:"):
            try:
                mag_data['x'] = float(line.split(":")[1])
            except:
                continue
        elif line.startswith("Y:"):
            try:
                mag_data['y'] = float(line.split(":")[1])
            except:
                continue
        elif line.startswith("Z:"):
            try:
                mag_data['z'] = float(line.split(":")[1])
            except:
                continue

        # --- Lecture des panneaux solaires ---
        match = re.search(r"Panneau\s+(\d+).*?:\s*([-+]?[0-9]*\.?[0-9]+)", line)
        if match:
            num = int(match.group(1))
            courant = float(match.group(2))
            courants[num] = courant

        # --- Si on a à la fois le champ magnétique complet et les 6 panneaux ---
        if None not in mag_data.values() and len(courants) == 6:
            # ---------- Vecteur magnétique ----------
            Vx, Vy, Vz = mag_data['x'], mag_data['y'], mag_data['z']
            normB = np.linalg.norm([Vx, Vy, Vz])
            if normB > 0:
                B_norm = np.array([Vx, Vy, Vz]) / normB
            else:
                B_norm = np.zeros(3)

            # ---------- Vecteur Soleil–Satellite ----------
            I1, I2, I3, I4, I5, I6 = [courants[i] for i in range(1, 7)]
            Vs = np.array([I1 - I4, I2 - I5, I3 - I6])
            normS = np.linalg.norm(Vs)
            if normS > 0:
                S_norm = Vs / normS
            else:
                S_norm = np.zeros(3)

            # ---------- Tracé ----------
            ax.cla()
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
            ax.set_xlabel('X (+/-)')
            ax.set_ylabel('Y (+/-)')
            ax.set_zlabel('Z (+/-)')
            ax.set_title('Vecteurs : Soleil–Satellite (orange) et Champ magnétique (bleu)')
            ax.view_init(elev=30, azim=-60)

            # Axes de référence
            ax.quiver(0, 0, 0, 1, 0, 0, color='r', length=0.8, arrow_length_ratio=0.05)
            ax.quiver(0, 0, 0, 0, 1, 0, color='g', length=0.8, arrow_length_ratio=0.05)
            ax.quiver(0, 0, 0, 0, 0, 1, color='b', length=0.8, arrow_length_ratio=0.05)

            # Vecteur champ magnétique
            ax.quiver(0, 0, 0, B_norm[0], B_norm[1], B_norm[2],
                      color='royalblue', length=0.8, arrow_length_ratio=0.15)

            # Vecteur Soleil-satellite
            ax.quiver(0, 0, 0, S_norm[0], S_norm[1], S_norm[2],
                      color='orange', length=0.8, arrow_length_ratio=0.15)

            plt.draw()
            plt.pause(0.05)

            # Nettoyage pour nouvelle itération
            courants = {}
            mag_data = {'x': None, 'y': None, 'z': None}

except KeyboardInterrupt:
    print("\nArrêt du programme par l'utilisateur.")
    plt.ioff()
    plt.show()

finally:
    ser.close()
