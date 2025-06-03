##### DEPDENDENCIES #####
import numpy as np
import random
from random import sample
from civ import Civ
from planet import Planet
from collections import Counter



##### USER-ADJUSTABLE #####
# SCENARIO RANGE CONSTRAINTS:
MIN_PLANETS = 3                 # Inclusive lower bound integer for accepted range of planet count.
MAX_PLANETS = 30                # Inclusive higher bound integer for accepted range of planet count.
MIN_GRID_HEIGHT = 5             # Inclusive lower bound integer determining minimum grid height (y dimension).
MIN_GRID_WIDTH = 5              # Inclusive lower bound integer determining minimum grid width (x dimension).
MAX_GRID_HEIGHT = 50            # Inclusive higher bound integer determining maximum grid height (y dimension).
MAX_GRID_WIDTH = 50             # Inclusive higher bound integer determining maximum grid width (x dimension).
# INTERACTION MODIFIERS:
WAR_WIN_BOOST = 2               # Value of tech and military boost for winning a war.
COOPERATION_BOOST = 1           # Value of tech and culture boost for cooperating with another civ.
WAR_PENALTY = 1                 # Value of tech and culture penalty for an attacker losing a war.
TRADE_TECH_BOOST = 1            # Tech increase when a civ trades w/o receiving resources in return.



