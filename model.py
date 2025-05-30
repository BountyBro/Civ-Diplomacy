##### DEPDENDENCIES #####
import numpy as np
from random import sample
import random
import visualize as vis
from civ import Civ, proclaim_culture_victory
from planet import Planet



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

    def interact_civs(self, t): # Added turn 't'
        interactions = [] 
        for i, civ1 in enumerate(self.list_civs):
            if not civ1.alive:
                continue
            for j, civ2 in enumerate(self.list_civs):
                if i >= j or not civ2.alive:
                    continue

                if self.can_interact(civ1, civ2) and self.can_interact(civ2, civ1):
                    interaction_details = {'civ1': civ1, 'civ2': civ2} # Base details

                    if civ1.get_friendly() == 1 and civ2.get_friendly() == 1:
                        interaction_details['type'] = 'cooperation'
                        print(f"\tCivilizations {civ1.get_id()} and {civ2.get_id()} are cooperating.")
                        self.civs_cooperate(civ1, civ2)
                    elif civ1.get_friendly() == 0 or civ2.get_friendly() == 0:
                        interaction_details['type'] = 'war'
                        # Determine the actual attacker and defender for this war interaction
                        actual_attacker, actual_defender = None, None
                        if civ1.get_friendly() == 0 and civ2.get_friendly() == 1: # civ1 aggressive, civ2 friendly
                            actual_attacker = civ1
                            actual_defender = civ2
                        elif civ2.get_friendly() == 0 and civ1.get_friendly() == 1: # civ2 aggressive, civ1 friendly
                            actual_attacker = civ2
                            actual_defender = civ1
                        elif civ1.get_friendly() == 0 and civ2.get_friendly() == 0: # both aggressive
                            # If both are aggressive, decide who attacks. For now, simple random choice or based on ID.
                            # Let's make the one with lower ID the attacker for predictability in this case.
                            if civ1.get_id() < civ2.get_id():
                                actual_attacker = civ1
                                actual_defender = civ2
                            else:
                                actual_attacker = civ2
                                actual_defender = civ1
                        else: # This case (both friendly but war determined) should be rare/avoided by earlier logic.
                              # Default to civ1 attacking civ2 if it somehow occurs.
                            actual_attacker = civ1
                            actual_defender = civ2
                        
                        interaction_details['attacker'] = actual_attacker # For visualization arrow
                        interaction_details['defender'] = actual_defender # For visualization context

                        # Determine the specific planet of the defender that is being targeted
                        defender_target_planet_object = None
                        defender_planets_list = list(actual_defender.get_planets().values())
                        if defender_planets_list:
                            # For simplicity, still targeting the first planet of the defender.
                            # This could be made more sophisticated (e.g., closest, weakest, etc.)
                            defender_target_planet_object = defender_planets_list[0]
                            interaction_details['defender_target_planet_initial_pos'] = defender_target_planet_object.get_pos()
                        else:
                            interaction_details['defender_target_planet_initial_pos'] = None 

                        print(f"\tWar: Civ {actual_attacker.get_id()} (Attacker) vs Civ {actual_defender.get_id()} (Defender). Target: P-{defender_target_planet_object.get_id() if defender_target_planet_object else 'None'}")
                        self.civs_war(actual_attacker, actual_defender, t, defender_target_planet_object)
                    
                    interactions.append(interaction_details)
        return interactions

    def run_simulation(self):
        t = 0
        while True:
            t += 1
            print(f"Turn {t}:")            
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

            interactions = self.interact_civs(t) # Pass turn 't'
            yield t, interactions

            alive_civs = [civ for civ in self.list_civs if civ.alive]
            if len(alive_civs) == 1:
                message = f"\tCivilization {alive_civs[0].get_id()} has won the simulation through military!"
                print(message) # Console print for military victory
                yield message
                yield message
                yield message
                return
            if not alive_civs:
                message = "\tAll civilizations have been eliminated."
                print(message) # Console print for all civilizations eliminated
                yield message
                yield message
                yield message
                return
