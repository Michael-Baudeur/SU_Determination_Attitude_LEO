import serial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# Remplace 'COMx' par ton port série (ex: 'COM3' sur Windows, '/dev/ttyUSB0' sur Linux)
ser = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)  # Attendre que la connexion série se stabilise

plt.ion()
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.show(block=False)

while True:
    try:
        line = ser.readline().decode().strip()
        if line == "":
            continue

        values = list(map(float, line.split(',')))
        if len(values) != 6:
            continue

        Nx, Ny, Nz, Bx, By, Bz = values


        Bx=Bx/50
        By=By/50
        Bz=Bz/50

        Nx=Nx*5
        Ny=Ny*5
        Nz=Nz*5

        ax.clear()
        ax.quiver(0, 0, 0, Nx, Ny, Nz, color='orange', label='Soleil (N)')
        ax.quiver(0, 0, 0, Bx, By, Bz, color='blue', label='Magnétique (B)')

        ax.set_xlim([-1, 1])
        ax.set_ylim([-1, 1])
        ax.set_zlim([-1, 1])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title("Vecteurs Soleil-Satellite (N) et Magnétique (B)")
        ax.legend()
        plt.draw()
        plt.pause(0.1)

    except KeyboardInterrupt:
        print("Arrêt par l'utilisateur")
        break
    except Exception as e:
        print("Erreur :", e)

ser.close()
