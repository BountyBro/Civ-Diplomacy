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
    num_civs = len(model.list_civs)
    # Use a more distinguishable colormap if possible
    if num_civs <= 20:
        colors = plt.cm.tab20(np.linspace(0, 1, num_civs))
    elif num_civs <= 40: # tab20b and tab20c can be combined or used if tab20 is not enough
        colors = plt.cm.tab20b(np.linspace(0,1, num_civs))
    else:
        colors = plt.cm.jet(np.linspace(0, 1, num_civs))
    civ_colors = {civ.get_id(): color for civ, color in zip(model.list_civs, colors)}

    # 2. Setup the Plot
    fig, ax = plt.subplots(figsize=(13, 10)) # Adjusted for more legend space
    ax.set_facecolor('black')
    grid_height, grid_width = model.grid.shape
    ax.set_xlim(0, grid_width)
    ax.set_ylim(0, grid_height)
    ax.set_xticks(np.arange(0, grid_width, 1))
    ax.set_yticks(np.arange(0, grid_height, 1))
    plt.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)

    planet_dots = ax.scatter([], [], s=150, zorder=5)
    interaction_lines_and_arrows = [] # Will store lines and arrow annotations
    turn_title = ax.text(0.5, 1.01, '', transform=ax.transAxes, ha="center", va="bottom", color="black", fontsize=14)
    end_message_text = ax.text(0.5, 0.5, '', transform=ax.transAxes, ha="center", va="center", color="white", fontsize=20, visible=False)

    # Create legend for civilizations
    civ_legend_elements = [Line2D([0], [0], marker='o', color='w', label=f'Civ {civ_id}', 
                               markerfacecolor=civ_colors[civ_id], markersize=8) for civ_id in civ_colors]
    leg1 = ax.legend(handles=civ_legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Civilizations', title_fontsize='10')
    leg1.get_title().set_color("black")

    # Create legend for interaction types
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
    def update(frame_data):
        end_message_text.set_visible(False)
        planet_dots.set_visible(True)

        # Clear old lines and arrows
        for item in interaction_lines_and_arrows:
            item.remove()
        interaction_lines_and_arrows.clear()

        if isinstance(frame_data, str): # Victory message frame
            planet_dots.set_visible(False)
            turn_title.set_text('')
            end_message_text.set_text(frame_data)
            end_message_text.set_visible(True)
            return [end_message_text, planet_dots, turn_title] # Return all artists that might change

        turn, interactions = frame_data
        turn_title.set_text(f'Turn: {turn}')

        planet_positions = [p.get_pos() for p in model.list_planets]
        planet_plot_colors = [civ_colors.get(p.get_civ().get_id(), 'gray') if p.get_civ() else 'gray' for p in model.list_planets]
        planet_dots.set_offsets(np.array(planet_positions)[:, ::-1] if planet_positions else np.array([]))
        planet_dots.set_color(planet_plot_colors if planet_plot_colors else 'gray')

        for interaction in interactions:
            civ1 = interaction['civ1']
            civ2 = interaction['civ2']
            
            civ1_planets_list = list(civ1.get_planets().values())
            civ2_planets_list = list(civ2.get_planets().values())

            if civ1_planets_list and civ2_planets_list:
                pos1_civ_obj = civ1_planets_list[0] # Source civ object for line
                pos2_civ_obj = civ2_planets_list[0] # Target civ object for line

                pos1 = pos1_civ_obj.get_pos()
                pos2 = pos2_civ_obj.get_pos()

                if interaction['type'] == 'cooperation':
                    line, = ax.plot([pos1[1], pos2[1]], [pos1[0], pos2[0]], color='cyan', linestyle='--', linewidth=1.5, zorder=10)
                    interaction_lines_and_arrows.append(line)
                    # Single-sided arrow for cooperation (civ1 -> civ2 as per interaction data order)
                    arrow = ax.annotate("",
                                      xy=(pos2[1], pos2[0]), xycoords='data', # Arrowhead at civ2's planet
                                      xytext=(pos1[1], pos1[0]), textcoords='data', # Text (tail) at civ1's planet
                                      arrowprops=dict(arrowstyle="->", color='cyan', lw=1.0, shrinkA=5, shrinkB=5),
                                      zorder=11)
                    interaction_lines_and_arrows.append(arrow)
                elif interaction['type'] == 'war':
                    attacker_obj = interaction.get('attacker', civ1) # Default to civ1 if not specified
                    # Defender object is primarily for identifying who the interaction data refers to.
                    # The actual target position will come from 'defender_target_planet_initial_pos'

                    attacker_planets = list(attacker_obj.get_planets().values())
                    # Get the pre-calculated initial position of a defender planet
                    defender_target_initial_pos = interaction.get('defender_target_planet_initial_pos')

                    if attacker_planets and defender_target_initial_pos:
                        start_planet_pos = attacker_planets[0].get_pos()
                        end_planet_pos = defender_target_initial_pos # Use the stored initial position
                        
                        # ax.plot for the line itself
                        line, = ax.plot([start_planet_pos[1], end_planet_pos[1]], [start_planet_pos[0], end_planet_pos[0]], color='red', linestyle='-', linewidth=2.5, zorder=10)
                        interaction_lines_and_arrows.append(line)
                        
                        # Add an arrow annotation
                        arrow = ax.annotate("",
                                          xy=(end_planet_pos[1], end_planet_pos[0]), xycoords='data',
                                          xytext=(start_planet_pos[1], start_planet_pos[0]), textcoords='data', 
                                          arrowprops=dict(arrowstyle="->", color='red', lw=1.5, shrinkA=5, shrinkB=5),
                                          zorder=11)
                        interaction_lines_and_arrows.append(arrow)
                    elif attacker_planets and not defender_target_initial_pos:
                        # This case means the defender had no planets at the start of the interaction.
                        # No specific target for the arrow from model.py, so we might not draw one,
                        # or point it generically if needed, but for now, skip.
                        print(f"War interaction for attacker {attacker_obj.get_id()} but defender had no initial planets for arrow target.")
        
        return [planet_dots, turn_title, end_message_text] + interaction_lines_and_arrows

    # 4. Create and Run the Animation
    ani = animation.FuncAnimation(fig, update, frames=model.run_simulation, blit=True, interval=1000, repeat=False)
    ani.save('simulation_animation.gif', writer='pillow', fps=1)

def winPlot(data):
  pass # TO-DO: Displays a graph (form TBD) portraying the prevalence in victory between cooperative and aggressive civs.
