#Made with Mistral IA

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class QuiverDisplay:
    def __init__(self, figsize=(10, 8)):
        """Initialise l'affichage 3D et prépare la figure."""
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.vectors = {}  # Dictionnaire pour stocker les vecteurs par nom
        self.quiver_objects = {}  # Dictionnaire pour stocker les objets quiver par nom
        self.ax.set_xlim([-1.1, 1.1])
        self.ax.set_ylim([-1.1, 1.1])
        self.ax.set_zlim([-1.1, 1.1])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

    def add_vector(self, name, vector, color='r', length=0.5):
        """Ajoute un vecteur à l'affichage avec un nom unique."""
        if name in self.vectors:
            print(f"Erreur : Le vecteur '{name}' existe déjà.")
            return
        self.vectors[name] = list(vector) + [color, length]
        print(self.vectors[name])

    def update_vector(self, name, new_vector):
        """Met à jour un vecteur existant par son nom."""
        if name not in self.vectors:
            print(f"Erreur : Le vecteur '{name}' n'existe pas.")
            return
        self.vectors[name] = list(new_vector) + [self.vectors[name][3], self.vectors[name][4]]

    def _orient_to_posvec(self, vector):
        """Convertit un vecteur en position (0,0,0) et composantes (u,v,w)."""
        return (0, 0, 0, vector[0], vector[1], vector[2])

    def show(self):
        """Affiche la figure."""
        for vector, (cle, valeur) in enumerate(self.vectors.items()):
            x, y, z, u, v, w = self._orient_to_posvec(valeur[0:3])
            if vector in self.quiver_objects:
                self.quiver_objects[vector].remove()  # Supprime l'ancien quiver
            self.quiver_objects[vector] = self.ax.quiver(x, y, z, u, v, w, color=valeur[3])#, length=valeur[4])
            print(f"{cle} : x={u};y={v};z={w}")
        plt.pause(1)

    def clear(self):
        """Efface tous les vecteurs."""
        self.vectors.clear()
        for quiver in self.quiver_objects.values():
            quiver.remove()
        self.quiver_objects.clear()
        self.fig.canvas.draw_idle()
