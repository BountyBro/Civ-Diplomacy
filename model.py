''' Simulation control file. Utilizes agent files ('civ.py', 'planet.py') to host an agent-based, grid-based simulation.
- Mainly utilized through 'Model' object class.
- Stores simulation-centric constants and user-adjustable values.
- Model().run_simulation() can print results, but visualize.visualize_simulation(Model()) will provide a .gif of the simulation.
'''
##### DEPDENDENCIES #####
from civ import Civ
from planet import Planet
import numpy as np                          # Added for numeric array operations.
import os                                   # Added for directory creation.
import plotting                             # Added for plotting functions.
from collections import Counter             # Added for adaptable resource arithmetic operations.
from random import sample, random, choice   # Used in planet initialization, probabilistic operations.
from datetime import datetime



##### CONSTANTS #####
# War Score Constants:
W1_FRIENDLINESS = 0.1
W2_POP_PRESSURE = 0.3
W3_RES_PRESSURE = 0.2
W4_CULT_DIFF = 0.2
WAR_SCORE_EFFECTIVENESS_MODIFIER = 0.50 # Reduces likelihood of WarScore triggering war (was 0.60)

# User-Adjustable:

# SCENARIO RANGE CONSTRAINTS:
MIN_PLANETS = 3                             # Inclusive lower bound integer for accepted range of planet count.
MAX_PLANETS = 30                            # Inclusive higher bound integer for accepted range of planet count.
MIN_GRID_HEIGHT = 5                         # Inclusive lower bound integer determining minimum grid height (y dimension).
MIN_GRID_WIDTH = 5                          # Inclusive lower bound integer determining minimum grid width (x dimension).
MAX_GRID_HEIGHT = 50                        # Inclusive higher bound integer determining maximum grid height (y dimension).
MAX_GRID_WIDTH = 50                         # Inclusive higher bound integer determining maximum grid width (x dimension).
# INTERACTION MODIFIERS:
WAR_WIN_BOOST = 0.15                        # Value of tech and military boost for winning a war.
COOPERATION_BOOST = 0.1                     # Value of tech and culture boost for cooperating with another civ.
WAR_PENALTY = 0.1                           # Value of tech and culture penalty for an attacker losing a war.
TRADE_TECH_BOOST = 0.5                      # Tech increase when a civ trades w/o receiving resources in return.
AGGRESSION_FRIENDLINESS_THRESHOLD = 0.10    # Friendliness below this can trigger aggression (was 0.15).
MAX_TURNS_SIM = 200                         # Defining a max turn for the simulation run, used for save_count in animation.
PLANET_CONQUEST_CHANCE_ON_WIN = 1.0         # Chance to conquer a planet after winning a battle for it.
# Analysis TOGGLES:  True = ON, False = OFF
LOG_TOGGLE = True                           # Boolean to toggle .txt log of simulation data.
MASTER_PLOT_TOGGLE = True                   # Overrides all other plot toggles.
PLOT_H1 = True                              # Boolean to toggle if run_simulation should write a plot showing the correlation between desparation and war to output/plots.
PLOT_H2 = True                              # Boolean to toggle if run_simulation should write a plot showing the correlation between military power and war to output/plots.
PLOT_H3 = True                              # Boolean to toggle if run_simulation should write a plot showing the correlation between friendliness and culture to output/plots.
PLOT_H4 = True                              # Boolean to toggle if run_simulation should write a plot showing the correlation between culture comparisons and interactions to output/plots.
PLOT_H5 = True                              # Boolean to toggle if run_simulation should write a plot showing the impact of tech and resources on war and trade to output/plots.
PLOT_H6 = True                              # Boolean to toggle if run_simulation should write a plot showing civ lifespans and win conditions.



