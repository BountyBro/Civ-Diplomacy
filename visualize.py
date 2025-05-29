# The visualization module for the civ diplomacy project. Contains functions to display the simulation and plot data.
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.lines import Line2D # For custom legends

def visualize_simulation(model):
    """
    Creates and displays an animated visualization of the simulation model.
    """
    # 1. Setup Colors
    # Determine the number of civilizations to assign unique colors.
    num_civs = len(model.list_civs)
    # Choose a colormap based on the number of civilizations to ensure distinguishability.

    if num_civs <= 20:
        # plt.cm.tab20() is a qualitative colormap with 20 distinct colors, suitable for categorical data.
        colors_array = plt.cm.tab20(np.linspace(0, 1, num_civs))
    elif num_civs <= 40:
        # Combine tab20 and tab20b to get up to 40 unique colors.
        # First, take all 20 colors from tab20.
        colors_part1 = plt.cm.tab20(np.linspace(0, 1, 20))
        # Then, take the remaining needed colors from tab20b.
        num_needed_from_tab20b = num_civs - 20
        # Get the distinct colors from tab20b. We take the first num_needed_from_tab20b.
        colors_part2 = plt.cm.tab20b(np.linspace(0, 1, 20))[:num_needed_from_tab20b]
        # Stack the color arrays vertically to combine them.
        colors_array = np.vstack((colors_part1, colors_part2))
    else:
        # For a very large number of civilizations (> 40), plt.cm.jet is used as a fallback.
        # Note: Jet is a sequential colormap and might not provide optimal distinction for many categories.
        colors_array = plt.cm.jet(np.linspace(0, 1, num_civs))

    # Create a dictionary mapping each civilization ID to a specific color.
    civ_colors = {civ.get_id(): color for civ, color in zip(model.list_civs, colors_array)}

    # 2. Setup the Plot
    # Create a figure and an axes object for the plot. Adjust figsize for legend space.
    fig, ax = plt.subplots(figsize=(13, 10)) # Adjusted for more legend space
    # Set the background color of the plot to black.
    ax.set_facecolor('black')
    # Get the dimensions of the simulation grid.
    grid_height, grid_width = model.grid.shape
    # Set the limits of the x and y axes to match the grid dimensions.
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    # Set the tick marks for the x and y axes to correspond to grid cells.
    ax.set_xticks(np.arange(0, grid_width, 1))
    ax.set_yticks(np.arange(0, grid_height, 1))
    # Display a grid on the plot for better visualization of cell boundaries.
    plt.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
    # Remove tick marks and labels as they are not needed for this visualization.
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)

    # Initialize an empty scatter plot for planets. 's' is marker size, 'zorder' controls drawing order (higher is on top).
    # Planets will be updated in the animation function.
    planet_dots = ax.scatter([], [], s=150, zorder=5)
    # Initialize a list to store lines and arrows representing interactions between civilizations.
    # These will be cleared and redrawn each frame.
    interaction_lines_and_arrows = [] # Will store lines and arrow annotations
    # Add text to display the current turn number. Positioned at the top center of the plot.
    turn_title = ax.text(0.5, 1.01, '', transform=ax.transAxes, ha="center", va="bottom", color="black", fontsize=14)
    # Add text for displaying an end message (e.g., victory condition). Initially invisible.
    end_message_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha="center", va="center", color="white", fontsize=20, visible=False)

    # Create legend for civilizations:
    # Generates a list of Line2D objects, each representing a civilization with its assigned color.
    civ_legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'Civ {civ_id}', 
                               markerfacecolor=civ_colors[civ_id], markersize=8) for civ_id in civ_colors]
    # Create the first legend for civilizations, positioned at the upper right outside the plot.
    leg1 = ax.legend(handles=civ_legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Civilizations', title_fontsize='10')
    # Set the color of the legend title.
    leg1.get_title().set_color("black")

    # Create legend for interaction types:
    # Defines Line2D objects for 'War' (red line) and 'Cooperation' (cyan dashed line).
    interaction_legend_elements = [
        Line2D([0], [0], color='red', lw=2, label='War (Attacker -> Defender)'),
        Line2D([0], [0], color='cyan', lw=1.5, linestyle='--', label='Cooperation')
    ]
    leg2 = ax.legend(handles=interaction_legend_elements, loc='lower left', bbox_to_anchor=(1.02, 0.05), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Interactions', title_fontsize='10')
    leg2.get_title().set_color("black")
    ax.add_artist(leg1) # Need to re-add the first legend if creating a second one this way
    
    plt.subplots_adjust(right=0.80) # Make space for legends

    # 3. Define the Animation Update Function
    # This function is called for each frame of the animation.
    # 'frame_data' contains the data for the current turn (turn number and interactions) or a victory message.
    def update(frame_data):
        # Ensure the end message is not visible by default at the start of an update.
        end_message_text.set_visible(False)
        # Ensure planet dots are visible by default, can be hidden if it's an end message frame.
        planet_dots.set_visible(True)

        # Clear previously drawn interaction lines and arrows to prepare for the new frame.
        # This prevents drawing over old interactions.
        for item in interaction_lines_and_arrows:
            item.remove() # Remove the artist from the plot.
        interaction_lines_and_arrows.clear() # Clear the list.

        # Check if the frame_data is a string, which indicates a victory message.
        if isinstance(frame_data, str): # Victory message frame
            planet_dots.set_visible(False) # Hide planets when showing end message.
            turn_title.set_text('') # Clear the turn title.
            end_message_text.set_text(frame_data) # Set the victory message.
            end_message_text.set_visible(True) # Make the message visible.
            # Return the artists that were changed in this frame for blitting.
            return [end_message_text, planet_dots, turn_title] # Return all artists that might change

        # If not a victory message, frame_data contains the turn number and list of interactions.
        turn, interactions = frame_data
        # Update the turn title.
        turn_title.set_text(f'Turn: {turn}')

        # Update planet positions and colors.
        # Get current positions of all planets.
        planet_positions = [p.get_pos() for p in model.list_planets]
        # Determine the color for each planet based on its owning civilization, or gray if unowned.
        planet_plot_colors = [civ_colors.get(p.get_civ().get_id(), 'gray') if p.get_civ() else 'gray' for p in model.list_planets]
        # Update the scatter plot data for planets. Positions are reversed (y,x) for matplotlib scatter.
        planet_dots.set_offsets(np.array(planet_positions)[:, ::-1] if planet_positions else np.array([]))
        # Update the colors of the planets.
        planet_dots.set_color(planet_plot_colors if planet_plot_colors else 'gray')

        # Process and draw each interaction for the current turn.
        for interaction in interactions:
            civ1 = interaction['civ1'] # The first civilization in the interaction.
            civ2 = interaction['civ2'] # The second civilization in the interaction.
            
            # Get a list of planets for each civilization involved in the interaction.
            civ1_planets_list = list(civ1.get_planets().values())
            civ2_planets_list = list(civ2.get_planets().values())

            # Ensure both civilizations have planets to draw an interaction line between them.
            # The line is typically drawn between the first listed planet of each civ (can be arbitrary if civs have multiple planets).
            if civ1_planets_list and civ2_planets_list:
                pos1_civ_obj = civ1_planets_list[0] # Source civ object for line
                pos2_civ_obj = civ2_planets_list[0] # Target civ object for line

                pos1 = pos1_civ_obj.get_pos() # Position of the first civ's planet.
                pos2 = pos2_civ_obj.get_pos() # Position of the second civ's planet.

                # Handle cooperation interactions.
                if interaction['type'] == 'cooperation':
                    # Draw a cyan dashed line between the planets.
                    line, = ax.plot([pos1[1], pos2[1]], [pos1[0], pos2[0]], color='cyan', linestyle='--', linewidth=1.5, zorder=10)
                    interaction_lines_and_arrows.append(line)
                    # Add a single-sided arrow to indicate the direction of cooperation (from civ1 to civ2).
                    # 'shrinkA' and 'shrinkB' shorten the arrow to not overlap the planet markers.
                    arrow = ax.annotate("",
                                      xy=(pos2[1], pos2[0]), xycoords='data', # Arrowhead at civ2's planet
                                      xytext=(pos1[1], pos1[0]), textcoords='data', # Text (tail) at civ1's planet
                                      arrowprops=dict(arrowstyle="->", color='cyan', lw=1.0, shrinkA=5, shrinkB=5),
                                      zorder=11)
                    interaction_lines_and_arrows.append(arrow)
                # Handle war interactions.
                elif interaction['type'] == 'war':
                    # Identify the attacker. Defaults to civ1 if not explicitly specified.
                    attacker_obj = interaction.get('attacker', civ1) # Default to civ1 if not specified
                    # Defender object is primarily for identifying who the interaction data refers to.
                    # The actual target position will come from 'defender_target_planet_initial_pos'

                    attacker_planets = list(attacker_obj.get_planets().values())
                    # Retrieve the pre-calculated initial position of the defender's planet that is being targeted.
                    # This is important if the planet might be captured or destroyed during the interaction resolution.
                    defender_target_initial_pos = interaction.get('defender_target_planet_initial_pos')

                    # Ensure the attacker has planets and a target position for the defender is available.
                    if attacker_planets and defender_target_initial_pos:
                        start_planet_pos = attacker_planets[0].get_pos() # Attacker's planet position.
                        end_planet_pos = defender_target_initial_pos # Defender's targeted planet initial position.
                        
                        # Draw a red solid line between the attacker and the defender's target planet.
                        line, = ax.plot([start_planet_pos[1], end_planet_pos[1]], [start_planet_pos[0], end_planet_pos[0]], color='red', linestyle='-', linewidth=2.5, zorder=10)
                        interaction_lines_and_arrows.append(line)
                        
                        # Add an arrow annotation to show the direction of attack.
                        arrow = ax.annotate("",
                                          xy=(end_planet_pos[1], end_planet_pos[0]), xycoords='data', # Arrowhead at defender's planet
                                          xytext=(start_planet_pos[1], start_planet_pos[0]), textcoords='data', # Tail at attacker's planet
                                          arrowprops=dict(arrowstyle="->", color='red', lw=1.5, shrinkA=5, shrinkB=5),
                                          zorder=11)
                        interaction_lines_and_arrows.append(arrow)
                    elif attacker_planets and not defender_target_initial_pos:
                        # This case occurs if the defender had no planets when the war interaction was initiated.
                        # No specific target for the arrow, so it's not drawn.
                        # A message is printed for debugging/logging purposes.
                        print(f"War interaction for attacker {attacker_obj.get_id()} but defender had no initial planets for arrow target.")
        
        # Return all artists that were updated in this frame. This is used by blitting for efficiency.
        return [planet_dots, turn_title, end_message_text] + interaction_lines_and_arrows

    # 4. Create and Run the Animation
    ani = animation.FuncAnimation(fig, update, frames=model.run_simulation, blit=True, interval=1000, repeat=False)
    ani.save('simulation_animation.gif', writer='pillow', fps=1)
    plt.show()

def winPlot(data):
  pass # TO-DO: Displays a graph (form TBD) portraying the prevalence in victory between cooperative and aggressive civs.
