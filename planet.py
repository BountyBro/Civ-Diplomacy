'''TO-DO:
Define initial planet attribute values.
'''
##### DEPENDENCIES #####
import civ
import numpy as np
from random import randint



##### CONSTANTS #####
RESOURCE_MIN, RESOURCE_MAX = 100, 500
POPCAP_MIN, POPCAP_MAX = 1000, 5000

##### CLASSES #####
class Planet:
    id_iter = 0
    def __init__(self, pos_x, pos_y):
        # Model Controllers:
        self.id = Planet.id_iter                                        # Planet ID for planet list index and unique identification
        self.civ = None                                                 # The civilization that owns this planet.
        self.pos_x = pos_x                                              # The x-coordinate of the planet.
        self.pos_y = pos_y                                              # The y-coordinate of the planet.
        Planet.id_iter += 1                                             # Iterates planet tracker index.
        # Resources: [0]: Energy; [1]: Food: [2]; Minerals.
        self.resources = np.array([randint(RESOURCE_MIN, RESOURCE_MAX) for i in range(3)])
        self.population_cap = float(randint(POPCAP_MIN, POPCAP_MAX))    # Units in 1,000 people.

    def assign_civ(self, new_owner_civ):
        if self.civ:        # If there's an existing owner, remove it first.
            self.remove_civ()
        self.civ = new_owner_civ
        if new_owner_civ:   # Ensure new_owner_civ is not None.
            new_owner_civ.planets[self.id] = self
            new_owner_civ.resources += self.resources
            new_owner_civ.population_cap += self.population_cap
            new_owner_civ.num_planets += 1

    def remove_civ(self):
        if self.civ:
            del self.civ.planets[self.id]
            self.civ.num_planets -= 1
            self.civ.population_cap -= self.population_cap
            self.civ.population -= min(self.population_cap, self.civ.population / self.civ.num_planets)
            self.civ.resources -= self.resources
            self.civ = None

    def get_civ(self):
        return self.civ

    def get_pos(self):
        return (self.pos_x, self.pos_y)

    def get_id(self):
        return self.id
    
    def get_resources(self):
        return self.resources   # Returns a list of [energy, food, resources].

    def get_population_cap(self):
        return self.population_cap