##### CLASSES #####
class Model():
    def __init__(self, num_planets= 15, grid_height= 30, grid_width= 30, scenario= "", generate_plots_controller=True):
        ''' Model class constructor that creates a numpy array for a grid, with lists for civ agents and planet agents assigned to the civ agents.
        Inputs:
        - num_planets:  The # of planets to be used. Each planet is assigned to 1 civ, such that every civ has 1 planet, and vice versa.
        - grid_height: How tall to make the grid. Recommended to maintain equality with grid_width to stabilize simulation consistency.
        - grid_width: How wide to make the grid. Recommended to maintain equality with grid_height to stabilize simulation consistency.
        Output:
            - A Model object with attributes for the number of agents, a numpy array grid, and an array of distances between planet agents.
        '''
        # Prepare grid and 'Planet' agents for 'Civ' agent assignment.
        self.num_planets = max(MIN_PLANETS, min(num_planets, MAX_PLANETS))  # Applying range constraint to input 'num_planets'.
        self.list_planets = []
        self.grid = np.zeros(shape= (max(MIN_GRID_HEIGHT, min(grid_height, MAX_GRID_HEIGHT)), max(MIN_GRID_WIDTH, min(grid_width, MAX_GRID_WIDTH))))
        # Allocate 'Civ' agents according to scenario, if any.
        match scenario.lower():
            case "friendzone":
                self.list_civs = [Civ(self.num_planets, friendliness= 1) for i in range(num_planets)]
            case "thunderdome":
                self.list_civs = [Civ(self.num_planets, friendliness= 0) for i in range(num_planets)]
            case "juggernaut":
                self.list_civs = [Civ(self.num_planets) if i != 0 else Civ(self.num_planets, friendliness= 0, resources= {"energy": 500, "food": 500, "minerals": 500}) for i in range(num_planets)]
            case "wolf":
                self.list_civs = [Civ(self.num_planets, friendliness= 1) if i != 0 else Civ(self.num_planets, friendliness= 0) for i in range(num_planets)]
            case _:
                self.list_civs = [Civ(self.num_planets) for i in range(num_planets)]
        self.assign_planets(num_planets)
        self.ranges = self.distances()
        # Store all initial civ IDs for complete historical tracking
        self.all_initial_civ_ids = {civ.get_id() for civ in self.list_civs} 
        self.max_turns = MAX_TURNS_SIM  # Store max_turns as an instance attribute       
        self.historical_data = []       # Added for plotting
        self.civ_ids = self.list_civs.copy()
        self.end_type = ""
        self.generate_plots_controller = generate_plots_controller  # Boolean to control if plots should be generated at the end of the simulation.
        
        

    def assign_planets(self, num):
        ''' Model __init__() helper function. Assigns civs to unoccupied planets such that every planet is assigned 1 civ.
        Input:
            - Model Object: Holds the grid that planet coords are assigned to, the number of planets to make, a list of civs, and the list to append them to.
        Output:
            - Updates the source object's list_planets with randomly-assigned coordinates, and assigns civs from the provided list to each planet.
        '''
        isAvailable = np.full(shape= self.grid.shape, fill_value = True)
        coords = np.array([[(row, col) for col in range(self.grid.shape[1])] for row in range(self.grid.shape[0])])
        for i in range(self.num_planets):
            random_available_coord = sample(coords[isAvailable].tolist(), 1)[0]
            self.list_planets.append(Planet(num, random_available_coord[0], random_available_coord[1]))
            isAvailable[random_available_coord[0], random_available_coord[1]] = False
            self.list_planets[i].assign_civ(self.list_civs[i])
        return
    
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
        ''' Returns a boolean checking if any of civ2's planets are within civ1's range.
        Inputs:
            - civ1: The civ seeking interaction.
            - civ2: The civ that is the target of interaction.
        Output:
            - A boolean representing if any of civ2's planets are within civ1's range.
        '''
        return np.any([[self.ranges[p1.get_id()][p2.get_id()] < (civ1.tech / 10) for p1 in civ1.get_planets().values()] for p2 in civ2.get_planets().values()])
    
    def civs_cooperate(self, civ1, civ2):
        ''' interact_civs() helper function. Boosts involved civs' tech and culture based on COOPERATION_BOOST constant, and is used civs decide to cooperate.
        Inputs:
            - civ1: 1st involved civ agent.
            - civ2: 2nd involved civ agent.
        Output:
            - No output. Modifies provided civ agents' tech and culture attributes.
        '''
        civ1.change_relations(civ2, "Peace")
        civ1.tech +=            COOPERATION_BOOST
        civ2.tech +=            COOPERATION_BOOST
        civ1.culture +=         COOPERATION_BOOST
        civ2.culture +=         COOPERATION_BOOST

    def civs_war(self, attacker, defender, t, targeted_planet):
        ''' interact_civs() helper function. Boosts involved civs' tech and culture based on COOPERATION_BOOST constant, and is used civs decide to cooperate.
        Inputs:
            - attacker: The civ agent invading targeted_planet.
            - defender: The civ that owns targeted_planet.
            - t: Turn number. Used in civ.check_if_dead().
            - targeted_planet: The planet agent that war is being waged on.  
        Output:
            - No output. Modifies provided objects' tech and culture attributes.
        '''
        # print(f"\tCiv {attacker.get_id()} is attacking Civ {defender.get_id()}, targeting planet {targeted_planet.get_id() if targeted_planet else 'N/A'}.")
        # Removing trade relations if resources are being traded between attacker and defender.
        attacker.break_trade(defender)
        attacker.change_relations(defender, "War")
        # Determining combat power.
        attacker_power = attacker.get_military() * (1 + (0.1 * attacker.get_tech()))
        defender_power = defender.get_military() * (1 + (0.1 * defender.get_tech()))
        total_combat_power = attacker_power + defender_power
        
        # Determining war result.
        # Stalemate: Neither civ has any combat power, so nothing happens.
        if total_combat_power == 0: 
            # print(f"\tStalemate between Civ {attacker.get_id()} and Civ {defender.get_id()} due to zero combat power.")
            return
        attacker_win_chance = attacker_power / total_combat_power

        # Attacker wins: Attacker increments military and tech by WAR_WIN_BOOST, increments their victory counter, and potentially takes targeted_planet.
        if random() < attacker_win_chance:
            # print(f"\tAttacker Civ {attacker.get_id()} wins against Civ {defender.get_id()}!")
            attacker.military += WAR_WIN_BOOST # Attacker gets military boost
            attacker.tech += WAR_WIN_BOOST     # Attacker gets tech boost
            attacker.victories += 1
            # Attacker conquers the specific targeted planet, if it's valid and still owned by the defender.
            if targeted_planet and targeted_planet.get_civ() == defender:
                if random() < PLANET_CONQUEST_CHANCE_ON_WIN:
                    # print(f"\tCiv {attacker.get_id()} conquers planet {targeted_planet.get_id()} from Civ {defender.get_id()}.")
                    targeted_planet.assign_civ(attacker) # Planet changes owner
                else:
                    pass # print(f"\tCiv {attacker.get_id()} won the battle but failed to secure planet {targeted_planet.get_id()} from Civ {defender.get_id()}.")
                # Check if defender is eliminated after losing the planet (or failing to lose it but maybe other losses)
                if defender.check_if_dead(t, self.list_civs):
                    # print(f"\tCiv {defender.get_id()} has been eliminated by Civ {attacker.get_id()}.")
                    self.list_civs.remove(defender)
            elif targeted_planet and targeted_planet.get_civ() != defender:
                pass # print(f"\tTargeted planet {targeted_planet.get_id()} is no longer owned by defender Civ {defender.get_id()}. No conquest from this battle.")
            elif not targeted_planet:
                pass # print(f"\tDefender Civ {defender.get_id()} had no specific planet targeted (e.g. no planets left to target). No conquest from this battle.")
        
        # Defender wins: Defender increments culture, tech, and military by WAR_WIN_BOOST, increments their victory counter, and keeps targeted_planet. Attacker takes a penalty to culture, tech.
        else:
            # print(f"\tDefender Civ {defender.get_id()} wins the battle against attacker Civ {attacker.get_id()}!")
            defender.military += WAR_WIN_BOOST
            defender.tech += WAR_WIN_BOOST
            # defender.culture += WAR_WIN_BOOST
            defender.victories += 1
            attacker.tech = max(0, attacker.tech - WAR_PENALTY)
            attacker.culture = max(0, attacker.culture - WAR_PENALTY)
            # print(f"\tAttacker Civ {attacker.get_id()} loses {WAR_PENALTY} tech and culture due to failed attack.")

    def civs_trade(self, civ1, civ2):
        ''' interact_civs() helper function. Exchanges resources from surplus values to cancel out deficit values. civ2's tech will be incremented in case of no civ2 resource deficits.
        Inputs:
            - civ1: Civ seeking to resolve a resource deficit.
            - civ2: Civ willing to give their surplus resources to resolve civ1's resource deficit in exchange for resolving their own deficits, or gaining tech.
        Output:
            - No output. Modifies provided civ agents' resource values and potentially increments civ2's tech attribute.
        '''
        resource_keys = ["energy", "food", "minerals"]
        civ1_surplus = civ1.get_surplus()
        civ1_deficit = civ1.get_deficit()
        civ2_surplus = civ2.get_surplus()
        civ2_deficit = civ2.get_deficit()

        # Calculate potential flow of resources from civ2 to civ1
        # Based on what civ2 has in surplus and civ1 needs (deficit)
        flow_from_civ2_to_civ1 = Counter({
            key: min(civ2_surplus.get(key, 0), civ1_deficit.get(key, 0)) for key in resource_keys
        })

        # Calculate potential flow of resources from civ1 to civ2
        # Based on what civ1 has in surplus and civ2 needs (deficit)
        flow_from_civ1_to_civ2 = Counter({
            key: min(civ1_surplus.get(key, 0), civ2_deficit.get(key, 0)) for key in resource_keys
        })

        # amt_to_trade is the net change in resources for civ1
        # Positive values mean civ1 gains that resource, negative means civ1 loses
        amt_to_trade = Counter(flow_from_civ2_to_civ1)
        amt_to_trade.subtract(flow_from_civ1_to_civ2)
        civ1_new_resources = Counter(civ1.resources)
        civ1_new_resources.update(amt_to_trade)
        civ2_new_resources = Counter(civ2.resources)
        civ2_new_resources.subtract(amt_to_trade)

        # Exchanging resources
        civ1.resources = dict(civ1_new_resources)
        civ2.resources = dict(civ2_new_resources)
        # Storing traded values in case of removal later; values stored are positive if received from that civ_id, and negative if given to that civ_id.
        civ1.traded_resources[civ2.get_id()] = amt_to_trade
        civ2.traded_resources[civ1.get_id()] = -amt_to_trade

        # Tech boost logic:
        # Civ2 gets a tech boost if it was a net giver of resources and received less or nothing in return.
        # i.e., the total value of resources civ2 gave to civ1 is greater than what civ1 gave to civ2.
        
        # Total value civ2 gave to civ1 (sum of positive values in amt_to_trade from civ1's perspective)
        value_civ2_gave_to_civ1 = sum(v for k, v in amt_to_trade.items() if v > 0)

        # No Mutual Need: civ2 increments their tech by TRADE_TECH_BOOST.
        if value_civ2_gave_to_civ1 == 0:
            # print(f"\tCiv {civ2.get_id()} gets a tech boost from trade with Civ {civ1.get_id()}.")
            civ2.tech += TRADE_TECH_BOOST

    # Unstable attempt at new logic. Not called anywhere. Disregard.
    def interact_civs(self, t, active_civs):
        ''' run_simulation() helper function and the civ agent decision-making hub. Runs actions for each living civ during turn t.
        Inputs:
            - t: Turn counter. Used for civ.check_if_dead() in civs_war() helper function.
            - active_civs: A list of alive civs. Civs are still checked as elimination during iterations is possible.
        Outputs:
            - interactions:             Data tracked for visualization purposes.
            - conquest_events:          Data tracked for visualization purposes.
            - civ_interaction_counts:   Data tracked for visualization purposes.
        '''
        interactions = []
        conquest_events = []
        civ_interaction_counts = {civ.get_id(): {'trades': 0, 'wars_participated': 0, 'wars_initiated': 0} for civ in active_civs if civ.get_alive()}
        for actor in active_civs:
            if not actor.get_alive():
                continue
            reachable_civs = [civ for civ in active_civs if not (civ is actor) and self.can_interact(actor, civ)]

            # war_targets = [civ for civ in reachable_civs if actor.is_desparate or actor.relations[civ.get_id()] != "Peace"]
            # coop_targets = [civ for civ in reachable_civs if actor.relations[civ.get_id()] != "War"]
            war_targets = reachable_civs
            coop_targets = reachable_civs

            if coop_targets:
                coop_target = choice(coop_targets)
            trade_targets = list(dict(sorted(
                            {civ: (1 - (0 if max(actor.get_culture(), civ.get_culture()) == 0 else abs(actor.get_culture() - civ.get_culture()) / max(actor.get_culture(), civ.get_culture())) + civ.get_friendliness()) 
                             for civ in coop_targets 
                             if (np.any(np.where((0 < (np.array(list(map(int, civ.get_surplus().values()))) - np.array(list(map(int, actor.get_deficit().values()))))))))
                             }.items(), key= lambda item: item[1], reverse= True)).keys())
            if trade_targets:
                trade_target = trade_targets[0]
            # Sorts a dictionary of war probability values by highest to lowest, w/ target IDs as keys.
            war_scores = dict(sorted(
                            {target.get_id(): 
                             W1_FRIENDLINESS * (1 - actor.get_friendliness()) +
                             W2_POP_PRESSURE * actor.population_pressure +
                             W3_RES_PRESSURE * actor.resource_pressure_component +
                             W4_CULT_DIFF * (0 if max(actor.get_culture(), target.get_culture()) == 0 else 
                                           abs(actor.get_culture() - target.get_culture()) / max(actor.get_culture(), target.get_culture())) 
                           for target in war_targets}.items(), key= lambda item: item[1], reverse= True))
            # Adding a dummy value at the end to avoid .index(True) raising a ValueError due to probabilistic success.
            war_positives = [random() < war_odds for war_odds in war_scores.values()]
            to_war = (True in war_positives)
            # 1) Seek war if desparate, or cooperation if not desparate.
            if actor.is_desparate:
                # Making sure a war probability triggered in case of statistical anomalies or peaceful, yet desparate individuals.
                if to_war:
                    war_target_score = war_positives.index(True)
                    # Using list_civs in order to make use of the target's ID.
                    war_target = self.civ_ids[list(war_scores.keys())[war_target_score]]
                    actor.war_initiations_this_turn += 1
                    # Determining closest planet they own to attack.
                    planet_targets = np.array([[(target, self.ranges[target][origin]) for target in war_target.get_planet_ids()] for origin in actor.get_planet_ids()])
                    planet_target = self.list_planets[int([planet_targets[0,0,0]][0])] if planet_targets.shape[0] == 1 else self.list_planets[int(planet_targets[np.argmin(planet_targets, axis= 0)[0,1], np.argmin(planet_targets, axis= 1)[0,0], 0])]
                    original_owner_civ = planet_target.get_civ() if planet_target else None
                    self.civs_war(actor, war_target, t, planet_target)
                    interactions.append({"civ1": actor, "civ2": war_target, "type": "war", "attacker": actor, "defender": war_target, "defender_target_planet_initial_pos": planet_target.get_pos() if planet_target else None})
                    civ_interaction_counts[actor.get_id()]['wars_participated'] += 1
                    civ_interaction_counts[war_target.get_id()]['wars_participated'] += 1
                    if planet_target and planet_target.get_civ() == actor and original_owner_civ == war_target:
                        conquest_events.append({"planet_id": planet_target.get_id(), 
                                                "new_owner_civ_id": actor.get_id(), 
                                                "old_owner_civ_id": war_target.get_id() if original_owner_civ else None})
            elif coop_targets:
                # Cooperate w/ a random cooperative, in-range civ.
                self.civs_cooperate(actor, coop_target)
                # print(f"\tCooperation: Civilizations {actor.get_id()} and {coop_target.get_id()} are cooperating.")
                interactions.append({"civ1": actor, "civ2": coop_target, "type": "cooperation"})
            # 2) Seek trade.
            if trade_targets:
                self.civs_trade(actor, trade_target)
                # print(f"\tTrade: Civilizations {actor.get_id()} and {trade_target.get_id()} are trading.")
                civ_interaction_counts[actor.get_id()]['trades'] += 1
                civ_interaction_counts[trade_target.get_id()]['trades'] += 1
                interactions.append({"civ1": actor, "civ2": coop_target, "type": "trade"})
            # 3) Seek cooperation if desparate, or war if not desparate.
            if actor.is_desparate and coop_targets:
                self.civs_cooperate(actor, coop_target)
                # print(f"\tCooperation: Civilizations {actor.get_id()} and {coop_target.get_id()} are cooperating.")
                interactions.append({"civ1": actor, "civ2": coop_target, "type": "cooperation"})
            else:
                if to_war:
                    war_target_score = war_positives.index(True)
                    war_target = self.civ_ids[list(war_scores.keys())[war_target_score]]
                    actor.war_initiations_this_turn += 1
                    planet_targets = np.array([[(target, self.ranges[target][origin]) for target in war_target.get_planet_ids()] for origin in actor.get_planet_ids()])
                    planet_target = self.list_planets[int([planet_targets[0,0,0]][0])] if planet_targets.shape[0] == 1 else self.list_planets[int(planet_targets[np.argmin(planet_targets, axis= 0)[0,1], np.argmin(planet_targets, axis= 1)[0,0], 0])]
                    original_owner_civ = planet_target.get_civ()
                    self.civs_war(actor, war_target, t, planet_target)
                    interactions.append({"civ1": actor, "civ2": war_target, "type": "war", "attacker": actor, "defender": war_target, "defender_target_planet_initial_pos": planet_target.get_pos() if planet_target else None})
                    civ_interaction_counts[actor.get_id()]['wars_participated'] += 1
                    civ_interaction_counts[war_target.get_id()]['wars_participated'] += 1
                    if planet_target and planet_target.get_civ() == actor and original_owner_civ == war_target:
                        conquest_events.append({"planet_id": planet_target.get_id(), 
                                                "new_owner_civ_id": actor.get_id(), 
                                                "old_owner_civ_id": war_target.get_id() if original_owner_civ else None})
        return interactions, conquest_events, civ_interaction_counts

    def interact_civs2(self, t, active_civs):
        ''' run_simulation() helper function and the civ agent decision-making hub. Runs actions for each living civ during turn t.
        Inputs:
            - t: Turn counter. Used for civ.check_if_dead() in civs_war() helper function.
            - active_civs: A list of alive civs. Civs are still checked as elimination during iterations is possible.
        Outputs:
            - interactions:             Data tracked for visualization purposes.
            - conquest_events:          Data tracked for visualization purposes.
            - civ_interaction_counts:   Data tracked for visualization purposes.
        '''
        interactions = []
        conquest_events = []
        civ_interaction_counts = {civ.get_id(): {'trades': 0, 'wars_participated': 0, 'wars_initiated': 0} for civ in active_civs if civ.get_alive()}
        civ_pairs = [(active_civs[i], active_civs[j]) for i in range(len(active_civs)) for j in range(i + 1, len(active_civs))]
        for civ1, civ2 in civ_pairs:
            if not civ1.get_alive() or not civ2.get_alive(): # Check again in case one was eliminated by an earlier pair's interaction
                continue

            if not self.can_interact(civ1, civ2) or not self.can_interact(civ2, civ1):
                continue

            interaction_details = {'civ1': civ1, 'civ2': civ2, 'type': 'none'} # Default type

            # Determine initial attacker/defender for targeting, this might be overridden by desperation/aggression
            # Let's simplify: if war happens, one will be attacker, one defender.
            # The civ with lower friendliness is more likely to be an aggressor.
            potential_aggressor = civ1 if civ1.get_friendliness() < civ2.get_friendliness() else civ2
            potential_target_civ = civ2 if potential_aggressor == civ1 else civ1

            # Determine the closest planet of potential_target_civ to potential_aggressor
            targeted_planet_object = None
            min_dist = float('inf')

            if potential_aggressor.get_planets() and potential_target_civ.get_planets():
                for p_attacker_id in potential_aggressor.get_planet_ids():
                    for p_defender_id in potential_target_civ.get_planet_ids():
                        p_attacker_obj_safe = potential_aggressor.get_planet(p_attacker_id)
                        p_defender_obj_safe = potential_target_civ.get_planet(p_defender_id)
                        if p_attacker_obj_safe and p_defender_obj_safe:
                            dist = np.sqrt((p_attacker_obj_safe.get_pos()[0] - p_defender_obj_safe.get_pos()[0])**2 + \
                                           (p_attacker_obj_safe.get_pos()[1] - p_defender_obj_safe.get_pos()[1])**2)
                            if dist < min_dist:
                                min_dist = dist
                                targeted_planet_object = p_defender_obj_safe
            
            interaction_details['defender_target_planet_initial_pos'] = targeted_planet_object.get_pos() if targeted_planet_object else None

            # Decision logic:
            declared_war_this_interaction = False # Renamed for clarity in this interaction
            actual_attacker, actual_defender = None, None

            # 1. Desperation War
            if civ1.is_desparate and not civ2.is_desparate:
                actual_attacker, actual_defender = civ1, civ2
                declared_war_this_interaction = True
            elif civ2.is_desparate and not civ1.is_desparate:
                actual_attacker, actual_defender = civ2, civ1
                declared_war_this_interaction = True
            elif civ1.is_desparate and civ2.is_desparate:
                if civ1.get_military() > civ2.get_military():
                    actual_attacker, actual_defender = civ1, civ2
                elif civ2.get_military() > civ1.get_military():
                    actual_attacker, actual_defender = civ2, civ1
                else: 
                    actual_attacker = civ1 if civ1.get_friendliness() <= civ2.get_friendliness() else civ2
                    actual_defender = civ2 if actual_attacker == civ1 else civ1
                declared_war_this_interaction = True

            if declared_war_this_interaction:
                interaction_details['type'] = 'war'
                interaction_details['attacker'] = actual_attacker
                interaction_details['defender'] = actual_defender
                actual_attacker.war_initiations_this_turn += 1 # Track initiation
                original_owner_civ = targeted_planet_object.get_civ() if targeted_planet_object else None
                self.civs_war(actual_attacker, actual_defender, t, targeted_planet_object)
                if targeted_planet_object and targeted_planet_object.get_civ() == actual_attacker and original_owner_civ == actual_defender:
                    conquest_events.append({"planet_id": targeted_planet_object.get_id(), 
                                            "new_owner_civ_id": actual_attacker.get_id(), 
                                            "old_owner_civ_id": actual_defender.get_id() if original_owner_civ else None})
            else:
                # 2. WarScore-based War (if no desperation war)
                c1_culture = civ1.get_culture()
                c2_culture = civ2.get_culture()
                # Calculate cultural difference (handle potential division by zero)
                max_c = max(c1_culture, c2_culture)
                delta_C_12 = abs(c1_culture - c2_culture) / max_c if max_c > 0.0 else 0.0

                war_score_1_attacks_2 = (W1_FRIENDLINESS * (1 - civ1.get_friendliness()) +
                                         W2_POP_PRESSURE * civ1.population_pressure +
                                         W3_RES_PRESSURE * civ1.resource_pressure_component +
                                         W4_CULT_DIFF * delta_C_12)
                
                war_score_2_attacks_1 = (W1_FRIENDLINESS * (1 - civ2.get_friendliness()) +
                                         W2_POP_PRESSURE * civ2.population_pressure +
                                         W3_RES_PRESSURE * civ2.resource_pressure_component +
                                         W4_CULT_DIFF * delta_C_12)

                civ1_triggers_warscore = (war_score_1_attacks_2 * WAR_SCORE_EFFECTIVENESS_MODIFIER) > random()
                civ2_triggers_warscore = (war_score_2_attacks_1 * WAR_SCORE_EFFECTIVENESS_MODIFIER) > random()

                potential_attacker_by_warscore = None
                potential_defender_by_warscore = None

                if civ1_triggers_warscore and civ2_triggers_warscore:
                    # Both trigger, higher score attacks
                    if war_score_1_attacks_2 >= war_score_2_attacks_1:
                        potential_attacker_by_warscore, potential_defender_by_warscore = civ1, civ2
                    else:
                        potential_attacker_by_warscore, potential_defender_by_warscore = civ2, civ1
                elif civ1_triggers_warscore:
                    potential_attacker_by_warscore, potential_defender_by_warscore = civ1, civ2
                elif civ2_triggers_warscore:
                    potential_attacker_by_warscore, potential_defender_by_warscore = civ2, civ1
                
                if potential_attacker_by_warscore:
                    actual_attacker, actual_defender = potential_attacker_by_warscore, potential_defender_by_warscore
                    declared_war_this_interaction = True
                    interaction_details['type'] = 'war'
                    interaction_details['attacker'] = actual_attacker
                    interaction_details['defender'] = actual_defender
                    actual_attacker.war_initiations_this_turn += 1 # Track initiation
                    attacker_score_display = war_score_1_attacks_2 if actual_attacker == civ1 else war_score_2_attacks_1
                    original_owner_civ = targeted_planet_object.get_civ() if targeted_planet_object else None
                    self.civs_war(actual_attacker, actual_defender, t, targeted_planet_object)
                    if targeted_planet_object and targeted_planet_object.get_civ() == actual_attacker and original_owner_civ == actual_defender:
                        conquest_events.append({"planet_id": targeted_planet_object.get_id(), 
                                                "new_owner_civ_id": actual_attacker.get_id(), 
                                                "old_owner_civ_id": actual_defender.get_id() if original_owner_civ else None})
                else:
                    # 3. Cooperation (if no desperation or WarScore war)
                    if civ1.get_friendliness() == 1 and civ2.get_friendliness() == 1:
                        interaction_details['type'] = 'cooperation'
                        self.civs_cooperate(civ1, civ2)
                    # 4. Low-Friendliness Aggression War (if no other war or cooperation)
                    elif civ1.get_friendliness() < AGGRESSION_FRIENDLINESS_THRESHOLD or civ2.get_friendliness() < AGGRESSION_FRIENDLINESS_THRESHOLD:
                        interaction_details['type'] = 'war'
                        civ1_is_aggressor_candidate = civ1.get_friendliness() < AGGRESSION_FRIENDLINESS_THRESHOLD
                        civ2_is_aggressor_candidate = civ2.get_friendliness() < AGGRESSION_FRIENDLINESS_THRESHOLD

                        if civ1_is_aggressor_candidate and not civ2_is_aggressor_candidate:
                            actual_attacker, actual_defender = civ1, civ2
                        elif not civ1_is_aggressor_candidate and civ2_is_aggressor_candidate:
                            actual_attacker, actual_defender = civ2, civ1
                        elif civ1_is_aggressor_candidate and civ2_is_aggressor_candidate:
                            actual_attacker = civ1 if civ1.get_friendliness() <= civ2.get_friendliness() else civ2
                            actual_defender = civ2 if actual_attacker == civ1 else civ1
                        # No 'else' needed here as the outer 'elif' ensures one of them is below threshold.
                        
                        interaction_details['attacker'] = actual_attacker
                        interaction_details['defender'] = actual_defender
                        actual_attacker.war_initiations_this_turn += 1 # Track initiation
                        original_owner_civ = targeted_planet_object.get_civ() if targeted_planet_object else None
                        self.civs_war(actual_attacker, actual_defender, t, targeted_planet_object)
                        if targeted_planet_object and targeted_planet_object.get_civ() == actual_attacker and original_owner_civ == actual_defender:
                             conquest_events.append({"planet_id": targeted_planet_object.get_id(), 
                                                     "new_owner_civ_id": actual_attacker.get_id(), 
                                                     "old_owner_civ_id": actual_defender.get_id() if original_owner_civ else None})
                    # 5. Trade (if nothing else)
                    else: 
                        interaction_details['type'] = 'trade'
                        self.civs_trade(civ1, civ2)
            
            if interaction_details['type'] != 'none':
                interactions.append(interaction_details)
                # Update civ interaction counts
                if interaction_details['type'] == 'trade':
                    if civ1.get_id() in civ_interaction_counts: civ_interaction_counts[civ1.get_id()]['trades'] += 1
                    if civ2.get_id() in civ_interaction_counts: civ_interaction_counts[civ2.get_id()]['trades'] += 1
                elif interaction_details['type'] == 'war':
                    attacker = interaction_details.get('attacker')
                    defender = interaction_details.get('defender')
                    if attacker and attacker.get_id() in civ_interaction_counts:
                        civ_interaction_counts[attacker.get_id()]['wars_participated'] += 1
                    if defender and defender.get_id() in civ_interaction_counts:
                        civ_interaction_counts[defender.get_id()]['wars_participated'] += 1
                
        return interactions, conquest_events, civ_interaction_counts

    def run_simulation(self):
        ''' Main simulation function. Utilizes a series of helper functions and agent methods to simulate interplanetary civilizations' interactions.
        Inputs:
            - None. All necessary modifications are made when a 'Model' object is initialized.
        Outputs:
            - message: Used for printing simulation results.
            - t: Used to check if civs have been eliminated in the turn at the time of the check.
            - interactions:     Data tracked for visualization purposes.
            - conquest_events:  Data tracked for visualization purposes.
        '''
        # Preparing Simulation-specific Variables.
        t = 0
        Civ.instances = list(self.list_civs)
        # Running Simulation.
        while t < self.max_turns:
            # 0) Turn Increment:
            t += 1
            # print(f"Turn {t}:")
            # 1) Updating Attributes:       
            for civ_idx in range(len(self.list_civs) -1, -1, -1): # Iterate backwards for safe removal
                civ = self.list_civs[civ_idx]
                if not civ.get_alive(): # Should not happen if removal is correct, but as safeguard
                    if civ in self.list_civs: # Check if it's still in the list before trying to remove
                         self.list_civs.pop(civ_idx)
                    continue
                civ.update_attributes()
                if civ.has_won_culture_victory:
                    message = f"\tCivilization {civ.get_id()} has achieved a culture victory!"
                    # Yield message multiple times for display duration
                    yield message, [], [] # Match tuple structure
                    yield message, [], []
                    yield message, [], []
                    # Collect data for the turn of victory, interactions for this turn haven't happened yet.
                    self._collect_historical_data(t, [], {}, is_final_turn=True, final_message=message) 
                    self.generate_all_plots()
                    self.end_type = "Culture"
                    return # End simulation due to culture victory.
            # 2) Civ Interactions:
            active_civs_for_interaction = [civ for civ in self.list_civs if civ.get_alive()]
            if not active_civs_for_interaction: # All civs might have been eliminated before interactions
                message = "\tAll civilizations are eliminated before interactions this turn."
                # print(message)
                self._collect_historical_data(t, [], {}, is_final_turn=True, final_message=message)
                yield message, [], [] 
                self.generate_all_plots()
                self.end_type = "Stalemate"
                return
            
            for civ_obj in active_civs_for_interaction: # Use the snapshot
                civ_obj.reset_turn_counters()

            interactions, conquest_events, civ_interaction_counts = self.interact_civs(t, active_civs_for_interaction) 
            
            self._collect_historical_data(t, interactions, civ_interaction_counts)
            yield t, interactions, conquest_events
            
            # 3) Check End Conditions (after interactions):
            current_alive_civs = [civ for civ in self.list_civs if civ.get_alive()]
            if len(current_alive_civs) == 1:
                winner_civ = current_alive_civs[0]
                message = f"\tCivilization {winner_civ.get_id()} has won the simulation through military!"
                # print(message) 
                self._collect_historical_data(t, interactions, civ_interaction_counts, is_final_turn=True, final_message=message) # Collect final data
                yield message, [], []
                self.generate_all_plots()
                self.end_type = "Military"
                return
            
            for civ in current_alive_civs: 
                if civ.has_won_culture_victory:
                    message = f"\tCivilization {civ.get_id()} has achieved a culture victory!"
                    # print(message)
                    # Data for this turn was already collected, but we mark it as final for this civ's win
                    self._collect_historical_data(t, interactions, civ_interaction_counts, is_final_turn=True, final_message=message)
                    yield message, [], []
                    self.generate_all_plots()
                    self.end_type = "Culture"
                    return

            if not current_alive_civs:
                message = "\tAll civilizations have been eliminated."
                # print(message)
                self._collect_historical_data(t, interactions, civ_interaction_counts, is_final_turn=True, final_message=message)
                yield message, [], []
                self.generate_sim_log()
                self.generate_all_plots()
                self.end_type = "Stalemate"
                return

    def _collect_historical_data(self, turn, interactions, civ_interaction_counts_from_interact, is_final_turn=False, final_message=None):
        ''' Helper function to channel data from run_simulation() to visualize.py's functions.
        Inputs:
            - turn: Positive integer representing number of time steps that have passed for this phase of the simulation.
            - interactions: A list of civ interaction dictionaries.
            - civ_interaction_counts_from_interact: A list of civ dictionaries tracking how many times that civ did specific interactions.
            - is_final_turn: Default = False. Only altered when collecting data during end conditions.
            - final_message: A string value used to present the type of end condition.
        Outputs:
            - None. Appends a snapshot of this turn's interactions to the calling 'Model' object's historical_data list parameter.
        '''
        turn_civ_data = {}
        current_civ_map = {c.get_id(): c for c in self.list_civs} # Civs currently active

        for civ_id_iter in self.all_initial_civ_ids: # Use the stored set of all initial civ IDs
            civ = current_civ_map.get(civ_id_iter)
            if civ: # Civ is currently active in self.list_civs
                status = 'active'
                num_trade_partners = civ_interaction_counts_from_interact.get(civ.get_id(), {}).get('trades', 0)
                wars_participated = civ_interaction_counts_from_interact.get(civ.get_id(), {}).get('wars_participated', 0)
                is_at_war_this_turn = wars_participated > 0
                
                demand = civ.get_demand()
                surplus = civ.get_surplus()
                deficit = civ.get_deficit()

                turn_civ_data[civ.get_id()] = {
                    'population': civ.get_population(),
                    'tech': civ.get_tech(),
                    'military': civ.get_military(),
                    'culture': civ.get_culture(),
                    'friendliness': civ.get_friendliness(),
                    'status': status,
                    'victories': civ.victories,
                    'population_pressure': civ.population_pressure,
                    'food_pressure': civ.food_pressure,
                    'energy_pressure': civ.energy_pressure,
                    'minerals_pressure': civ.minerals_pressure,
                    'war_initiations': civ.war_initiations_this_turn,
                    'food_stock': civ.resources.get('food', 0),
                    'energy_stock': civ.resources.get('energy', 0),
                    'minerals_stock': civ.resources.get('minerals', 0),
                    'num_trade_partners': num_trade_partners,
                    'is_at_war': is_at_war_this_turn,
                    'desperation': civ.is_desparate,
                    'desperation_value': civ.desperation,
                    'planets_owned': len(civ.get_planets()),
                    'total_demand_food': demand.get('food', 0),
                    'total_demand_energy': demand.get('energy', 0),
                    'total_demand_minerals': demand.get('minerals', 0),
                    'total_surplus_food': surplus.get('food', 0),
                    'total_surplus_energy': surplus.get('energy', 0),
                    'total_surplus_minerals': surplus.get('minerals', 0),
                    'total_deficit_food': deficit.get('food', 0),
                    'total_deficit_energy': deficit.get('energy', 0),
                    'total_deficit_minerals': deficit.get('minerals', 0),
                }
            else: # Civ was eliminated or not in self.list_civs for current turn
                # Provide a basic entry indicating elimination.
                # Plotting functions should check 'status'
                turn_civ_data[civ_id_iter] = {'status': 'eliminated', 'civ_id': civ_id_iter}
                # Add default zero/empty values for other keys H1/H6 might try to access for eliminated civs
                # to prevent KeyErrors in plotting if it doesn't guard well.
                attributes_for_eliminated = [
                    'population', 'tech', 'military', 'culture', 'friendliness', 
                    'victories', 'population_pressure', 'food_pressure', 'energy_pressure', 
                    'minerals_pressure', 'war_initiations', 'food_stock',
                    'energy_stock', 'minerals_stock', 'num_trade_partners', 'is_at_war', 
                    'desperation', 'planets_owned', 'total_demand_food', 'total_demand_energy', 
                    'total_demand_minerals', 'total_surplus_food', 'total_surplus_energy', 
                    'total_surplus_minerals', 'total_deficit_food', 'total_deficit_energy', 
                    'total_deficit_minerals'
                ]
                for attr in attributes_for_eliminated:
                    turn_civ_data[civ_id_iter][attr] = 0 # Or appropriate default (e.g., 0.0 for floats, False for bools)

        turn_relations_data = {}
        # Cultural similarity calculation needs access to Civ objects by ID.
        # Using Civ.instances was a previous approach. A safer way is to use the civ objects
        # involved in the 'interactions' list directly if they are passed as objects.
        # The 'interactions' list from 'interact_civs' contains civ1, civ2 as objects.

        for interaction in interactions:
            civ1_obj = interaction.get('civ1') 
            civ2_obj = interaction.get('civ2')

            if civ1_obj and civ2_obj: # Ensure both objects are present
                c1_id = civ1_obj.get_id()
                c2_id = civ2_obj.get_id()
                pair_key = tuple(sorted((c1_id, c2_id)))
                
                c1_culture = civ1_obj.get_culture()
                c2_culture = civ2_obj.get_culture()

                cultural_sim = 0.0
                if c1_culture == c2_culture:
                    cultural_sim = 1.0
                else:
                    max_culture = max(float(c1_culture), float(c2_culture)) # Ensure float for division
                    if max_culture == 0: 
                        cultural_sim = 1.0
                    else:
                        cultural_sim = 1.0 - abs(float(c1_culture) - float(c2_culture)) / max_culture
                
                turn_relations_data[pair_key] = {
                    'type': interaction.get('type', 'unknown'),
                    'cultural_similarity': cultural_sim
                }
        
        snapshot = {
            'turn': turn,
            'civ_data': turn_civ_data,
            'relations_data': turn_relations_data
        }
        if is_final_turn and final_message:
            snapshot['final_message'] = final_message

        self.historical_data.append(snapshot)

    def generate_sim_log(self):
        ''' Writes a .txt file to the current directory, storing all historical_data from a simulation.
        Inputs:
            - None. Uses self.historical_data. Can be toggled by LOG_TOGGLE in this file's constants table.
        Outputs:
            - None. Writes a .txt file in the same directory that stores historical data.
        '''
        if not LOG_TOGGLE:
            return
        if not self.historical_data:
            # print("No historical data to plot.")
            return
        time_of_creation = datetime.now().strftime("%Y-%m-%d_%I-%M-%S%p")
        ideal_file_name = f"output/logs/Civ_Sim_log_{time_of_creation}.json"
        # In case of multiple sim_logs generated in the same second,..
        if os.path.exists(ideal_file_name):
            # Number this new entry,..
            counter = 2
            while os.path.exists(ideal_file_name):
                # And go until that number creates a fresh entry.
                ideal_file_name = f"output/logs/Civ_Sim_log_{time_of_creation}_{counter}.txt"
                counter += 1
        final_file_name = os.path.join(os.path.dirname(__file__), ideal_file_name)
        with open(final_file_name, "at") as log:
            log.write(str(self.historical_data))
        # print(f"Log \"{ideal_file_name}\" has been written!")

    def generate_all_plots(self):
        '''
        Inputs:
            - None. Utilizes the calling 'Model' object's historical_data parameter as the input data for the generated plots.
              Boolean constants are used to toggle generate_all_plots()'s call, as well as individual calls w/in the function.
        Outputs:
            - Writes plots tied to our V&V sources in output/plots.
        '''
        # If all plots are toggled off, skip plot writing process.
        if not self.generate_plots_controller or (self.generate_plots_controller and not np.any([PLOT_H1, PLOT_H2, PLOT_H3, PLOT_H4, PLOT_H5, PLOT_H6])):
            return
        if not self.historical_data:
            # print("No historical data to plot.")
            return
        output_dir = "output/plots"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # print(f"\nGenerating plots in {output_dir}...")
        # H1: Resource/Desperation Dynamics Leading to Conflict/Trade
        if PLOT_H1:
            plotting.generate_h1_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h1_"))
        # H2: Military Buildup and Conflict Escalation
        if PLOT_H2:
            plotting.generate_h2_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h2_"))
        # H3: Friendliness, Cooperation, and Cultural Exchange
        if PLOT_H3:
            plotting.generate_h3_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h3_"))
        # H4: Cultural Similarity and Interaction Choice (Network Graph for last turn)
        # The plotting function takes snapshot_turn=-1 to use the last turn by default.
        if PLOT_H4:
            plotting.generate_h4_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h4_"))
        # H5: Tech Advancement, Resource Needs, and Trade/Conflict Propensity (Scatter plots)
        if PLOT_H5:
            plotting.generate_h5_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h5_"))
        # H6: Civilization Lifespans and Victory Conditions
        if PLOT_H6:
            plotting.generate_h6_plots(self.historical_data, save_path_prefix=os.path.join(output_dir, "h6_"))
        # print("Plot generation complete.")

