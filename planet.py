# The file containing the planet.py agent, acting as mediums for interaction between civs and the form of placing civs across the model grid.
import civ


class Planet:
  def __init__(self, id, pos_x, pos_y):
    self.id = id
    self.civ = None     # The civilization that owns this planet
    self.pos_x = pos_x  # The x-coordinate of the planet
    self.pos_y = pos_y  # The y-coordinate of the planet

  def assign_civ(self, civ):
    self.civ = civ
    self.civ.planets[self.id] = self
    self.civ.num_planets += 1

  def remove_civ(self):
    if self.civ:
      del self.civ.planets[self.id]
      self.civ.num_planets -= 1
      self.civ = None

  def get_civ(self):
    return self.civ
  
  def get_pos(self):
    return (self.pos_x, self.pos_y)
  
  def get_id(self):
    return self.id