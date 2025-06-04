''' 'Civ' agent class file. Stores civ methods, constants, and simulation tools.
'''
##### DEPENDENCIES #####
import planet
import numpy as np
from random import random
from collections import Counter



##### CONSTANTS #####
MAX_CULTURE = 800     # Amount of culture required for a culture victory.
DESPERATION_POINT = 0.6         # Value at which a civilization is considered "desparate", and will prioritize war over trade.
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
m_c =       1.0       # Mineral consumption per capita.
alpha_T =   0.1       # Tech influence on energy demand.
alpha_M =   0.1       # Mineral influence on energy demand.
epsilon_R = 0.5       # Resource pressure's influence on desperation.
epsilon_P = 0.5       # Population pressure's influence on desparation. 



##### CLASSES #####
class Civ:
    id_iter = 0
    instances = [] # Added to track all civ instances

    def __init__(self, num_civs, tech= 0, culture= 0, military= 0, friendliness= random(), resources= {"energy": 0, "food": 0, "minerals": 0}):
        base_resources = Counter({"energy": 0, "food": 0, "minerals": 0})
        base_resources.update(Counter(resources))
        # Model Controllers:
        self.civ_id = Civ.id_iter % num_civs        # The civilzation ID for unique identification and iteration.
        self.num_planets = 0                        # Positive integer value. civ loses at self.num_planets == 0.
        self.alive = True                           # Set to False when len(self.planets) == 0.
        self.has_won_culture_victory = False        # Added flag for clean stop.
        self.planets = {}                           # Dictionary of planets owned by the civ. Key is the planet ID, value is the planet object.
        Civ.id_iter += 1                            # Incrementing class ID counter.
        Civ.instances.append(self)                  # Added to track all civ instances
        # Attributes:
        self.friendliness = max(0, friendliness)    # The friendliness of a civ. 
        self.culture = max(0, culture)              # The attribute that determines how close a civ is to a culture victory.
        self.military = max(0, military)            # The attribute that determines a civ's odds of success in war.
        self.tech = max(0, tech)                    # The attribute that determines how far a civ can travel.
        self.resources = base_resources
        self.demand = {}                            # Needs for resources (energy, food, minerals). Initialized as dict.
        self.surplus = {}                           # Excess of resources. Initialized as dict.
        self.deficit = {}                           # Deficit of resources. Initialized as dict.
        self.population = 1.0                       # Total population of this civ. Units in 1,000 people.    
        self.population_cap = 0.0                   # Maximum limit of population as determined by sum(self.planets.population_cap). Units in 1,000 people.
        self.max_growth_rate = 0                    # Ceiling of population growth.
        self.desperation = 0.0                      # Determinant to prioritize war or trade.   
        self.is_desparate = False                   # Checks desparation barrier.      
        self.resource_pressure_component = 0.0      # Rp_i for WarScore: sum_k Deficit_ik / sum_k Demand_ik
        self.traded_resources = [{"energy": 0, "food": 0, "minerals": 0} for i in range(num_civs)]
        self.relations = ["Neutral" for i in range(num_civs)]   # 3 States: "Neutral" can war or trade; "Peace" can trade, but only war if desparate; "War" cannot trade.
        # Attributes for historical data plotting
        self.victories = 0
        self.population_pressure = 0.0
        self.food_pressure = 0.0
        self.energy_pressure = 0.0
        self.minerals_pressure = 0.0
        self.war_initiations_this_turn = 0
        # Resource stocks are available via self.resources
        # num_trade_partners and is_at_war will be determined by Model per turn.

    def reset_turn_counters(self):
        ''' Static setter for 'Civ' agents' 'war_initiations_this_turn' attribute.
        '''
        self.war_initiations_this_turn = 0

    def update_attributes(self):
        '''
        Inputs:
            - None. All flow variables are calculated dynamically and rely on the calling 'Civ' agent's existing attributes.
        Outputs:
            - None. Updates calling 'Civ' agent's attributes, and potentially prints in case of cultural victory during update.
        '''
        # Preparing flow variables.
        food_per_capita = self.resources["food"] / max(self.population, 1e-3)
        self.max_growth_rate = 0.01 + 0.005 * np.tanh(self.tech / 100)
        # growth_rate = self.max_growth_rate * min(1.0, food_per_capita)
        growth_rate = min(1.0, food_per_capita)
        # Updating attributes
        self.population += self.population * growth_rate
        self.culture += delta_P * self.population + delta_T * self.tech + delta_R * sum(self.resources.values())
        self.military = sigma_P * self.population + sigma_T * self.tech + sigma_M * self.resources["minerals"]
        self.tech += beta_P * np.log(self.population) + beta_E * (max(self.resources["energy"], 1e-3) / self.population) # max() to avoid ZeroDivisionError.
        # Friendliness Update
        friendliness_after_victories = max(0.0, self.friendliness - theta * getattr(self, 'victories', 0)) # Defaults victories to 0 if not set.
        cultural_pacification = beta_f * (self.culture / MAX_CULTURE)
        self.friendliness = min(1.0, friendliness_after_victories + cultural_pacification)  # Caps friendliness at 1.0.
        # Demand, Surplus and Deficit Update
        self.demand = {"energy": e_c * self.population + alpha_T * self.tech + alpha_M * self.military, "food": f_c * self.population, "minerals": m_c * self.military}
        flux = Counter(self.resources)
        flux.subtract(Counter(self.demand))
        self.surplus = dict((k, v if 0 < v else 0) for k, v in flux.items())
        self.deficit = dict((k, abs(v) if v < 0 else 0) for k, v in flux.items())
        # Calculate population pressure, avoiding division by zero
        current_pop_cap = self.get_population_cap()
        if current_pop_cap <= 0:
            if self.get_population() > 0:
                self.population_pressure = float(self.get_population())
            else:
                self.population_pressure = 0.0
        else:
            self.population_pressure = max(0.0, float(self.get_population() - current_pop_cap) / current_pop_cap)
        # Calculate individual resource pressures (deficit / demand, if demand > 0)
        resource_keys = ["energy", "food", "minerals"]
        for key in resource_keys:
            demand_val = self.demand.get(key, 0)
            deficit_val = self.deficit.get(key, 0)
            pressure_attr_name = f"{key}_pressure" # e.g., self.energy_pressure
            if demand_val > 0:
                setattr(self, pressure_attr_name, deficit_val / demand_val)
            else:
                setattr(self, pressure_attr_name, 0.0 if deficit_val == 0 else 1.0) # Max pressure if demand is 0 but deficit exists
        # Calculate deficit pressure for overall desperation calculation
        sum_demand_val = np.sum(list(self.get_demand().values()))
        sum_deficit_val = np.sum(list(self.get_deficit().values()))
        deficit_pressure_for_desperation = deficit_pressure_for_desperation = sum_deficit_val / sum_demand_val if sum_demand_val > 0 else 0.0
        self.resource_pressure_component = deficit_pressure_for_desperation # Store Rp_i
        self.desperation = float(epsilon_R * self.population_pressure + epsilon_P * deficit_pressure_for_desperation)
        self.is_desparate = DESPERATION_POINT < self.desperation
        # Checking Culture Victory Condition
        if not self.has_won_culture_victory and self.culture >= MAX_CULTURE:
            self.has_won_culture_victory = True
            # print(f"\tCivilization {self.civ_id} has achieved a culture victory!")

    def change_relations(self, civ2, new_relation):
        ''' Changes relations between calling 'Civ' agent and provided civ2 agent.
        Inputs:
            - civ2: The civ whose relations with the calling civ are being changed.
            - new_relation: The string 
        Outputs:
            - None. Modifies agent attributes.
        '''
        if not (new_relation in ["Neutral", "Peace", "War"]):
            raise ValueError(f"change_relations() called w/ \"{new_relation}\" relation, which isn't \"Neutral\", \"War\", or \"Peace\".")
        self.relations[civ2.get_id()] = new_relation
        civ2.relations[self.get_id()] = new_relation

    def break_trade(self, civ2):
        ''' Resets traded_values between calling 'Civ' agent and provided 'Civ' agent.
        Inputs:
            - civ2: Another civ agent that has traded w/ the calling agent.
        Outputs:
            - None. Modifies agent attributes.
        '''
        # If resources have been traded,..
        if(self.traded_resources[civ2.get_id()] != {"energy": 0, "food": 0, "minerals": 0}):
            # Return traded resources, and...
            traded_amount = Counter(self.resources)
            traded_amount.subtract(Counter(self.traded_resources[civ2.get_id()]))
            self.resources = dict(traded_amount)
            new_civ2_resources = Counter(civ2.resources)
            new_civ2_resources.update(Counter(self.traded_resources[self.get_id()]))
            civ2.resources = dict(new_civ2_resources)
            # Set traded resource values to 0.
            self.traded_resources[civ2.get_id()] = {"energy": 0, "food": 0, "minerals": 0}
            civ2.traded_resources[self.get_id()] = {"energy": 0, "food": 0, "minerals": 0}

    def check_if_dead(self, t, civ_list):
        '''
        Inputs:
            - t: Turn timestep used to establish chronological order for visualization purposes.
            - civ_list: Used by kill_civ() to break trades. "Dead men seal no deals".
        Outputs:
            - None. Calls kill_civ on the calling 'Civ' agent if it has no planets.
        '''
        if self.num_planets == 0:
            self.kill_civ(t, civ_list)
            return True
        return False

    def kill_civ(self, t, civ_list):
        '''
        Inputs:
            - t: Turn timestep used to establish chronological order for visualization purposes.
        Outputs:
            - None. Prints civ elimination and declares the 'Civ' agent dead.
        '''
        self.alive = False
        for planet in self.planets.values():
            planet.remove_civ()
        for civ in [civ for civ in civ_list if not (civ is self)]:
            self.break_trade(civ)
        self.planets.clear()
        self.num_planets = 0.0
        self.population = 0.0
        # print(f"\tCivilization {self.civ_id} has been eliminated at turn {t}.")

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
    
    def get_deficit(self):
        return self.deficit     # Returns a dictionary w/ keys "energy", "food", and "minerals".
    
    def get_surplus(self):
        return self.surplus     # Returns a dictionary w/ keys "energy", "food", and "minerals".
    
    def get_demand(self):
        return self.demand      # Returns a dictionary w/ keys "energy", "food", and "minerals".
    
    def get_desperation(self):
        return self.desperation