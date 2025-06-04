''' Main file for Civ-Diplomacy project. Calls functions to run simulations and visualize. Written by Luis Sandoval, Noah Brestel, and Daniil Marozau.
'''
##### DEPENDENCIES #####
from model import Model, log_to_plots
from visualize import visualize_simulation
from civ import Civ
from planet import Planet
from matplotlib.pyplot import bar, show



##### MAIN #####
if __name__ == "__main__":
    # Create a simulation model - provided parameters are user-adjustable.
    ''' Scenarios include:
    - "Friendzone": All civs start at maximum friendliness.
    - "Thunderdome": All civs start at minimum friendliness.
    - "Juggernaut": 1 civ starts at minimum friendliness w/ an additional 500 resources in each category.
    - "Wolf": 1 civ starts at minimum friendliness, and the rest start at maximum friendliness.
    Scenarios are not case-sensitive. Any other value will provide a random simulation outside these scenarios.
    '''
    ''' Default Run Args:
    simulation_model = Model(num_planets= 15, grid_height= 30, grid_width= 30, scenario= "Thunderdome")
    # Start the visualization
    visualize_simulation(simulation_model)
    # Store a .txt log of the simulation to convert to plots when needed.
    simulation_model.generate_sim_log()
    # log_to_plots("output/logs/name_of_the_log_file") # Will work w/ either raw file name (if in output/logs), or relative path as shown here.
    '''
    num_runs = 100
    parameters = (15, 30, 30, "")
    sim_list = [Model(*parameters) for i in range(num_runs)]
    for i in range(100):
        Civ.id_iter = 0
        Planet.id_iter = 0
        for gen in sim_list[i].run_simulation():
            pass
    ends = [sim.end_type for sim in sim_list]
    counts = [ends.count("Culture"), ends.count("Military"), ends.count("Stalemate")]
    bar(["Culture", "Military", "Stalemate"], counts)
    show()



''' KNOWN BUGS:
- simulation_animation.gif shows that civ colors change between turns.
'''