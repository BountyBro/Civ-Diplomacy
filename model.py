''' File containing the 'Model' class, used to run a simulation.
Changelog:
v0.0.0: Established simulation end condition. - DM
v0.0.1: Created and filled 'Model' class. - NB
'''
##### DEPDENDENCIES #####
import numpy as np
from random import sample
import random
import visualize as vis
from civ import Civ, proclaim_culture_victory
from planet import Planet



##### USER-ADJUSTABLE #####
# MAX_CULTURE = 100 # Moved to civ.py
MIN_PLANETS = 3         # Inclusive lower bound integer for accepted range of planet count.
MAX_PLANETS = 25        # Inclusive higher bound integer for accepted range of planet count.
MIN_GRID_HEIGHT = 10    # Inclusive lower bound integer determining minimum grid height (y dimension).
MIN_GRID_WIDTH = 10     # Inclusive lower bound integer determining minimum grid width (x dimension).
MAX_GRID_HEIGHT = 50    # Inclusive higher bound integer determining maximum grid height (y dimension).
MAX_GRID_WIDTH = 50     # Inclusive higher bound integer determining maximum grid width (x dimension).
WAR_WIN_BOOST = 2         # Value of tech and military boost for winning a war.
COOPERATION_BOOST = 1      # Value of tech and culture boost for cooperating with another civ.
WAR_PENALTY = 1            # Value of tech and culture penalty for an attacker losing a war.


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

    def civs_war(self, c1, c2, t): # Actual war mechanics happen here
        # Determine attacker and defender FOR MECHANICS
        if c1.get_friendly() == 0 and c2.get_friendly() == 1:
            attacker = c1
            defender = c2
        elif c2.get_friendly() == 0 and c1.get_friendly() == 1:
            attacker = c2
            defender = c1
        else: 
            attacker = c1
            defender = c2
        # The rest of civs_war logic remains the same (calculating power, battle, consequences...)
        # This internal attacker/defender is for who fights whom and who gets what.
        # The one stored in interaction_details is for the visualizer's arrow direction.

        print(f"Civ {attacker.get_id()} (Is Aggressive: {attacker.get_friendly()==0}) is ACTUALLY attacking Civ {defender.get_id()} (Is Aggressive: {defender.get_friendly()==0}).")

        # Tech gives a bonus to combat effectiveness
        attacker_power = attacker.get_military() * (1 + (0.1 * attacker.get_tech()))
        defender_power = defender.get_military() * (1 + (0.1 * defender.get_tech()))

        total_combat_power = attacker_power + defender_power

        if total_combat_power == 0: # Stalemate if both have zero power
            print(f"Stalemate between Civ {attacker.get_id()} and Civ {defender.get_id()} due to zero combat power.")
            return

        attacker_win_chance = attacker_power / total_combat_power

        if random.random() < attacker_win_chance:
            # Attacker wins
            print(f"Attacker Civ {attacker.get_id()} wins against Civ {defender.get_id()}!")
            attacker.military += WAR_WIN_BOOST # Attacker gets military boost
            attacker.tech += WAR_WIN_BOOST     # Attacker gets tech boost

            defender_planets = list(defender.get_planets().values())
            if defender_planets: # Defender has planets to lose
                conquered_planet = random.choice(defender_planets)
                print(f"Civ {attacker.get_id()} conquers planet {conquered_planet.get_id()} from Civ {defender.get_id()}.")
                conquered_planet.assign_civ(attacker) # Planet changes owner
                
                # Check if defender is eliminated
                if defender.check_if_dead(t):
                    print(f"Civ {defender.get_id()} has been eliminated from the war by Civ {attacker.get_id()}.")
            else:
                print(f"Defender Civ {defender.get_id()} had no planets to conquer.")
        else:
            # Defender wins (Attacker loses)
            print(f"Defender Civ {defender.get_id()} wins against Civ {attacker.get_id()}!")
            defender.military += WAR_WIN_BOOST # Defender gets military boost
            defender.tech += WAR_WIN_BOOST     # Defender gets tech boost
            defender.culture += WAR_WIN_BOOST  # Defender gets culture boost

            # Attacker takes a hit to tech and culture
            attacker.tech = max(0, attacker.tech - WAR_PENALTY)
            attacker.culture = max(0, attacker.culture - WAR_PENALTY)
            print(f"Attacker Civ {attacker.get_id()} loses {WAR_PENALTY} tech and culture.")

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
                        print(f"Civilizations {civ1.get_id()} and {civ2.get_id()} are cooperating.")
                        self.civs_cooperate(civ1, civ2)
                    elif civ1.get_friendly() == 0 or civ2.get_friendly() == 0:
                        interaction_details['type'] = 'war'
                        current_attacker, current_defender = None, None # For clarity

                        # Determine attacker and defender for visualization metadata AND mechanics
                        if civ1.get_friendly() == 0 and civ2.get_friendly() == 1:
                            current_attacker = civ1
                            current_defender = civ2
                        elif civ2.get_friendly() == 0 and civ1.get_friendly() == 1:
                            current_attacker = civ2
                            current_defender = civ1
                        else: # Both same friendly status, or both aggressive. Default c1 attacks.
                            current_attacker = civ1 
                            current_defender = civ2
                        
                        interaction_details['attacker'] = current_attacker
                        interaction_details['defender'] = current_defender

                        # Store initial position of a defender planet for arrow targeting
                        defender_initial_planets = list(current_defender.get_planets().values())
                        if defender_initial_planets:
                            interaction_details['defender_target_planet_initial_pos'] = defender_initial_planets[0].get_pos()
                        else:
                            # If defender has no planets initially, arrow might not be meaningful or drawable for target
                            interaction_details['defender_target_planet_initial_pos'] = None 

                        print(f"Civilizations {civ1.get_id()} and {civ2.get_id()} are at war! (Visual Attacker: {current_attacker.get_id()})")
                        self.civs_war(civ1, civ2, t) # Actual war mechanics, uses its own attacker/defender logic now.
                    
                    interactions.append(interaction_details)
        return interactions

    def run_simulation(self):
        t = 0
        while True:
            t += 1
            print(f"Turn {t}")
            
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
                message = f"Civilization {alive_civs[0].get_id()} has won the simulation through military!"
                yield message
                yield message
                yield message
                return
            if not alive_civs:
                message = "All civilizations have been eliminated."
                yield message
                yield message
                yield message
                return
