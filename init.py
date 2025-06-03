''' Main file for Civ-Diplomacy project. Calls functions to run simulations and visualize. Written by Luis Sandoval, Noah Brestel, and Daniil Marozau.
'''
##### DEPENDENCIES #####
from model import Model
from visualize import visualize_simulation



##### MAIN #####
if __name__ == "__main__":
    # Create a simulation model - provided parameters are user-adjustable.
    ''' Scenarios include:
    - "Friendzone": All civs start at maximum friendliness.
    - "Thunderdom": All civs start at minimum friendliness.
    - "Juggernaut": 1 civ starts at minimum friendliness w/ an additional 500 resources in each category.
    - "Wolf": 1 civ starts at minimum friendliness, and the rest start at maximum friendliness.
    Scenarios are not case-sensitive. Any other value will provide a random simulation outside these scenarios.
    '''
    simulation_model = Model(num_planets= 15, grid_height= 30, grid_width= 30, scenario= "")
    # Start the visualization
    visualize_simulation(simulation_model)



''' KNOWN BUGS:
- plot.show() is not working.
- simulation_animation.gif shows that civ colors change between turns.
'''