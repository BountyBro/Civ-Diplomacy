''' 'Planet' agent class file. Stores planet methods, constants, and simulation tools.
'''
##### DEPENDENCIES #####
import civ
import numpy as np
from random import randint
from collections import Counter



##### CONSTANTS #####
RESOURCE_MIN, RESOURCE_MAX =    100, 500
POPCAP_MIN, POPCAP_MAX =        1000, 5000



##### CLASSES #####
class Planet:
    id_iter = 0

    def __init__(self, num_planets, pos_x, pos_y):
        # Model Controllers:
        self.id = Planet.id_iter % num_planets                          # Planet ID for planet list index and unique identification
        self.civ = None                                                 # The civilization that owns this planet.
        self.pos_x = pos_x                                              # The x-coordinate of the planet.
        self.pos_y = pos_y                                              # The y-coordinate of the planet.
        Planet.id_iter += 1                                             # Iterates planet tracker index.
        self.resources = {"energy": randint(RESOURCE_MIN, RESOURCE_MAX), "food": randint(RESOURCE_MIN, RESOURCE_MAX), "minerals": randint(RESOURCE_MIN, RESOURCE_MAX)}
        self.population_cap = float(randint(POPCAP_MIN, POPCAP_MAX))    # Units in 1,000 people.

    def assign_civ(self, new_owner_civ):
        ''' Adds calling 'Planet' agent to new_owner_civ.planets and increments new_owner_civ's attributes accordingly.
        Inputs:
            - new_owner_civ: The 'Civ' agent that is being assigned to the calling 'Planet' agent.
        Outputs:
            - None. Adds calling 'Planet' agent to new_owner_civ.planets and increments new_owner_civ's attributes accordingly.
        '''
        if self.civ:        # If there's an existing owner, remove it first.
            self.remove_civ()
        self.civ = new_owner_civ
        if new_owner_civ:   # Ensure new_owner_civ is not None.
            new_owner_civ.planets[self.id] = self
            new_amt_resources = Counter(new_owner_civ.resources)
            new_amt_resources.update(self.resources)
            new_owner_civ.resources = dict(new_amt_resources)
            new_owner_civ.population_cap += self.population_cap
            new_owner_civ.num_planets += 1

    def remove_civ(self):
        ''' Unassigns the currently-occupying civ and decrements the civ's resources accordingly.
        Inputs:
            - None.
        Outputs:
            - None.
        '''
        if self.civ:
            # Calculate population to remove based on current number of planets
            population_to_remove = 0
            if self.civ.num_planets > 0: # Ensure num_planets is positive before division
                # This planet's share of population, capped by this planet's capacity.
                # Should be based on the idea that population is somewhat distributed.
                population_share = self.civ.population / self.civ.num_planets 
                population_to_remove = min(self.population_cap, population_share)
            # Ensure we don't make population negative
            population_to_remove = min(population_to_remove, self.civ.population) 

            del self.civ.planets[self.id]
            self.civ.num_planets -= 1 # Decrement num_planets AFTER using it for population calculation
            self.civ.population_cap -= self.population_cap
            self.civ.population -= population_to_remove
            new_resource_count = Counter(self.civ.resources)
            new_resource_count.subtract(Counter(self.resources))
            self.civ.resources = dict(new_resource_count)
            
            # Check if civ should be marked dead is handled by civ.check_if_dead() in model.py
            # which is called after a planet is conquered.

            self.civ = None

    # Getters

    def get_civ(self):
        return self.civ

    def get_pos(self):
        return (self.pos_x, self.pos_y)

    def get_id(self):
        return self.id
    
    def get_resources(self):
        return self.resources   # Returns a dictionary w/ keys "energy", "food", and "minerals".

    def get_population_cap(self):
        return self.population_cap