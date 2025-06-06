''' Primary visualization method file. Used to create animations of simulations, both stored as simulation_animation.gif, and as a matplotlib.plot.show() (if that works).
'''
##### DEPENDENCIES #####
import matplotlib
matplotlib.use('TkAgg') # Ensure interactive backend is set
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.lines import Line2D # For custom legends
from matplotlib.patches import Rectangle # For military bars
from planet import POPCAP_MAX # Added for scaling planet sizes



##### FUNCTIONS #####
def visualize_simulation(model):
    ''' Provides a visual representation of the input model in the form of a .gif file stored in the same directory.
        Inputs:
            - model: A 'Model' objcet to base the visualizaiton off of.
        Outputs:
            - simulation_animation.gif: written to the same dir. Visualizes the provided model turn-by-turn.
    '''
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
    fig, ax = plt.subplots(figsize=(13, 11)) # Adjusted height for more legend space
    # Set the background color of the plot to black.
    ax.set_facecolor('black')
    # Get the dimensions of the simulation grid.
    grid_height, grid_width = model.grid.shape
    # Set the limits of the x and y axes to match the grid dimensions.
    ax.set_xlim(-1, grid_width + 1)
    ax.set_ylim(-1, grid_height + 1)
    # Set the tick marks for the x and y axes to correspond to grid cells.
    ax.set_xticks(np.arange(0, grid_width, 1))
    ax.set_yticks(np.arange(0, grid_height, 1))
    # Display a grid on the plot for better visualization of cell boundaries.
    plt.grid(True, which='both', color='gray', linestyle='--', linewidth=0.5)
    # Remove tick marks and labels as they are not needed for this visualization.
    plt.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)

    # Initialize an empty scatter plot for planets. 's' is marker size, 'zorder' controls drawing order (higher is on top).
    # Planets will be updated in the animation function.
    # Added linewidth and initial edgecolor for resource indication
    planet_dots = ax.scatter([], [], s=150, zorder=5, linewidths=1.5, edgecolors='none') 
    # Initialize a list to store lines and arrows representing interactions between civilizations.
    # These will be cleared and redrawn each frame.
    interaction_lines_and_arrows = [] # Will store lines and arrow annotations
    strength_indicator_patches = [] # Will store military strength bars
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
    # Defines Line2D objects for 'War' (red line), 'Cooperation' (cyan dashed line), and 'Trade' (green dotted line).
    interaction_legend_elements = [
        Line2D([0], [0], color='red', lw=2, label='War'),
        # Line2D([0], [0], color='cyan', lw=1.5, linestyle='--', label='Cooperation'), # Removed Cooperation
        Line2D([0], [0], color='green', lw=1.5, linestyle=':', label='Trade') 
    ]
    leg2 = ax.legend(handles=interaction_legend_elements, loc='lower left', bbox_to_anchor=(1.02, 0.05), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Interactions', title_fontsize='10')
    leg2.get_title().set_color("black")
    ax.add_artist(leg1) # Need to re-add the first legend if creating a second one this way
    ax.add_artist(leg2) # Add the second legend

    # Create legend for resource border colors:
    resource_legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Dominant Energy', 
               markerfacecolor='gray', markeredgecolor='yellow', markeredgewidth=1.5, markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Dominant Food', 
               markerfacecolor='gray', markeredgecolor='green', markeredgewidth=1.5, markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Dominant Minerals', 
               markerfacecolor='gray', markeredgecolor='silver', markeredgewidth=1.5, markersize=8)
    ]
    # Position this legend below the interaction legend
    leg3 = ax.legend(handles=resource_legend_elements, loc='lower left', bbox_to_anchor=(1.02, -0.12), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Planet Resources', title_fontsize='10')
    leg3.get_title().set_color("black")
    ax.add_artist(leg3)

    # Create legend for military strength:
    military_legend_elements = [
        Line2D([0], [0], color='purple', lw=4, label='Military Strength'),
        Line2D([0], [0], color='deepskyblue', lw=4, label='Tech Level'),
        Line2D([0], [0], color='gold', lw=4, label='Culture Progress')
    ]
    leg4 = ax.legend(handles=military_legend_elements, loc='lower left', bbox_to_anchor=(1.02, -0.25), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Civilization Stats', title_fontsize='10')
    leg4.get_title().set_color("black")
    ax.add_artist(leg4)
    
    # Create legend for Friendliness Bar
    friendliness_legend_elements = [
        Rectangle((0,0), 1, 1, color='red', label='Unfriendly (<0.25)'),
        Rectangle((0,0), 1, 1, color='yellow', label='Neutral (0.25-0.75)'),
        Rectangle((0,0), 1, 1, color='lime', label='Friendly (>0.75)') # Using lime for consistency if green is for food borders
    ]
    leg5 = ax.legend(handles=friendliness_legend_elements, loc='lower left', bbox_to_anchor=(1.02, -0.38), 
                     borderaxespad=0., labelcolor='black', frameon=False, title='Civilization Friendliness', title_fontsize='10')
    leg5.get_title().set_color("black")
    ax.add_artist(leg5)

    plt.subplots_adjust(right=0.80, bottom=0.28) # Adjusted bottom for new legend

    # 3. Define the Animation Update Function
    def update(frame_data):
        ''' Custom arg function for matplotlib.animation.funcAnimation(). Updates animation for each frame.
        Inputs:
            - frame_data: The data to be displayed during the new frame. Provided by funcAnimation().
        Outputs:
            - None. Replaces old frame data to display new information.
        '''
        # Clear previous frame's elements
        end_message_text.set_visible(False)
        planet_dots.set_visible(True) # Make sure planets are visible by default each frame

        for item in interaction_lines_and_arrows: item.remove()
        interaction_lines_and_arrows.clear()
        for patch in strength_indicator_patches: patch.remove()
        strength_indicator_patches.clear()

        # Check if frame_data is a victory/end message based on its structure
        # model.py yields (message_string, [], []) for such cases
        if len(frame_data) == 3 and isinstance(frame_data[0], str) and frame_data[1] == [] and frame_data[2] == []:
            message_str = frame_data[0]
            planet_dots.set_visible(False) # Hide planets during end message
            turn_title.set_text('') # Clear turn title
            end_message_text.set_text(message_str)
            end_message_text.set_visible(True)
            # Return relevant artists
            return [planet_dots, turn_title, end_message_text] + interaction_lines_and_arrows + strength_indicator_patches
        
        # Otherwise, it's a normal turn frame
        turn, current_interactions, conquest_events = frame_data 
        turn_title.set_text(f'Turn: {turn}')

        # ----- PLANET DRAWING LOGIC RESTORED -----
        # Identify planets conquered this turn for the flash effect
        conquered_planet_ids_this_turn = {event['planet_id'] for event in conquest_events}

        # Update planet positions and colors.
        planet_positions = [p.get_pos() for p in model.list_planets]
        planet_plot_colors = []
        planet_border_colors_final = [] 

        for i, p in enumerate(model.list_planets):
            if p.get_id() in conquered_planet_ids_this_turn:
                planet_plot_colors.append('white') # Flash color
                planet_border_colors_final.append('white') # Flash border
            else:
                owner_civ = p.get_civ()
                planet_plot_colors.append(civ_colors.get(owner_civ.get_id(), 'gray') if owner_civ else 'gray')
                # Determine border color based on resources (logic from before)
                current_border_color = civ_colors.get(owner_civ.get_id(), 'gray') if owner_civ else 'gray' # Default to fill
                resources = p.get_resources() 
                resource_colors = {"energy": 'yellow', "food": 'green', "minerals": 'silver'}
                if resources and sum(resources.values()) > 0:
                    dominant_resource_name = None
                    if resources["energy"] > resources["food"] and resources["energy"] > resources["minerals"]:
                        dominant_resource_name = "energy"
                    elif resources["food"] > resources["energy"] and resources["food"] > resources["minerals"]:
                        dominant_resource_name = "food"
                    elif resources["minerals"] > resources["energy"] and resources["minerals"] > resources["food"]:
                        dominant_resource_name = "minerals"
                    else: 
                        if resources["energy"] >= resources["food"] and resources["energy"] >= resources["minerals"] and resources["energy"] > 0:
                            dominant_resource_name = "energy"
                        elif resources["food"] >= resources["energy"] and resources["food"] >= resources["minerals"] and resources["food"] > 0:
                            dominant_resource_name = "food"
                        elif resources["minerals"] >= resources["energy"] and resources["minerals"] >= resources["food"] and resources["minerals"] > 0:
                            dominant_resource_name = "minerals"
                    if dominant_resource_name:
                        current_border_color = resource_colors[dominant_resource_name]
                planet_border_colors_final.append(current_border_color)

        # Calculate planet sizes based on population_cap or current population if owned.
        sizing_values = []
        for p in model.list_planets:
            civ_owner = p.get_civ()
            if civ_owner:
                civ_total_pop_cap = civ_owner.get_population_cap()
                civ_current_pop = civ_owner.get_population()
                if civ_total_pop_cap > 0:
                    # Proportional share of civ's population on this planet
                    planet_pop_share = (p.get_population_cap() / civ_total_pop_cap) * civ_current_pop
                    sizing_values.append(planet_pop_share)
                else:
                    sizing_values.append(0) # Civ owns planet but has 0 total capacity
            else: # Unowned planet
                sizing_values.append(p.get_population_cap())

        min_dot_size = 30  # Min visual marker size
        max_dot_size = 250 # Max visual marker size
        
        norm_min_data_val = 0 # The conceptual minimum for population/capacity values
        norm_max_data_val = POPCAP_MAX # Use global max capacity for normalization scale

        if not model.list_planets: # No planets
            planet_plot_sizes = []
        elif norm_max_data_val == norm_min_data_val: # Avoid division by zero if max_cap is same as min_cap (e.g. 0)
            planet_plot_sizes = [min_dot_size + (max_dot_size - min_dot_size) / 2] * len(sizing_values)
        else:
            planet_plot_sizes = [
                min_dot_size + ( (max(0, val) - norm_min_data_val) / (norm_max_data_val - norm_min_data_val) ) * (max_dot_size - min_dot_size)
                for val in sizing_values
            ]
        
        # Clip sizes to be within the defined visual range
        planet_plot_sizes = [max(min_dot_size, min(s, max_dot_size)) for s in planet_plot_sizes]
                
        planet_dots.set_offsets(np.array(planet_positions)[:, ::-1] if planet_positions else np.array([]))
        planet_dots.set_color(planet_plot_colors if planet_plot_colors else 'gray')
        if model.list_planets:
            planet_dots.set_sizes(planet_plot_sizes)
            planet_dots.set_edgecolors(planet_border_colors_final) 
        else:
            planet_dots.set_sizes([])

        # ----- INTERACTION LINE DRAWING LOGIC RESTORED -----
        for idx, interaction in enumerate(current_interactions): # Added idx for debug
            civ1, civ2 = interaction['civ1'], interaction['civ2']
            # Ensure both civs have planets based on the current state in the model objects
            civ1_planets_for_interaction = list(civ1.get_planets().values())
            civ2_planets_for_interaction = list(civ2.get_planets().values())

            if civ1_planets_for_interaction and civ2_planets_for_interaction: 
                pos1, pos2 = civ1_planets_for_interaction[0].get_pos(), civ2_planets_for_interaction[0].get_pos()
                if interaction['type'] == 'trade':
                    if len(civ1_planets_for_interaction) > 0 and len(civ2_planets_for_interaction) > 0: # Redundant check, but explicit
                        line, = ax.plot([pos1[1], pos2[1]], [pos1[0], pos2[0]], color='green', linestyle='--', linewidth=2.5, zorder=10)
                        interaction_lines_and_arrows.append(line)
                elif interaction['type'] == 'war':
                    attacker_obj = interaction.get('attacker', civ1) # Default to civ1 if 'attacker' not specified
                    defender_target_initial_pos = interaction.get('defender_target_planet_initial_pos')
                    
                    # Ensure attacker has planets to attack from and a target position is defined
                    attacker_planets_for_war = list(attacker_obj.get_planets().values())
                    if attacker_planets_for_war and defender_target_initial_pos:
                        start_pos = attacker_planets_for_war[0].get_pos()
                        # Draw line for war
                        line, = ax.plot([start_pos[1], defender_target_initial_pos[1]], [start_pos[0], defender_target_initial_pos[0]], color='red', lw=2.5, zorder=10)
                        interaction_lines_and_arrows.append(line)
                        # Draw arrow for war
                        arrow = ax.annotate("", xy=(defender_target_initial_pos[1], defender_target_initial_pos[0]), 
                                            xytext=(start_pos[1], start_pos[0]), 
                                            arrowprops=dict(arrowstyle="->",color='red',lw=1.5,shrinkA=5,shrinkB=5),zorder=11)
                        interaction_lines_and_arrows.append(arrow)
            else: # One or both civs have no planets according to current state
                pass
        
        # ----- STRENGTH INDICATOR DRAWING LOGIC -----
        # Constants for bar drawing (inspired by user snippet)
        fixed_bar_width = 0.2
        max_bar_height_visual = 0.8  # Max height in grid units for stat bars
        gap_from_planet_edge = 0.1
        gap_between_bars = 0.05

        friendliness_bar_height_val = 0.15 # Renamed to avoid conflict

        # Max values for normalization (assuming 100 if not otherwise specified by model/civ)
        MAX_MILITARY = 100.0
        MAX_TECH = 100.0
        MAX_CULTURE = 100.0

        # For dynamic positioning based on planet visual size
        min_dot_size_px = 30  # from planet_plot_sizes calculation
        max_dot_size_px = 250 # from planet_plot_sizes calculation
        # Estimate visual radius in data/grid coordinates.
        # These are rough estimates; matplotlib sizing is complex (area vs radius).
        # Assuming a somewhat linear mapping for simplicity of visual offset.
        # Smallest planet visual diameter might be around 0.2 grid units, largest around 0.8-1.0.
        min_expected_planet_radius_grid = 0.15 # Approximate radius in grid units for min_dot_size_px
        max_expected_planet_radius_grid = 0.5  # Approximate radius in grid units for max_dot_size_px


        for i, civ in enumerate(model.list_civs): # Use enumerate if accessing planet_plot_sizes by index
            if civ.get_alive() and list(civ.get_planets().values()):
                # Anchor bars to the civ's first planet
                first_planet_obj = list(civ.get_planets().values())[0]
                planet_pos_x_grid, planet_pos_y_grid = first_planet_obj.get_pos()[1], first_planet_obj.get_pos()[0] # grid_x, grid_y

                # Find the plot size of this specific planet to estimate its visual radius
                # This requires matching the planet object to its size calculated earlier
                # This is a simplified approach; ideally, planet objects would store their last computed visual size
                current_planet_s_value = 0 # Default
                planet_index_in_model_list = -1
                try:
                    # Find the index of the first_planet_obj in the model.list_planets
                    # This is crucial for fetching the correct size from planet_plot_sizes
                    planet_index_in_model_list = model.list_planets.index(first_planet_obj)
                    if planet_index_in_model_list < len(planet_plot_sizes): # planet_plot_sizes is defined in the update scope
                         current_planet_s_value = planet_plot_sizes[planet_index_in_model_list] # This is in pixels squared (area)
                    else: # Fallback or if planet_plot_sizes not yet fully populated for this civ's planet
                        current_planet_s_value = min_dot_size_px # Default to min size if issue
                except ValueError: # Planet not found in list, should not happen if civ owns it
                     current_planet_s_value = min_dot_size_px


                # Calculate dynamic offset from planet edge (from user snippet)
                normalized_size_factor = 0.0
                if (max_dot_size_px - min_dot_size_px) > 0: # Avoid division by zero
                    # Convert current_planet_s_value (area) to a linear scale for normalization factor
                    # This assumes s_value is proportional to radius^2. So, take sqrt for linear factor.
                    # Normalize against sqrt of min/max dot sizes.
                    linear_s_value = np.sqrt(current_planet_s_value)
                    linear_min_dot_size = np.sqrt(min_dot_size_px)
                    linear_max_dot_size = np.sqrt(max_dot_size_px)
                    if (linear_max_dot_size - linear_min_dot_size) > 0:
                        normalized_size_factor = (linear_s_value - linear_min_dot_size) / (linear_max_dot_size - linear_min_dot_size)
                normalized_size_factor = min(1.0, max(0.0, normalized_size_factor)) # Clamp between 0 and 1
                
                current_planet_visual_radius_grid = min_expected_planet_radius_grid + \
                    normalized_size_factor * (max_expected_planet_radius_grid - min_expected_planet_radius_grid)

                bar_base_y = planet_pos_y_grid - (max_bar_height_visual / 2) # Common bottom alignment for stat bars

                # --- Military Bar (Right side, first) ---
                military_strength = civ.get_military()
                normalized_military_strength = min(1.0, max(0.0, military_strength / MAX_MILITARY if MAX_MILITARY > 0 else 0))
                military_bar_height_actual = normalized_military_strength * max_bar_height_visual
                
                military_bar_x = planet_pos_x_grid + current_planet_visual_radius_grid + gap_from_planet_edge
                military_bar_y = bar_base_y
                
                if military_bar_height_actual > 0: 
                    rect_mil = Rectangle((military_bar_x, military_bar_y), fixed_bar_width, military_bar_height_actual, 
                                     facecolor='purple', edgecolor='black', linewidth=0.5, zorder=12) # zorder from 6 to 12
                    ax.add_patch(rect_mil)
                    strength_indicator_patches.append(rect_mil)

                # --- Tech Bar (Right side, second) ---
                tech_strength = civ.get_tech()
                normalized_tech_strength = min(1.0, max(0.0, tech_strength / MAX_TECH if MAX_TECH > 0 else 0))
                tech_bar_height_actual = normalized_tech_strength * max_bar_height_visual
                
                tech_bar_x = military_bar_x + fixed_bar_width + gap_between_bars 
                tech_bar_y = bar_base_y

                if tech_bar_height_actual > 0: 
                    rect_tech = Rectangle((tech_bar_x, tech_bar_y), fixed_bar_width, tech_bar_height_actual, 
                                     facecolor='deepskyblue', edgecolor='black', linewidth=0.5, zorder=12) # zorder from 6 to 12
                    ax.add_patch(rect_tech)
                    strength_indicator_patches.append(rect_tech)
                
                # --- Culture Bar (Right side, third) ---
                culture_level = civ.get_culture()
                normalized_culture = min(1.0, max(0.0, culture_level / MAX_CULTURE if MAX_CULTURE > 0 else 0))
                culture_bar_height_actual = normalized_culture * max_bar_height_visual

                culture_bar_x = tech_bar_x + fixed_bar_width + gap_between_bars
                culture_bar_y = bar_base_y

                if culture_bar_height_actual > 0:
                    rect_culture = Rectangle((culture_bar_x, culture_bar_y), fixed_bar_width, culture_bar_height_actual,
                                           facecolor='gold', edgecolor='black', linewidth=0.5, zorder=12) # zorder from 6 to 12
                    ax.add_patch(rect_culture)
                    strength_indicator_patches.append(rect_culture)
                
                # --- Friendliness Bar (Below planet) ---
                friendliness_value = civ.get_friendliness()
                friendliness_bar_width_actual = current_planet_visual_radius_grid * 2.0 # Adjusted from 2.5
                friendliness_bar_x_pos = planet_pos_x_grid - (friendliness_bar_width_actual / 2) # Centered under planet
                friendliness_bar_y_pos = planet_pos_y_grid - current_planet_visual_radius_grid - gap_from_planet_edge - friendliness_bar_height_val 

                friendliness_color = 'yellow' # Default
                if friendliness_value < 0.25:
                    friendliness_color = 'red'
                elif friendliness_value > 0.75:
                    friendliness_color = 'lime'
                
                rect_friendliness = Rectangle((friendliness_bar_x_pos, friendliness_bar_y_pos), 
                                              friendliness_bar_width_actual, friendliness_bar_height_val,
                                              facecolor=friendliness_color, edgecolor='black', linewidth=0.5, zorder=12) # zorder from 6 to 12
                ax.add_patch(rect_friendliness)
                strength_indicator_patches.append(rect_friendliness)

        # For normal frames, return artists that are actively managed
        return [planet_dots, turn_title, end_message_text] + interaction_lines_and_arrows + strength_indicator_patches

    # Use a default interval if model doesn't specify, or use model's preference
    interval_ms = getattr(model, 'LOGICAL_TURN_DURATION_MS', 1000)
    # Get MAX_TURNS from the model instance for save_count
    simulation_max_turns = getattr(model, 'max_turns', 200) # Default to 200 if not found

    def init():
        ''' Custom arg function for funcAnimation().
        Inputs:
            - None.
        Outputs:
            - Returns a list of planet points, title, end message, lines, arrows, and indicator patches.
        '''
        turn_title.set_text('')
        end_message_text.set_visible(False)
        planet_dots.set_offsets(np.empty((0, 2)))
        for item in interaction_lines_and_arrows: item.remove()
        interaction_lines_and_arrows.clear()
        for patch in strength_indicator_patches: patch.remove()
        strength_indicator_patches.clear()
        return [planet_dots, turn_title, end_message_text] + interaction_lines_and_arrows + strength_indicator_patches

    # Create the generator object ONCE before passing it to FuncAnimation
    simulation_frames_generator = model.run_simulation()
    
    ani = animation.FuncAnimation(fig, update, frames=simulation_frames_generator, init_func=init, blit=False, 
                                interval=interval_ms, repeat=False, save_count=simulation_max_turns, cache_frame_data=False)
    # ani.save('simulation_animation.gif', writer='pillow', fps=1000/interval_ms if interval_ms > 0 else 1)
    plt.show()

# TO-DO: Write plot fns based on our established metrics.
