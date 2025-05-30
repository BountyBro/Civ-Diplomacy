##### DEPENDENCIES #####
import civ



##### CLASSES #####
class Planet:
    def __init__(self, id, pos_x, pos_y):
        self.id = id        # Planet ID for planet list index and unique identification
        self.civ = None     # The civilization that owns this planet.
        self.pos_x = pos_x  # The x-coordinate of the planet.
        self.pos_y = pos_y  # The y-coordinate of the planet.
        # NEW ATTRIBUTE:
        # self.resources = [] # Assigns a random number of resources from A to B. [I figure 0~3 w/ weight on 0~1? - Noah]

    def assign_civ(self, new_owner_civ):
        if self.civ:        # If there's an existing owner, remove it first.
            self.remove_civ()
        self.civ = new_owner_civ
        if new_owner_civ:   # Ensure new_owner_civ is not None.
            new_owner_civ.planets[self.id] = self
            # new_owner_civ.resources.append(self.resources)
            new_owner_civ.num_planets += 1

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
    
    '''NEW GETTER:
    def get_resources(self):
        return self.resources   # returns a list.
    '''