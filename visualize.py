##### DEPENDENCIES #####
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.lines import Line2D # For custom legends
from matplotlib.patches import Rectangle # For military bars
from planet import POPCAP_MAX # Added for scaling planet sizes



##### FUNCTIONS #####
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
    # This function is called for each frame of the animation.
    def update(frame_data):
        # Clear previous frame's elements
        end_message_text.set_visible(False)
        planet_dots.set_visible(True) # Make sure planets are visible by default each frame

        for item in interaction_lines_and_arrows: item.remove()
        interaction_lines_and_arrows.clear()
        for patch in strength_indicator_patches: patch.remove()
        strength_indicator_patches.clear()

        if isinstance(frame_data, str): # Victory message frame
            planet_dots.set_visible(False)
            turn_title.set_text('')
            end_message_text.set_text(frame_data)
            end_message_text.set_visible(True)
            # Return only essential artists when it's just a message
            return [planet_dots, turn_title, end_message_text]

        # Unpack turn data, now including conquest_events
        turn, current_interactions, conquest_events = frame_data 
        turn_title.set_text(f'Turn: {turn}')

        # Identify planets conquered this turn for the flash effect
        conquered_planet_ids_this_turn = {event['planet_id'] for event in conquest_events}

        # Update planet positions and colors.
        planet_positions = [p.get_pos() for p in model.list_planets]
        planet_plot_colors = []
        planet_border_colors_final = [] # Renamed to avoid conflict with loop variable

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
                resource_colors = {'Energy': 'yellow', 'Food': 'green', 'Minerals': 'silver'}
                resource_indices = {'Energy': 0, 'Food': 1, 'Minerals': 2}
                if resources and sum(resources) > 0:
                    dominant_resource_name = None
                    if resources[resource_indices['Energy']] > resources[resource_indices['Food']] and resources[resource_indices['Energy']] > resources[resource_indices['Minerals']]:
                        dominant_resource_name = 'Energy'
                    elif resources[resource_indices['Food']] > resources[resource_indices['Energy']] and resources[resource_indices['Food']] > resources[resource_indices['Minerals']]:
                        dominant_resource_name = 'Food'
                    elif resources[resource_indices['Minerals']] > resources[resource_indices['Energy']] and resources[resource_indices['Minerals']] > resources[resource_indices['Food']]:
                        dominant_resource_name = 'Minerals'
                    else: 
                        if resources[resource_indices['Energy']] >= resources[resource_indices['Food']] and resources[resource_indices['Energy']] >= resources[resource_indices['Minerals']] and resources[resource_indices['Energy']] > 0:
                            dominant_resource_name = 'Energy'
                        elif resources[resource_indices['Food']] >= resources[resource_indices['Energy']] and resources[resource_indices['Food']] >= resources[resource_indices['Minerals']] and resources[resource_indices['Food']] > 0:
                            dominant_resource_name = 'Food'
                        elif resources[resource_indices['Minerals']] >= resources[resource_indices['Energy']] and resources[resource_indices['Minerals']] >= resources[resource_indices['Food']] and resources[resource_indices['Minerals']] > 0:
                            dominant_resource_name = 'Minerals'
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
        
        # planet_border_colors was here, now planet_border_colors_final is built in the loop above

        planet_dots.set_offsets(np.array(planet_positions)[:, ::-1] if planet_positions else np.array([]))
        planet_dots.set_color(planet_plot_colors if planet_plot_colors else 'gray')
        if model.list_planets:
            planet_dots.set_sizes(planet_plot_sizes)
            planet_dots.set_edgecolors(planet_border_colors_final) # Use the final list 
        else:
            planet_dots.set_sizes([])

        # Draw military strength indicators (Vertical Bars)
        fixed_bar_width = 0.2
        max_bar_height_visual = 0.8 # Max height in grid units
        military_bar_color = 'purple'
        tech_bar_color = 'deepskyblue'
        culture_bar_color = 'gold' # Added for culture

        # Constants for dynamic offset calculation
        gap_from_planet_edge = 0.05
        gap_between_bars = 0.05
        min_expected_planet_radius_grid = 0.15 
        max_expected_planet_radius_grid = 0.4  
        # min_dot_size and max_dot_size are already defined in the outer scope (30, 250)

        effective_max_military = getattr(model, 'MOCK_MAX_MILITARY_STRENGTH', 100) 
        effective_max_tech = getattr(model, 'MOCK_MAX_TECH_STRENGTH', 100) 
        effective_max_culture = getattr(model, 'MOCK_MAX_CULTURE', 100) # Added for culture

        for i, p in enumerate(model.list_planets): # Added enumerate for planet_plot_sizes index
            civ_owner = p.get_civ()
            if civ_owner:
                planet_pos_x, planet_pos_y = p.get_pos()[1], p.get_pos()[0] 
                planet_s_value = planet_plot_sizes[i]

                # Calculate dynamic offset from planet edge
                normalized_size_factor = 0.0
                if (max_dot_size - min_dot_size) > 0: # Avoid division by zero
                    normalized_size_factor = (planet_s_value - min_dot_size) / (max_dot_size - min_dot_size)
                normalized_size_factor = min(1.0, max(0.0, normalized_size_factor)) # Clamp between 0 and 1
                
                current_planet_visual_radius_grid = min_expected_planet_radius_grid + \
                    normalized_size_factor * (max_expected_planet_radius_grid - min_expected_planet_radius_grid)

                bar_base_y = planet_pos_y - (max_bar_height_visual / 2)

                # --- Military Bar (Right side, first) ---
                military_strength = civ_owner.get_military()
                normalized_military_strength = min(1.0, max(0.0, military_strength / effective_max_military))
                military_bar_height_actual = normalized_military_strength * max_bar_height_visual
                
                military_bar_x = planet_pos_x + current_planet_visual_radius_grid + gap_from_planet_edge
                # military_bar_y = planet_pos_y - (military_bar_height_actual / 2) # Old: Centered vertically
                military_bar_y = bar_base_y # New: Common bottom alignment
                
                if military_bar_height_actual > 0: 
                    rect_mil = Rectangle((military_bar_x, military_bar_y), fixed_bar_width, military_bar_height_actual, 
                                     facecolor=military_bar_color, edgecolor='black', linewidth=0.5, zorder=6)
                    ax.add_patch(rect_mil)
                    strength_indicator_patches.append(rect_mil)

                # --- Tech Bar (Right side, second) ---
                tech_strength = civ_owner.get_tech()
                normalized_tech_strength = min(1.0, max(0.0, tech_strength / effective_max_tech))
                tech_bar_height_actual = normalized_tech_strength * max_bar_height_visual
                
                tech_bar_x = military_bar_x + fixed_bar_width + gap_between_bars 
                # tech_bar_y = planet_pos_y - (tech_bar_height_actual / 2) # Old: Centered vertically
                tech_bar_y = bar_base_y # New: Common bottom alignment

                if tech_bar_height_actual > 0: 
                    rect_tech = Rectangle((tech_bar_x, tech_bar_y), fixed_bar_width, tech_bar_height_actual, 
                                     facecolor=tech_bar_color, edgecolor='black', linewidth=0.5, zorder=6)
                    ax.add_patch(rect_tech)
                    strength_indicator_patches.append(rect_tech)
                
                # --- Culture Bar (Right side, third) ---
                culture_level = civ_owner.get_culture()
                normalized_culture = min(1.0, max(0.0, culture_level / effective_max_culture))
                culture_bar_height_actual = normalized_culture * max_bar_height_visual

                culture_bar_x = tech_bar_x + fixed_bar_width + gap_between_bars
                culture_bar_y = bar_base_y

                if culture_bar_height_actual > 0:
                    rect_culture = Rectangle((culture_bar_x, culture_bar_y), fixed_bar_width, culture_bar_height_actual,
                                           facecolor=culture_bar_color, edgecolor='black', linewidth=0.5, zorder=6)
                    ax.add_patch(rect_culture)
                    strength_indicator_patches.append(rect_culture)
                
                # --- Friendliness Bar (Below planet) ---
                friendliness_value = civ_owner.get_friendliness()
                friendliness_bar_height = 0.15
                friendliness_bar_width = current_planet_visual_radius_grid * 2.5 # Make it a bit wider than planet
                friendliness_bar_x = planet_pos_x - (friendliness_bar_width / 2) # Centered under planet
                # Position below the planet dot, considering planet's visual radius
                friendliness_bar_y = planet_pos_y - current_planet_visual_radius_grid - gap_from_planet_edge - friendliness_bar_height 

                friendliness_color = 'yellow' # Default
                if friendliness_value < 0.25:
                    friendliness_color = 'red'
                elif friendliness_value > 0.75:
                    friendliness_color = 'lime' # Consistent with legend
                
                rect_friendliness = Rectangle((friendliness_bar_x, friendliness_bar_y), 
                                              friendliness_bar_width, friendliness_bar_height,
                                              facecolor=friendliness_color, edgecolor='black', linewidth=0.5, zorder=6)
                ax.add_patch(rect_friendliness)
                strength_indicator_patches.append(rect_friendliness)

        # Draw static interaction lines (war, base trade lines)
        for interaction in current_interactions:
            civ1, civ2 = interaction['civ1'], interaction['civ2']
            if list(civ1.get_planets().values()) and list(civ2.get_planets().values()):
                pos1, pos2 = list(civ1.get_planets().values())[0].get_pos(), list(civ2.get_planets().values())[0].get_pos()
                if interaction['type'] == 'trade':
                    line, = ax.plot([pos1[1], pos2[1]], [pos1[0], pos2[0]], color='green', linestyle=':', linewidth=1.5, zorder=10)
                    interaction_lines_and_arrows.append(line)
                elif interaction['type'] == 'war':
                    attacker_obj = interaction.get('attacker', civ1)
                    defender_target_initial_pos = interaction.get('defender_target_planet_initial_pos')
                    if list(attacker_obj.get_planets().values()) and defender_target_initial_pos:
                        start_pos = list(attacker_obj.get_planets().values())[0].get_pos()
                        line, = ax.plot([start_pos[1], defender_target_initial_pos[1]], [start_pos[0], defender_target_initial_pos[0]], color='red', lw=2.5, zorder=10)
                        interaction_lines_and_arrows.append(line)
                        arrow = ax.annotate("", xy=(defender_target_initial_pos[1], defender_target_initial_pos[0]), xytext=(start_pos[1], start_pos[0]), arrowprops=dict(arrowstyle="->",color='red',lw=1.5,shrinkA=5,shrinkB=5),zorder=11)
                        interaction_lines_and_arrows.append(arrow)
        
        return [planet_dots, turn_title, end_message_text] + strength_indicator_patches + interaction_lines_and_arrows

    # Use a default interval if model doesn't specify, or use model's preference
    interval_ms = getattr(model, 'LOGICAL_TURN_DURATION_MS', 1000)

    ani = animation.FuncAnimation(fig, update, frames=model.run_simulation, blit=True, 
                                interval=interval_ms, repeat=False)
    ani.save('simulation_animation.gif', writer='pillow', fps=1000/interval_ms if interval_ms > 0 else 1)
    #plt.show()

