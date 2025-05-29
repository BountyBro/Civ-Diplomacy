# The visualization module for the civ diplomacy project. Contains functions to display the simulation and plot data.
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

def visualize_simulation(model):
    """
    Creates and displays an animated visualization of the simulation model.
    """
    # 1. Setup Colors
    num_civs = len(model.list_civs)
    colors = plt.cm.jet(np.linspace(0, 1, num_civs))
    civ_colors = {civ.get_id(): color for civ, color in zip(model.list_civs, colors)}

    # 2. Setup the Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('black')
    grid_height, grid_width = model.grid.shape
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_xticks(np.arange(0, grid_width, 1))
    ax.set_yticks(np.arange(0, grid_height, 1))
    plt.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)

    planet_dots = ax.scatter([], [], s=150, zorder=5)
    interaction_lines = []
    turn_title = ax.text(0.5, 1.01, '', transform=ax.transAxes, ha="center", va="bottom", color="black", fontsize=14)
    # Text object for end message
    end_message_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha="center", va="center", color="white", fontsize=20, visible=False)

    # 3. Define the Animation Update Function
    def update(frame_data):
        # Clear end message visibility from previous frame if it was a message frame
        end_message_text.set_visible(False)
        
        if isinstance(frame_data, str): # Victory message frame
            # Clear existing plot elements
            planet_dots.set_visible(False)
            for line in interaction_lines:
                line.remove()
            interaction_lines.clear()
            turn_title.set_text('')
            
            # Display victory message
            end_message_text.set_text(frame_data)
            end_message_text.set_visible(True)
            return [end_message_text] # Only return the message text artist

        # Normal frame (turn, interactions)
        turn, interactions = frame_data
        # Ensure planet_dots are visible for normal frames
        planet_dots.set_visible(True)
        turn_title.set_text(f'Turn: {turn}')

        # Update Planets
        planet_positions = [p.get_pos() for p in model.list_planets]
        # Corrected planet_colors list comprehension to handle p.get_civ() returning None
        planet_plot_colors = [civ_colors[p.get_civ().get_id()] if p.get_civ() and p.get_civ().get_id() in civ_colors else 'gray' for p in model.list_planets]
        planet_dots.set_offsets(np.array(planet_positions)[:, ::-1]) # Flip coords for x,y plot
        planet_dots.set_color(planet_plot_colors)

        # Animate Interactions
        for line in interaction_lines:
            line.remove()
        interaction_lines.clear()

        for interaction in interactions:
            civ1 = interaction['civ1']
            civ2 = interaction['civ2']
            
            # Ensure planets for these civs exist and civs are alive before trying to get positions
            # This check might be more robust depending on how Civ.get_planet behaves for dead/unassigned civs
            civ1_planet = civ1.get_planet(civ1.get_id()) 
            civ2_planet = civ2.get_planet(civ2.get_id())

            if civ1_planet and civ2_planet and civ1.alive and civ2.alive:
                pos1 = civ1_planet.get_pos()
                pos2 = civ2_planet.get_pos()

                line_style = '--' if interaction['type'] == 'cooperation' else '-'
                line_color = 'cyan' if interaction['type'] == 'cooperation' else 'red'
                line_width = 1.5 if interaction['type'] == 'cooperation' else 2.5

                line, = ax.plot([pos1[1], pos2[1]], [pos1[0], pos2[0]], color=line_color, linestyle=line_style, linewidth=line_width, zorder=10)
                interaction_lines.append(line)
        
        # Ensure end_message_text is part of the returned artists if not a message frame, even if invisible
        # This helps blitting to know about it, though it might not be strictly necessary if only returned when visible.
        return [planet_dots, turn_title, end_message_text] + interaction_lines

    # 4. Create and Run the Animation
    # Slowed down: interval to 1000ms (1 sec/frame)
    ani = animation.FuncAnimation(fig, update, frames=model.run_simulation, blit=True, interval=1000, repeat=False)
    # plt.show() # Keep commented out as per previous preference
    # Save animation as GIF with adjusted fps
    ani.save('simulation_animation.gif', writer='pillow', fps=1) 

def winPlot(data):
  pass # TO-DO: Displays a graph (form TBD) portraying the prevalence in victory between cooperative and aggressive civs.