def log_to_plots(file_name):
    ''' Evaluates a civ_sim_log.txt file to write plots.
    Inputs:
        - None. Uses a dummy 'Model' object to write in historical_data.
    '''
    file_name = "".join("output/logs", file_name) if not file_name.startswith("output/logs") else file_name
    file_name = os.path.join(os.path.dirname(__file__), file_name)
    if not os.path.exists(file_name):
        raise FileExistsError(f"\"{file_name}\" does not exist.")
    data = eval(open(file_name).read())
    if not data:
        # print("No historical data to plot.")
        return
    output_dir = "output/plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # print(f"\nGenerating plots in {output_dir}...")
    # H1: Resource/Desperation Dynamics Leading to Conflict/Trade
    if PLOT_H1:
        plotting.generate_h1_plots(data, save_path_prefix=os.path.join(output_dir, "h1_"))
    # H2: Military Buildup and Conflict Escalation
    if PLOT_H2:
        plotting.generate_h2_plots(data, save_path_prefix=os.path.join(output_dir, "h2_"))
    # H3: Friendliness, Cooperation, and Cultural Exchange
    if PLOT_H3:
        plotting.generate_h3_plots(data, save_path_prefix=os.path.join(output_dir, "h3_"))
    # H4: Cultural Similarity and Interaction Choice (Network Graph for last turn)
    # The plotting function takes snapshot_turn=-1 to use the last turn by default.
    if PLOT_H4:
        plotting.generate_h4_plots(data, save_path_prefix=os.path.join(output_dir, "h4_"))
    # H5: Tech Advancement, Resource Needs, and Trade/Conflict Propensity (Scatter plots)
    if PLOT_H5:
        plotting.generate_h5_plots(data, save_path_prefix=os.path.join(output_dir, "h5_"))
    # H6: Civilization Lifespans and Victory Conditions
    if PLOT_H6:
        plotting.generate_h6_plots(data, save_path_prefix=os.path.join(output_dir, "h6_"))
    # print("Plot generation complete.")
