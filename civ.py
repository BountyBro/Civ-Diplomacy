''' TO-DO:
- Replace update_attributes()'s culture_step & tech_step parameters w/ their respective formulas (see how tech is assigned).
'''
##### DEPENDENCIES #####
import planet
import numpy as np
from random import random
# from model import MAX_CULTURE, proclaim_culture_victory # Removed for circular import fix



##### CONSTANTS #####
MAX_CULTURE = 100   # Amount of culture required for a culture victory.



##### FUNCTIONS #####
def proclaim_culture_victory(civ_id):
    # we need to stop the simulation and declare a winner
    print(f"\tCivilization {civ_id} has achieved a culture victory!")



##### CLASSES #####
class Civ:
    id_iter = 0
    def __init__(self, tech= 0, culture= 0, military= 0):
        # Model Controllers:
        self.civ_id = Civ.id_iter               # The civilzation ID for unique identification and iteration.
        self.num_planets = 0                    # Positive integer value. civ loses at self.num_planets == 0.
        self.alive = True                       # Set to False when len(self.planets) == 0.
        self.has_won_culture_victory = False    # Added flag for clean stop.
        self.planets = {}                       # Dictionary of planets owned by the civ. Key is the planet ID, value is the planet object.
        Civ.id_iter += 1
        # Attributes:
        self.friendliness = random()            # The friendliness of a civ. 
        self.culture = max(0, culture)          # The attribute that determines how close a civ is to a culture victory.
        self.military = max(0, military)        # The attribute that determines a civ's odds of success in war.
        self.tech = max(0, tech)                # The attribute that determines how far a civ can travel.
        self.resources = np.zeros(3)            # Resources: [0]: Energy; [1]: Food: [2]; Minerals.
        self.demand = np.zeros(3)               # Need for resources (refer to prior line).
        self.surplus = np.zeros(3)              # Excess of resources.
        self.deficit = np.zeros(3)              # Deficit of resources.
        self.population = 1.0                   # Total population of this civ. Units in 1,000 people.    
        self.population_cap = 0.0               # Maximum limit of population as determined by sum(self.planets.population_cap). Units in 1,000 people.
        self.max_growth_rate = 0                # Ceiling of population growth.
        
        
    def update_attributes(self, culture_step= 0, friendliness_step= 0, military_step = 0, resources_step= [0] * 3):
        # Population
        self.population += self.population * self.max_growth_rate * min(1.0, float(self.resources[1]) / self.population)
        # Attributes
        self.culture += culture_step
        self.friendliness += friendliness_step
        self.military += military_step
        self.tech += 0.5 * np.log(self.population) + 0.3 * self.resources[0] / self.population
        # Resources
        self.resources += resources_step
        self.demand = np.array([(self.population + self.tech + self.military) / 10, self.population, self.military * 0.3])
        flux = self.resources - self.demand
        self.surplus = np.where(0 < flux, flux, 0)
        self.deficit = np.where(flux < 0, 0, flux)
        # Check Victory Condition
        if not self.has_won_culture_victory and self.culture >= MAX_CULTURE:
            self.has_won_culture_victory = True # Set flag
            proclaim_culture_victory(self.civ_id) # Call local version

    def check_if_dead(self, t):
        if self.num_planets == 0:
            self.kill_civ(t)
            return True
        return False

    def kill_civ(self, t):
        self.alive = False
        for planet in self.planets.values():
            planet.remove_civ()
        self.planets.clear()
        self.num_planets = 0.0
        self.population = 0.0
        print(f"\tCivilization {self.civ_id} has been eliminated at turn {t}.")

    # Getters

    def get_id(self):
        return self.civ_id

    def get_alive(self):
        return self.alive
    
    def get_planet(self, planet_id):
        return self.planets.get(planet_id, None)
    
    def get_planets(self):
        return self.planets
    
    def get_planet_ids(self):
        return list(self.planets.keys())

    def get_planet_positions(self):
        return [planet.get_pos() for planet in self.planets.values()]

    def get_num_planets(self):
        return self.num_planets

    def get_population(self):
        return self.population
    
    def get_population_cap(self):
        return self.population_cap

    def get_resources(self):
        return self.resources   # Returns a list.

    def get_culture(self):
        return self.culture

    def get_military(self):
        return self.military
    
    def get_tech(self):
        return self.tech
    
    def get_friendliness(self):
        return self.friendliness