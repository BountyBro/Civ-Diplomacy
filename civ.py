##### DEPENDENCIES #####
import planet
from random import choice, randint
# from model import MAX_CULTURE, proclaim_culture_victory # Removed for circular import fix



##### CONSTANTS #####
MAX_CULTURE = 100   # Amount of culture required for a culture victory.



##### FUNCTIONS #####
def proclaim_culture_victory(civ_id):
    # we need to stop the simulation and declare a winner
    print(f"\tCivilization {civ_id} has achieved a culture victory!")



##### CLASSES #####
class Civ:
    def __init__(self, civ_id, tech= 0, culture= 0, military= 0):
        # Model Controllers:
        self.civ_id = civ_id                        # The civilzation ID for unique identification and iteration.
        self.num_planets = 0                        # Positive integer value. civ loses at self.num_planets == 0.
        self.alive = True                           # Set to False when len(self.planets) == 0.
        self.has_won_culture_victory = False        # Added flag for clean stop.
        self.planets = {}                           # Dictionary of planets owned by the civ. Key is the planet ID, value is the planet object.
        # Attributes:
        self.friendly = choice([0,1])        # Corrected: Was random.choice(0,1)
        self.culture = culture                      # The attribute that determines how close a civ is to a culture victory.
        self.military = military                    # The attribute that determines a civ's odds of success in war.
        self.tech = tech                            # The attribute that determines how far a civ can travel.
        self.tech_growth = randint(1, 3)     # Controls the rate of the civ's technological growth.
        self.mil_growth = randint(1, 3)      # Controls the rate of the civ's miilitary growth. Corrected: Was self.military_growth in some contexts
        self.culture_growth = randint(1, 3)  # Controls the rate of the civ's cultural growth.    
        ''' NEW ATTRIBUTES - Daniil's suggestions:
        self.population = 0                         # Guessing init_pop = 1, but do they need more to take over new planets?
        self.growth = 0                             # Assuming this equates to #-of-steps to increment population where it takes X steps to do so.
        self.growth_remainder = X                   # Placeholder in case of alternative growth control method. Holds #-of-steps until population increment.
        self.economy = 0                            # Still not sure what this does functionally unless we make resources modify attributes.
        self.resources = []                         # Stores resources gained through owned planets or trade.
        '''    

    def update_attributes(self, tech, culture, military, friendly):
        self.tech += self.tech_growth
        self.culture += self.culture_growth
        self.military += self.mil_growth # Corrected attribute name
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
        self.num_planets = 0
        print(f"\tCivilization {self.civ_id} has been eliminated at turn {t}")

    # Getters

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

    def get_id(self):
        return self.civ_id

    def get_friendly(self):
        return self.friendly

    def get_culture(self):
        return self.culture

    def get_military(self):
        return self.military
    
    def get_tech(self):
        return self.tech
    
''' NEW GETTERS:
    def get_population(self):
        return self.population

    def get_growth(self):
        return self.growth

    def get_growth_remainder(self):
        return self.growth_remainder

    def get_economy(self):
        return self.economy

    def get_resources(self):
        return self.resources   # Returns a list.
''' 