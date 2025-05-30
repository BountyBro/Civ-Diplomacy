##### DEPENDENCIES #####
import model
import visualize as vis



##### MAIN #####
if __name__ == "__main__":
    # Create a simulation model - provided parameters are user-adjustable.
    simulation_model = model.Model(num_planets=15, grid_height=30, grid_width=30)
    # Start the visualization
    vis.visualize_simulation(simulation_model)

''' KNOWN BUGS:
- Simulation animation displays on last frame. This is bypassed by saving as a gif. Could also set funcAnimation.repeat to True, but storing is good documentation.
- Simulation print ends w/ 3 "Turn 1:\n" prints. Only prints after simulation is displayed, whereas the rest of the print is resolved prior.
'''