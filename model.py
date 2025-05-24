''' File containing the 'Model' class, used to run a simulation.
Changelog:
v0.0.0: Established simulation end condition. - DM
v0.0.1: Created and filled 'Model' class. - NB
'''
##### DEPDENDENCIES #####
import numpy as np
from random import sample
import visualize as vis
from civ import Civ
from planet import Planet



##### USER-ADJUSTABLE #####
MAX_CULTURE = 100       # Value of culture (see 'civ.py') required to trigger culture end condition for a civ.
MIN_PLANETS = 3         # Inclusive lower bound integer for accepted range of planet count.
MAX_PLANETS = 25        # Inclusive higher bound integer for accepted range of planet count.
MIN_GRID_HEIGHT = 10    # Inclusive lower bound integer determining minimum grid height (y dimension).
MIN_GRID_WIDTH = 10     # Inclusive lower bound integer determining minimum grid width (x dimension).
MAX_GRID_HEIGHT = 50    # Inclusive higher bound integer determining maximum grid height (y dimension).
MAX_GRID_WIDTH = 50     # Inclusive higher bound integer determining maximum grid width (x dimension).



##### CLASSES #####
class Model():
    def __init__(self, num_planets, grid_height, grid_width):
        self.num_planets = max(MIN_PLANETS, min(num_planets, MAX_PLANETS))  # Applying range constraint to input 'num_planets'
        self.grid = np.zeros(shape= (max(MIN_GRID_HEIGHT, min(grid_height, MAX_GRID_HEIGHT)), max(MIN_GRID_WIDTH, min(grid_width, MAX_GRID_WIDTH))))
        self.list_planets = []
        self.list_civs = [Civ(i, 0, 0, 0) for i in range(num_planets)]
        self.assign_planets()
        self.ranges = self.distances()

    def assign_planets(self):
        isAvailable = np.full(shape= self.grid.shape, fill_value = True)
        coords = np.array([[(row, col) for col in range(self.grid.shape[1])] for row in range(self.grid.shape[0])])
        for i in range(self.num_planets):
            random_available_coord = sample(coords[isAvailable])
            self.list_planets.append(Planet(i, random_available_coord[0], random_available_coord[1]))
            isAvailable[random_available_coord[0], random_available_coord[1]] = False
            self.list_planets[i].assign_civ(self.list_civs[i])
    
    def distances(self):
        ''' Returns a 2D array of dimensions 'num_planets'-by-'num_planets' that holds the distances between planets.
        All [x,y] pairs where x == y will be 0 (a planet's distance from itself is 0).
        All [x,y] and [y,x] pairs will yield the same value (distance is constant regardless of direction).
        Inputs:
            - Uses self.list_planets to retrieve planet postions.
            - Uses self.num_planets to determine list dimensions.
        Outputs: 
            - A 2D list of dimensions 'num_planets'-by-'num_planets'containing positive float values.
        '''
        return [[(float(self.list_planets[i].get_pos()[0] - self.list_planets[j].get_pos()[0]) ** 2 + float(self.list_planets[i].get_pos()[1] - self.list_planets[j].get_pos()[1]) ** 2) ** 0.5 if i != j else 0 for i in range(self.num_planets)] for j in range(self.num_planets)]



def proclaim_culture_victory(civ_id):
    # we need to stop the simulation and declare a winner
    print(f"Civilization {civ_id} has achieved a culture victory!")