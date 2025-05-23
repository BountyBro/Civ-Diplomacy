# The file utilizing all other modules to run the civ diplomacy simulation.

import numpy as np
import visualize as vis
from civ import Civ
from planet import Planet

# Constants
MAX_CULTURE = 100

def proclaim_culture_victory(civ_id):
    # we need to stop the simulation and declare a winner
    print(f"Civilization {civ_id} has achieved a culture victory!")