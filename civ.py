# The civilization agent file for tracking a civilization's

class civ:
  def __init__(self, tech, culture, military, friendly):
    self.tech = tech
    self.culture = culture
    self.military = military
    self.friendly = friendly  # Boolean integer value (i.e. 0 or 1). 0 marking aggressive civs, 1 marking cooperative civs.
    self.num_planets = 0      # Positive integer value. civ loses at self.num_planets == 0.