# TO-DO: Write plot fns based on our established metrics.


##### MOCK OBJECTS FOR TESTING #####
MOCK_MAX_MILITARY_STRENGTH = 100 # Define for mock scenario scaling
MOCK_MAX_TECH_STRENGTH = 100 # Define for mock tech scaling
MOCK_MAX_CULTURE = 100 # Align with civ.py MAX_CULTURE

class MockPlanet:
    def __init__(self, id, pos_x, pos_y, population_cap, resources=None, civ=None):
        self.id = id
        self.pos_x = pos_x
        self.pos_y = pos_y
        self._population_cap = population_cap
        self.civ_owner = civ
        # Resources: [Energy, Food, Minerals]
        self._resources = resources if resources else [0, 0, 0]

    def get_id(self):
        return self.id

    def get_pos(self):
        return (self.pos_x, self.pos_y)

    def get_population_cap(self):
        return self._population_cap

    def get_civ(self):
        return self.civ_owner

    def assign_civ(self, civ):
        self.civ_owner = civ

    def get_resources(self):
        return self._resources

class MockCiv:
    def __init__(self, id, current_population=0.0, total_population_cap=0.0, military=0, tech=0, culture=0, friendliness=0.5):
        self.id = id
        self._current_population = current_population
        self._total_population_cap = total_population_cap
        self.planets = {} # Stores MockPlanet objects
        self._military = military
        self._tech = tech
        self._culture = culture # Added culture
        self.friendliness = friendliness # Added friendliness

    def get_id(self):
        return self.id

    def get_population(self):
        return self._current_population

    def get_population_cap(self):
        return self._total_population_cap
    
    def get_planets(self): # Required for interaction drawing logic, though not strictly for sizing
        return self.planets

    def get_military(self):
        return self._military

    def get_tech(self):
        return self._tech

    def get_culture(self):
        return self._culture # Added culture getter

    def get_friendliness(self): # Added getter
        return self.friendliness

    def add_planet(self, planet):
        self.planets[planet.get_id()] = planet
        planet.assign_civ(self)
        self._total_population_cap += planet.get_population_cap()
        # Simple population distribution for testing sizing
        if self._total_population_cap > 0:
             # For testing, let's assume population is somewhat related to total capacity
             # This is a simplification for testing planet sizing logic
            self._current_population = self._total_population_cap * 0.5 
        # Pass the constant to the model instance for access in update() if needed by getattr
        self.MOCK_MAX_MILITARY_STRENGTH = MOCK_MAX_MILITARY_STRENGTH 
        self.MOCK_MAX_TECH_STRENGTH = MOCK_MAX_TECH_STRENGTH
        self.MOCK_MAX_CULTURE = MOCK_MAX_CULTURE # Pass to model instance

