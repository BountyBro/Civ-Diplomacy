# The civilization agent file for tracking a civilization's
import random
import planet
from model import MAX_CULTURE, proclaim_culture_victory

class Civ:
  def __init__(self, civ_id, tech, culture, military):
    # The civilization's ID
    self.civ_id = civ_id

    # The civilization's attributes
    self.tech = tech
    self.culture = culture
    self.military = military
    self.friendly = random.choice(0,1)  # Boolean integer value (i.e. 0 or 1). 0 marking aggressive civs, 1 marking cooperative civs.
    self.num_planets = 0      # Positive integer value. civ loses at self.num_planets == 0.
    self.planets = {}         # Dictionary of planets owned by the civ. Key is the planet ID, value is the planet object.

    self.tech_growth = random.randint(1, 3)
    self.mil_growth = random.randint(1, 3)
    self.culture_growth = random.randint(1, 3)

    self.alive = True

  def update_attributes(self, tech, culture, military, friendly):
    self.tech += self.tech_growth
    self.culture += self.culture_growth
    self.military += self.military_growth

    if self.culture >= MAX_CULTURE:
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
