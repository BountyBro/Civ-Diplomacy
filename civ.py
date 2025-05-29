# The civilization agent file for tracking a civilization's
import random
import planet
# from model import MAX_CULTURE, proclaim_culture_victory # Removed for circular import fix

MAX_CULTURE = 100 # Defined here

def proclaim_culture_victory(civ_id):
    # we need to stop the simulation and declare a winner
    print(f"Civilization {civ_id} has achieved a culture victory!")

class Civ:
  def __init__(self, civ_id, tech= 0, culture= 0, military= 0):
    # The civilization's ID
    self.civ_id = civ_id

    # The civilization's attributes
    self.tech = tech
    self.culture = culture
    self.military = military
    self.friendly = random.choice([0,1])  # Corrected: Was random.choice(0,1)
    self.num_planets = 0      # Positive integer value. civ loses at self.num_planets == 0.
    self.planets = {}         # Dictionary of planets owned by the civ. Key is the planet ID, value is the planet object.

    self.tech_growth = random.randint(1, 3)
    self.mil_growth = random.randint(1, 3) # Corrected: Was self.military_growth in some contexts
    self.culture_growth = random.randint(1, 3)

    self.alive = True
    self.has_won_culture_victory = False # Added flag for clean stop

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
    print(f"Civilization {self.civ_id} has been eliminated at turn {t}")

  # Getters
  def get_planets(self):
    return self.planets

  def get_id(self):
    return self.civ_id

  def get_friendly(self):
    return self.friendly
  
  def get_tech(self):
    return self.tech
  
  def get_culture(self):
    return self.culture
  
  def get_military(self):
    return self.military
  
  def get_num_planets(self):
    return self.num_planets
  
  def get_alive(self):
    return self.alive
  
  def get_planet(self, planet_id):
    return self.planets.get(planet_id, None)
  
  def get_planet_ids(self):
    return list(self.planets.keys())
  
  def get_planet_positions(self):
    return [planet.get_pos() for planet in self.planets.values()]
