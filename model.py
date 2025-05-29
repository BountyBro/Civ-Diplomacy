''' File containing the 'Model' class, used to run a simulation.
Changelog:
v0.0.0: Established simulation end condition. - DM
v0.0.1: Created and filled 'Model' class. - NB
'''
##### DEPDENDENCIES #####
import numpy as np
from random import sample
import random
import visualize as vis
from civ import Civ, proclaim_culture_victory
from planet import Planet



##### USER-ADJUSTABLE #####
# MAX_CULTURE = 100 # Moved to civ.py
MIN_PLANETS = 3         # Inclusive lower bound integer for accepted range of planet count.
MAX_PLANETS = 25        # Inclusive higher bound integer for accepted range of planet count.
MIN_GRID_HEIGHT = 10    # Inclusive lower bound integer determining minimum grid height (y dimension).
MIN_GRID_WIDTH = 10     # Inclusive lower bound integer determining minimum grid width (x dimension).
MAX_GRID_HEIGHT = 50    # Inclusive higher bound integer determining maximum grid height (y dimension).
MAX_GRID_WIDTH = 50     # Inclusive higher bound integer determining maximum grid width (x dimension).
WAR_WIN_BOOST = 2         # Value of tech and military boost for winning a war.
COOPERATION_BOOST = 1      # Value of tech and culture boost for cooperating with another civ.


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
            random_available_coord = sample(coords[isAvailable].tolist(), 1)[0]
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
        return [
            [
            (float(self.list_planets[i].get_pos()[0] - self.list_planets[j].get_pos()[0]) ** 2 +
             float(self.list_planets[i].get_pos()[1] - self.list_planets[j].get_pos()[1]) ** 2) ** 0.5
            if i != j else 0
            for i in range(self.num_planets)
            ]
            for j in range(self.num_planets)
        ]
    
    def can_interact(self, civ1, civ2):
        for planet1 in civ1.get_planets().values():
            for planet2 in civ2.get_planets().values():
                dist = ((planet1.get_pos()[0] - planet2.get_pos()[0]) ** 2 + 
                    (planet1.get_pos()[1] - planet2.get_pos()[1]) ** 2) ** 0.5
                if civ1.get_tech() >= dist:
                    return True
        return False # Ensure False is returned if no interaction is possible
    
    def civs_cooperate(self, civ1, civ2):
        civ1.tech += COOPERATION_BOOST
        civ2.tech += COOPERATION_BOOST
        civ1.culture += COOPERATION_BOOST
        civ2.culture += COOPERATION_BOOST

    def civs_war(self, civ1, civ2):
        pass # War logic placeholder

    def interact_civs(self):
        interactions = [] 
        for i, civ1 in enumerate(self.list_civs):
            if not civ1.alive:
                continue
            for j, civ2 in enumerate(self.list_civs):
                if i >= j or not civ2.alive:
                    continue

                if self.can_interact(civ1, civ2) and self.can_interact(civ2, civ1):
                    interactions.append({'civ1': civ1, 'civ2': civ2, 'type': 'cooperation' if civ1.get_friendly() and civ2.get_friendly() else 'war'})
                    if civ1.get_friendly() == 1 and civ2.get_friendly() == 1:
                        print(f"Civilizations {civ1.get_id()} and {civ2.get_id()} are cooperating.")
                        self.civs_cooperate(civ1, civ2)
                    elif civ1.get_friendly() == 0 or civ2.get_friendly() == 0:
                        print(f"Civilizations {civ1.get_id()} and {civ2.get_id()} are at war!")
                        self.civs_war(civ1, civ2)
        return interactions

    def run_simulation(self):
        t = 0
        while True:
            t += 1
            print(f"Turn {t}")
            
            for civ in self.list_civs:
                if not civ.alive:
                    continue
                civ.update_attributes(civ.tech, civ.culture, civ.military, civ.friendly)
                if civ.has_won_culture_victory:
                    message = f"Civilization {civ.get_id()} has achieved a culture victory!"
                    # Yield message multiple times for display duration
                    yield message
                    yield message
                    yield message
                    return # Stop simulation

            interactions = self.interact_civs()
            yield t, interactions

            alive_civs = [civ for civ in self.list_civs if civ.alive]
            if len(alive_civs) == 1:
                message = f"Civilization {alive_civs[0].get_id()} has won the simulation through military!"
                yield message
                yield message
                yield message
                return
            if not alive_civs:
                message = "All civilizations have been eliminated."
                yield message
                yield message
                yield message
                return
