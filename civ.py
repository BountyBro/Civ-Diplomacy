##### DEPENDENCIES #####
import planet
import numpy as np
from random import random
from collections import Counter



##### CONSTANTS #####
MAX_CULTURE = 100   # Amount of culture required for a culture victory.
# Attribute Update Flow Variables
beta_P =    0.5       # Tech growth rate from population.
beta_E =    0.3       # Tech growth rate from energy.
delta_P =   0.0005    # Culture growth rate per population.
delta_T =   0.001     # Culture growth rate per tech.
delta_R =   0.0005    # Culture growth rate per resource unit.
sigma_P =   0.1       # Military growth rate from population.
sigma_T =   0.2       # Military growth rate from technology.
sigma_M =   0.3       # Military growth rate from minerals.
theta =     0.15      # Friendliness decay from combat victories.
beta_f =    0.1       # Friendliness growth from cultural smoothing.
e_c =       1.0       # Energy consumption per capita
f_c =       1.0       # Food consumption per capita (adjust if necessary)
m_c =       0.3       # Mineral consumption per capita.
alpha_T =   0.1       # Tech influence on energy demand.
alpha_M =   0.1       # Mineral influence on energy demand.



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
        Civ.id_iter += 1                        # Incrementing class ID counter.
        # Attributes:
        self.friendliness = random()            # The friendliness of a civ. 
        self.culture = max(0, culture)          # The attribute that determines how close a civ is to a culture victory.
        self.military = max(0, military)        # The attribute that determines a civ's odds of success in war.
        self.tech = max(0, tech)                # The attribute that determines how far a civ can travel.
        self.resources = {"energy": 0, "food": 0, "minerals": 0}
        self.demand = np.zeros(3)               # Need for resources (refer to prior line).
        self.surplus = np.zeros(3)              # Excess of resources.
        self.deficit = np.zeros(3)              # Deficit of resources.
        self.population = 1.0                   # Total population of this civ. Units in 1,000 people.    
        self.population_cap = 0.0               # Maximum limit of population as determined by sum(self.planets.population_cap). Units in 1,000 people.
        self.max_growth_rate = 0                # Ceiling of population growth.
        
    def update_attributes(self, resources_step= {"energy": 0, "food": 0, "minerals": 0}):
        # Preparing flow variables.
        food_per_capita = self.resources["food"] / max(self.population, 1e-3)
        growth_rate = self.max_growth_rate * min(1.0, food_per_capita)
        # Updating attributes
        self.population += self.population * growth_rate
        self.resources = dict(Counter(self.resources) + Counter(resources_step))
        self.culture += delta_P * self.population + delta_T * self.tech + delta_R * sum(self.resources.values())
        self.military = sigma_P * self.population + sigma_T * self.tech + sigma_M * self.resources["minerals"]
        self.tech += beta_P * np.log(self.population) + beta_E * (max(self.resources["energy"], 1e-3) / self.population) # max() to avoid ZeroDivisionError.
        # Friendliness Update
        friendliness_after_victories = max(0.0, self.friendliness - theta * getattr(self, 'victories', 0)) # Defaults victories to 0 if not set.
        cultural_pacification = beta_f * (self.culture / MAX_CULTURE)
        self.friendliness = min(1.0, friendliness_after_victories + cultural_pacification)  # Caps friendliness at 1.0.
        # Demand, Surplus and Deficit Update
        self.demand = {"energy": e_c * self.population + alpha_T * self.tech + alpha_M * self.military, "food": f_c * self.population, "minerals": m_c * self.military}
        flux = Counter(self.resources) - Counter(self.demand)
        self.surplus = dict((k, v if 0 < v else 0) for k, v in flux.items())
        self.deficit = dict((k, -v if v < 0 else 0) for k, v in flux.items())
        # Checking Culture Victory Condition
        if not self.has_won_culture_victory and self.culture >= MAX_CULTURE:
            self.has_won_culture_victory = True
            proclaim_culture_victory(self.civ_id)

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
        return self.resources   # Returns a dictionary w/ keys "energy", "food", and "minerals".

    def get_culture(self):
        return self.culture

    def get_military(self):
        return self.military
    
    def get_tech(self):
        return self.tech
    
    def get_friendliness(self):
        return self.friendliness