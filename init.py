''' The main program that is used to configure the simulations run, and data collected.
Changelog:
v0.0.0: Established dependencies and tied to 'model.py'. - NB
'''
import model
import visualize as vis

if __name__ == "__main__":
    # Create a simulation model
    # You can adjust these parameters
    simulation_model = model.Model(num_planets=15, grid_height=30, grid_width=30)

    # Start the visualization
    vis.visualize_simulation(simulation_model)