##### CLASSES #####
class Model():
    def __init__(self, num_planets, grid_height, grid_width):
        ''' Model class constructor that creates a numpy array for a grid, with lists for civ agents and planet agents assigned to the civ agents.
        Inputs:
        - num_planets:  The # of planets to be used. Each planet is assigned to 1 civ, such that every civ has 1 planet, and vice versa.
        - grid_height: How tall to make the grid. Recommended to maintain equality with grid_width to stabilize simulation consistency.
        - grid_width: How wide to make the grid. Recommended to maintain equality with grid_height to stabilize simulation consistency.
        Output:
            - A Model object with attributes for the number of agents, a numpy array grid, and an array of distances between planet agents.
        '''
        # Initializing model constants and model resources.
        self.num_planets = max(MIN_PLANETS, min(num_planets, MAX_PLANETS))  # Applying range constraint to input 'num_planets'
        self.grid = np.zeros(shape= (max(MIN_GRID_HEIGHT, min(grid_height, MAX_GRID_HEIGHT)), max(MIN_GRID_WIDTH, min(grid_width, MAX_GRID_WIDTH))))
        self.list_planets = []
        self.list_civs = [Civ() for i in range(num_planets)]
        self.assign_planets()
        self.ranges = self.distances()
        relations = [[{"Trade": False, "War": False}] * len(self.list_civs) for i in range(len(self.list_civs))]

    def assign_planets(self):
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
            self.list_planets.append(Planet(random_available_coord[0], random_available_coord[1]))
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
        return np.any([[self.ranges[p1.get_id()][p2.get_id()] < civ1.tech for p1 in civ1.get_planets().values()] for p2 in civ2.get_planets().values()])
    
    def civs_cooperate(self, civ1, civ2):
        civ1.tech +=            COOPERATION_BOOST
        civ2.tech +=            COOPERATION_BOOST
        civ1.culture +=         COOPERATION_BOOST
        civ2.culture +=         COOPERATION_BOOST

    def civs_war(self, attacker, defender, t, targeted_planet): # actual_attacker, actual_defender, targeted_planet are passed directly
        print(f"\tCiv {attacker.get_id()} is attacking Civ {defender.get_id()}, targeting planet {targeted_planet.get_id() if targeted_planet else 'N/A'}.")

        # Tech gives a bonus to combat effectiveness
        attacker_power = attacker.get_military() * (1 + (0.1 * attacker.get_tech()))
        defender_power = defender.get_military() * (1 + (0.1 * defender.get_tech()))

        total_combat_power = attacker_power + defender_power

        if total_combat_power == 0: # Stalemate if both have zero power
            print(f"\tStalemate between Civ {attacker.get_id()} and Civ {defender.get_id()} due to zero combat power.")
            return # No changes in this case

        attacker_win_chance = attacker_power / total_combat_power

        if random.random() < attacker_win_chance:
            # Attacker wins
            print(f"\tAttacker Civ {attacker.get_id()} wins against Civ {defender.get_id()}!")
            attacker.military += WAR_WIN_BOOST # Attacker gets military boost
            attacker.tech += WAR_WIN_BOOST     # Attacker gets tech boost

            # Attacker conquers the specific targeted planet, if it's valid and still owned by the defender.
            if targeted_planet and targeted_planet.get_civ() == defender:
                print(f"\tCiv {attacker.get_id()} conquers planet {targeted_planet.get_id()} from Civ {defender.get_id()}.")
                targeted_planet.assign_civ(attacker) # Planet changes owner
                
                # Check if defender is eliminated after losing the planet
                if defender.check_if_dead(t):
                    print(f"\tCiv {defender.get_id()} has been eliminated by Civ {attacker.get_id()}.")
                    self.list_civs.remove(defender)
            elif targeted_planet and targeted_planet.get_civ() != defender:
                 print(f"\tTargeted planet {targeted_planet.get_id()} is no longer owned by defender Civ {defender.get_id()}. No conquest from this battle.")
            elif not targeted_planet:
                print(f"\tDefender Civ {defender.get_id()} had no specific planet targeted (e.g. no planets left to target). No conquest from this battle.")
        else:
            # Defender wins (Attacker loses the battle)
            print(f"\tDefender Civ {defender.get_id()} wins the battle against attacker Civ {attacker.get_id()}!")
            defender.military += WAR_WIN_BOOST # Defender gets military boost
            defender.tech += WAR_WIN_BOOST     # Defender gets tech boost
            defender.culture += WAR_WIN_BOOST  # Defender gets culture boost

            # Attacker takes a hit to tech and culture for the failed attack
            attacker.tech = max(0, attacker.tech - WAR_PENALTY)
            attacker.culture = max(0, attacker.culture - WAR_PENALTY)
            print(f"\tAttacker Civ {attacker.get_id()} loses {WAR_PENALTY} tech and culture due to failed attack.")
            # No planets change hands if the defender wins the battle.

    def civs_trade(self, civ1, civ2):
        resource_keys = ["energy", "food", "minerals"] # Define standard resource keys

        civ1_surplus = civ1.get_surplus()
        civ1_deficit = civ1.get_deficit() # Deficit represents demand for civ1
        civ2_surplus = civ2.get_surplus()
        civ2_deficit = civ2.get_deficit() # Deficit represents demand for civ2

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
        amt_to_trade = flow_from_civ2_to_civ1 - flow_from_civ1_to_civ2

        # Exchanging resources
        civ1.resources = dict(Counter(civ1.resources) + amt_to_trade)
        civ2.resources = dict(Counter(civ2.resources) - amt_to_trade) # If civ1 gains, civ2 loses (-amt_to_trade)

        # Tech boost logic:
        # Civ2 gets a tech boost if it was a net giver of resources and received less or nothing in return.
        # i.e., the total value of resources civ2 gave to civ1 is greater than what civ1 gave to civ2.
        
        # Total value civ2 gave to civ1 (sum of positive values in amt_to_trade from civ1's perspective)
        value_civ2_gave_to_civ1 = sum(v for k, v in amt_to_trade.items() if v > 0)
        # Total value civ1 gave to civ2 (sum of absolute values of negative values in amt_to_trade from civ1's perspective)
        value_civ1_gave_to_civ2 = sum(-v for k, v in amt_to_trade.items() if v < 0)

        if value_civ2_gave_to_civ1 > value_civ1_gave_to_civ2:
            # Civ2 was a net giver in the trade
            print(f"\tCiv {civ2.get_id()} gets a tech boost from trade with Civ {civ1.get_id()}.")
            civ2.tech += TRADE_TECH_BOOST
        elif value_civ1_gave_to_civ2 > value_civ2_gave_to_civ1:
            # Civ1 was a net giver in the trade (symmetrical boost if desired)
            print(f"\tCiv {civ1.get_id()} gets a tech boost from trade with Civ {civ2.get_id()}.")
            civ1.tech += TRADE_TECH_BOOST
            
    def interact_civs(self, t): # Added turn 't'
        interactions = []
        conquest_events = []
        
        # Create a list of civs that are still alive to prevent errors if a civ is eliminated mid-loop
        active_civs = [civ for civ in self.list_civs if civ.get_alive()]
        civ_pairs = []
        for i in range(len(active_civs)):
            for j in range(i + 1, len(active_civs)):
                civ_pairs.append((active_civs[i], active_civs[j]))

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
                        # Robust way to get planet objects:
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
            # 1. Desperation: If either civ is desperate, war is more likely.
            #    If civ1 is desperate, it considers attacking civ2.
            #    If civ2 is desperate, it considers attacking civ1.
            #    If both are desperate, the one with lower friendliness (more inherently aggressive) or higher military might attack.
            
            declared_war = False
            actual_attacker, actual_defender = None, None

            if civ1.is_desparate and not civ2.is_desparate:
                actual_attacker, actual_defender = civ1, civ2
                declared_war = True
            elif civ2.is_desparate and not civ1.is_desparate:
                actual_attacker, actual_defender = civ2, civ1
                declared_war = True
            elif civ1.is_desparate and civ2.is_desparate:
                # Both desperate, let the one with higher military attack, or lower friendliness if equal military
                if civ1.get_military() > civ2.get_military():
                    actual_attacker, actual_defender = civ1, civ2
                elif civ2.get_military() > civ1.get_military():
                    actual_attacker, actual_defender = civ2, civ1
                else: # Equal military, use friendliness
                    actual_attacker = civ1 if civ1.get_friendliness() <= civ2.get_friendliness() else civ2
                    actual_defender = civ2 if actual_attacker == civ1 else civ1
                declared_war = True

            if declared_war:
                interaction_details['type'] = 'war'
                interaction_details['attacker'] = actual_attacker
                interaction_details['defender'] = actual_defender
                # Use the pre-calculated targeted_planet_object (closest planet of the defender to the attacker)
                print(f"\tDesperation War: Civ {actual_attacker.get_id()} (Attacker) vs Civ {actual_defender.get_id()} (Defender). Target: P-{targeted_planet_object.get_id() if targeted_planet_object else 'None'}")
                # Store original owner for conquest event
                original_owner_civ = targeted_planet_object.get_civ() if targeted_planet_object else None
                self.civs_war(actual_attacker, actual_defender, t, targeted_planet_object)
                if targeted_planet_object and targeted_planet_object.get_civ() == actual_attacker and original_owner_civ == actual_defender:
                    conquest_events.append({"planet_id": targeted_planet_object.get_id(), 
                                            "new_owner_civ_id": actual_attacker.get_id(), 
                                            "old_owner_civ_id": actual_defender.get_id() if original_owner_civ else None}) # actual_defender was original_owner_civ

            # 2. Friendliness-based interaction (if no desperation war occurred)
            else:
                if civ1.get_friendliness() == 1 and civ2.get_friendliness() == 1:
                    interaction_details['type'] = 'cooperation'
                    print(f"\tCooperation: Civilizations {civ1.get_id()} and {civ2.get_id()} are cooperating.")
                    self.civs_cooperate(civ1, civ2)
                elif civ1.get_friendliness() == 0 or civ2.get_friendliness() == 0: # At least one is maximally unfriendly
                    interaction_details['type'] = 'war'
                    if civ1.get_friendliness() == 0 and civ2.get_friendliness() < 1: # Civ1 is aggressor
                        actual_attacker, actual_defender = civ1, civ2
                    elif civ2.get_friendliness() == 0 and civ1.get_friendliness() < 1: # Civ2 is aggressor
                        actual_attacker, actual_defender = civ2, civ1
                    else: # Both are 0 friendliness, or one is 0 and other is 1 (edge case not fully covered by above)
                          # If civ1 is 0 and civ2 is 1, civ1 attacks. If civ2 is 0 and civ1 is 1, civ2 attacks.
                          # If both are 0, decide based on military or ID (civ1 attacks for now)
                        actual_attacker = civ1 if civ1.get_friendliness() <= civ2.get_friendliness() else civ2
                        actual_defender = civ2 if actual_attacker == civ1 else civ1
                    
                    interaction_details['attacker'] = actual_attacker
                    interaction_details['defender'] = actual_defender
                    # Use the pre-calculated targeted_planet_object for this war too
                    print(f"\tAggression War: Civ {actual_attacker.get_id()} (Attacker) vs Civ {actual_defender.get_id()} (Defender). Target: P-{targeted_planet_object.get_id() if targeted_planet_object else 'None'}")
                    original_owner_civ = targeted_planet_object.get_civ() if targeted_planet_object else None
                    self.civs_war(actual_attacker, actual_defender, t, targeted_planet_object)
                    if targeted_planet_object and targeted_planet_object.get_civ() == actual_attacker and original_owner_civ == actual_defender:
                         conquest_events.append({"planet_id": targeted_planet_object.get_id(), 
                                                 "new_owner_civ_id": actual_attacker.get_id(), 
                                                 "old_owner_civ_id": actual_defender.get_id() if original_owner_civ else None})
                else: # Neither full cooperation nor full aggression/desperation -> opportunity for trade
                    interaction_details['type'] = 'trade'
                    print(f"\tTrade: Civilizations {civ1.get_id()} and {civ2.get_id()} are trading.")
                    self.civs_trade(civ1, civ2)
            
            if interaction_details['type'] != 'none':
                interactions.append(interaction_details)
                
        return interactions, conquest_events

    def run_simulation(self):
        t = 0
        while True:
            # 0) Turn Increment:
            t += 1
            print(f"Turn {t}:")
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
                    return # Stop simulation
                
                # Check if civ died during its own attribute update (e.g. starvation, internal collapse - not explicitly modeled yet but good place)
                # Or if it was eliminated by a previous interaction this turn but list_civs hasn't been fully updated yet.
                # The main check_if_dead happens in civs_war. If a civ is eliminated, it's removed from self.list_civs there.
                # This loop structure needs to be careful about modifying self.list_civs while iterating.
                # Iterating backwards is safer for pop/remove.
                # `civ.check_if_dead(t)` is called within `civs_war` and handles removal from `self.list_civs`.


            # 2) Civ Interactions:
            # Make sure to use a list of civs that are confirmed alive before starting interactions
            # interact_civs itself now iterates over a snapshot of active_civs
            if not self.list_civs: # All civs might have been eliminated by culture victories or other means
                message = "\tAll civilizations have been eliminated (or only one remains due to culture victory)."
                yield message, [], []
                yield message, [], []
                yield message, [], []
                return

            interactions, conquest_events = self.interact_civs(t) # Corrected: removed self.list_civs
            yield t, interactions, conquest_events
            
            # 3) Check End Conditions (after interactions):
            # Filter out non-alive civs from self.list_civs more definitively here if not handled perfectly elsewhere
            # self.list_civs = [civ for civ in self.list_civs if civ.get_alive()] # This ensures list_civs is clean
            
            # A civ might be eliminated during interactions and removed from self.list_civs by civs_war.
            # Check for military victory
            if len(self.list_civs) == 1 and self.list_civs[0].get_alive(): # Ensure the last one is actually alive
                message = f"\tCivilization {self.list_civs[0].get_id()} has won the simulation through military!"
                print(message) # Console print for military victory
                yield message, [], [] # Match tuple structure
                yield message, [], []
                yield message, [], []
                return
            
            # Check for culture victory (again, in case an interaction triggered it, though primary check is in attribute update)
            # This specific check might be redundant if the one in attribute update loop is comprehensive and returns.
            # However, if a civ achieves culture victory and then gets eliminated in the same turn's interactions before its victory is processed:
            for civ in self.list_civs: # Iterate over potentially updated list
                if civ.has_won_culture_victory:
                    #This civ might have been set to has_won_culture_victory but not yet returned from the simulation
                    message = f"\tCivilization {civ.get_id()} has achieved a culture victory!"
                    yield message, [], []
                    yield message, [], []
                    yield message, [], []
                    return

            if not self.list_civs: # All civs eliminated
                message = "\tAll civilizations have been eliminated."
                print(message) # Console print for all civilizations eliminated
                yield message, [], [] # Match tuple structure
                yield message, [], []
                yield message, [], []
                return