class MockModel:
    def __init__(self, num_planets, grid_height, grid_width):
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.grid = np.zeros(shape=(grid_height, grid_width))
        self.list_planets = []
        self.list_civs = []
        self._setup_scenario(num_planets)
        self.MOCK_MAX_MILITARY_STRENGTH = MOCK_MAX_MILITARY_STRENGTH 
        self.MOCK_MAX_TECH_STRENGTH = MOCK_MAX_TECH_STRENGTH
        self.MOCK_MAX_CULTURE = MOCK_MAX_CULTURE
        self.LOGICAL_TURN_DURATION_MS = 1000
        self.targeted_planet_for_conquest_id = None 
        # Stores { (attacker_id, defender_id): {'end_turn': turn_num, 'initial_target_pos': (x,y)} }
        self.war_active_details = {} 

    def _setup_scenario(self, num_planets):
        # Create Civs
        civ1 = MockCiv(id=1, military=MOCK_MAX_MILITARY_STRENGTH * 0.75, tech=MOCK_MAX_TECH_STRENGTH * 0.5, culture=MOCK_MAX_CULTURE * 0.20, friendliness=0.15) # Unfriendly
        civ2 = MockCiv(id=2, military=MOCK_MAX_MILITARY_STRENGTH * 0.25, tech=MOCK_MAX_TECH_STRENGTH * 0.9, culture=MOCK_MAX_CULTURE * 0.85, friendliness=0.85) # Friendly
        self.list_civs.extend([civ1, civ2])

        # Create Planets
        p1 = MockPlanet(id=1, pos_x=5, pos_y=5, population_cap=POPCAP_MAX * 0.8, resources=[100, 20, 30])
        civ1.add_planet(p1)
        self.list_planets.append(p1)

        p2 = MockPlanet(id=2, pos_x=7, pos_y=7, population_cap=POPCAP_MAX * 0.2, resources=[10, 80, 15])
        civ1.add_planet(p2) 
        self.list_planets.append(p2)

        # This planet (p3) is owned by civ2 and will be targeted for conquest by civ1
        p3 = MockPlanet(id=3, pos_x=10, pos_y=10, population_cap=POPCAP_MAX * 0.5, resources=[40, 30, 90])
        civ2.add_planet(p3) 
        self.list_planets.append(p3)
        
        p4 = MockPlanet(id=4, pos_x=15, pos_y=15, population_cap=POPCAP_MAX * 0.9, resources=[120, 50, 50])
        self.list_planets.append(p4)

        p5 = MockPlanet(id=5, pos_x=3, pos_y=12, population_cap=POPCAP_MAX * 0.1, resources=[10, 10, 10])
        self.list_planets.append(p5)

        # Planet with zero resources
        p6 = MockPlanet(id=6, pos_x=12, pos_y=3, population_cap=POPCAP_MAX * 0.3, resources=[0,0,0])
        self.list_planets.append(p6)

        # Ensure number of planets matches num_planets for consistency if needed, add more generic ones
        current_planet_count = len(self.list_planets)
        for i in range(num_planets - current_planet_count):
            px, py = np.random.randint(0, self.grid_height), np.random.randint(0, self.grid_width)
            # Ensure unique positions crude check
            while any(p.get_pos() == (px,py) for p in self.list_planets):
                 px, py = np.random.randint(0, self.grid_height), np.random.randint(0, self.grid_width)
            p_new = MockPlanet(id=6+i+1, pos_x=px, pos_y=py, population_cap=POPCAP_MAX * np.random.uniform(0.05, 0.6), 
                               resources=[np.random.randint(0,50) for _ in range(3)])
            self.list_planets.append(p_new)

    def run_simulation(self):
        self.targeted_planet_for_conquest_id = None 
        self.war_active_details.clear()

        for t_logical in range(1, 10):
            interactions_for_logical_turn = []
            conquest_events_for_turn = [] 

            active_war_keys_to_remove = []
            for (attacker_id, defender_id), war_info in self.war_active_details.items():
                if t_logical <= war_info['end_turn']:
                    attacker_civ_obj = next((c for c in self.list_civs if c.id == attacker_id), None)
                    defender_civ_obj = next((c for c in self.list_civs if c.id == defender_id), None)
                    initial_target_pos = war_info['initial_target_pos']
                    
                    if attacker_civ_obj and defender_civ_obj and attacker_civ_obj.get_planets() and initial_target_pos:
                        # Add war interaction for ongoing war, even if it was also added on declaration turn.
                        # The visualization will draw one line if the civs and type match.
                        interactions_for_logical_turn.append({
                            'civ1': attacker_civ_obj, 
                            'civ2': defender_civ_obj, 
                            'type': 'war', 
                            'attacker': attacker_civ_obj, 
                            'defender_target_planet_initial_pos': initial_target_pos # Use stored initial target pos
                        })
                else:
                    active_war_keys_to_remove.append((attacker_id, defender_id))
            
            for key in active_war_keys_to_remove:
                del self.war_active_details[key]
                print(f"Turn {t_logical}: War between Civ {key[0]} and Civ {key[1]} has ended.")

            if t_logical % 3 == 0 and len(self.list_civs) >= 2:
                civ1_trade, civ2_trade = self.list_civs[0], self.list_civs[1]
                if civ1_trade.get_planets() and civ2_trade.get_planets():
                    interactions_for_logical_turn.append({'civ1': civ1_trade, 'civ2': civ2_trade, 'type': 'trade'})
            
            if t_logical == 5 and len(self.list_civs) >= 2: 
                attacker_civ = self.list_civs[0] 
                defender_civ = self.list_civs[1] 
                war_key = (attacker_civ.get_id(), defender_civ.get_id())

                if war_key not in self.war_active_details: 
                    target_planet_for_war = None
                    if list(defender_civ.get_planets().values()):
                        target_planet_for_war = list(defender_civ.get_planets().values())[0] 
                    
                    if attacker_civ.get_planets() and target_planet_for_war:
                        initial_target_pos_for_line = target_planet_for_war.get_pos()
                        self.targeted_planet_for_conquest_id = target_planet_for_war.get_id()
                        self.war_active_details[war_key] = {
                            'end_turn': 7, 
                            'initial_target_pos': initial_target_pos_for_line
                        }
                        print(f"Turn {t_logical}: War declared by Civ {attacker_civ.get_id()} on Civ {defender_civ.get_id()}, targeting planet {target_planet_for_war.get_id()}. War active until turn 7.")
                        
                        # Explicitly add war interaction for the declaration turn
                        interactions_for_logical_turn.append({
                            'civ1': attacker_civ, 
                            'civ2': defender_civ, 
                            'type': 'war', 
                            'attacker': attacker_civ, 
                            'defender_target_planet_initial_pos': initial_target_pos_for_line
                        })

            if t_logical == 6 and self.targeted_planet_for_conquest_id is not None and len(self.list_civs) >=2:
                conquering_civ = self.list_civs[0] 
                original_owning_civ = next((c for c in self.list_civs if c.id == 2), None) 
                planet_to_be_conquered = next((p for p in self.list_planets if p.get_id() == self.targeted_planet_for_conquest_id), None)

                if planet_to_be_conquered and original_owning_civ and planet_to_be_conquered.get_civ() == original_owning_civ:
                    old_owner_civ_id = original_owning_civ.get_id()
                    original_owning_civ.planets.pop(planet_to_be_conquered.get_id(), None)
                    original_owning_civ._total_population_cap -= planet_to_be_conquered.get_population_cap() 
                    original_owning_civ._current_population = original_owning_civ._total_population_cap * 0.5 
                    conquering_civ.add_planet(planet_to_be_conquered) 
                    conquering_civ._current_population = conquering_civ._total_population_cap * 0.6 
                    conquest_events_for_turn.append({
                        'planet_id': planet_to_be_conquered.get_id(),
                        'new_owner_civ_id': conquering_civ.get_id(),
                        'old_owner_civ_id': old_owner_civ_id
                    })
                    print(f"Turn {t_logical}: Planet {planet_to_be_conquered.get_id()} (was Civ {old_owner_civ_id}) conquered by Civ {conquering_civ.get_id()}")
                    self.targeted_planet_for_conquest_id = None 
                elif planet_to_be_conquered and planet_to_be_conquered.get_civ() != conquering_civ : 
                    old_owner_civ_id = None 
                    conquering_civ.add_planet(planet_to_be_conquered)
                    conquering_civ._current_population = conquering_civ._total_population_cap * 0.6
                    conquest_events_for_turn.append({
                        'planet_id': planet_to_be_conquered.get_id(),
                        'new_owner_civ_id': conquering_civ.get_id(),
                        'old_owner_civ_id': old_owner_civ_id
                    })
                    print(f"Turn {t_logical}: Unowned Planet {planet_to_be_conquered.get_id()} conquered by Civ {conquering_civ.get_id()}")
                    self.targeted_planet_for_conquest_id = None

            yield (t_logical, interactions_for_logical_turn, conquest_events_for_turn) 
        
        final_message = "Test simulation finished."
        # Yield end message with empty lists for interactions and conquests
        yield (final_message, [], []) 
        yield (final_message, [], [])
        yield (final_message, [], [])


if __name__ == "__main__":
    print("Running visualization in test mode with mock data...")
    # Create a mock simulation model
    # Using values similar to init.py for consistency in grid size if applicable
    mock_simulation_model = MockModel(num_planets=10, grid_height=30, grid_width=30)
    
    # Start the visualization with the mock model
    visualize_simulation(mock_simulation_model)
