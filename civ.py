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
beta_P = 0.5   # Tech growth from population
beta_E = 0.3   # Tech growth from energy
delta_P = 0.0005  # Culture growth per population
delta_T = 0.001   # Culture growth per tech
delta_R = 0.0005  # Culture growth per resource unit



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
        
        
    def update_attributes(self, culture_step= 0, friendliness_step= 0, military_step = 0, resources_step= [0] * 3):\
    
        food_per_capita = self.resources[1] / max(self.population, 1e-3)
        growth_rate = self.max_growth_rate * min(1.0, food_per_capita)
        self.population += self.population * growth_rate
        
        # Resources update
        for i in range(len(self.resources)):
            self.resources[i] += resources_step[i]

        # Tech Update
        energy = max(self.resources[0], 1e-3)  # prevent division by zero
        self.tech += beta_P * np.log(self.population) + beta_E * (energy / self.population)

        # Culture Update
        total_resources = sum(self.resources)
        self.culture += delta_P * self.population + delta_T * self.tech + delta_R * total_resources

        # Military Update
        sigma_P = 0.1
        sigma_T = 0.2
        sigma_M = 0.3
        minerals = self.resources[2]
        self.military = sigma_P * self.population + sigma_T * self.tech + sigma_M * minerals

        # Friendliness Updatetheta = 0.15
        beta_f = 0.1
        victories = getattr(self, 'victories', 0)  # default 0 if not set
        friendliness_after_victories = max(0.0, self.friendliness - theta * victories)
        cultural_pacification = beta_f * (self.culture / MAX_CULTURE)
        self.friendliness = min(1.0, friendliness_after_victories + cultural_pacification)  # cap friendliness at 1

        # Demand, Surplus and Deficit Update


        f_c = 1.0  # Food consumption per capita (adjust if necessary)
        e_c = 1.0  # Energy consumption per capita
        alpha_T = 0.1
        alpha_M = 0.1
        m_c = 0.3

        demand_energy = e_c * self.population + alpha_T * self.tech + alpha_M * self.military
        demand_food = f_c * self.population
        demand_minerals = m_c * self.military

        self.demand = np.array([demand_energy, demand_food, demand_minerals])

        # Calculate surplus and deficit
        flux = self.resources - self.demand
        self.surplus = np.where(flux > 0, flux, 0)
        self.deficit = np.where(flux < 0, -flux, 0)  # deficits are positive quantities

        # Check culture victory condition
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
        return self.resources   # Returns a list.

    def get_culture(self):
        return self.culture

    def get_military(self):
        return self.military
    
    def get_tech(self):
        return self.tech
    
    def get_friendliness(self):
        return self.friendliness