import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import networkx as nx # Added for network graph plotting

# Assuming historical_data is a list of dictionaries, where each dictionary represents a turn:
# historical_data = [
#     {
#         'turn': 1,
#         'civ_data': {
#             0: {'population': 100, 'tech': 10, ...},
#             1: {'population': 120, 'tech': 12, ...}
#         }
#     },
#     {
#         'turn': 2,
#         'civ_data': {
#             0: {'population': 110, 'tech': 15, ...},
#             1: {'population': 130, 'tech': 18, ...}
#         }
#     },
#     ...
# ]

def plot_line_chart(historical_data, attributes, civ_ids, civ_data_key='civ_data', title=None, ylabels=None, use_secondary_yaxis=True, save_path=None):
    """
    Generates a time-series line chart. Behavior adapts based on inputs:
    1. Single attribute string, list of civ_ids: Plots the attribute for each civ.
    2. List of attributes, single civ_id: Plots each attribute for that civ (supports secondary y-axis for 2 attributes).

    Args:
        historical_data (list): List of turn data snapshots.
        attributes (str or list of str): The attribute name (str) or a list of attribute names (list of str).
        civ_ids (any or list of any): A single civ ID (int/str) or a list of civ IDs.
                                       If None when attributes is a str, plots for all civs.
        civ_data_key (str, optional): Key in historical_data for civ data. Defaults to 'civ_data'.
        title (str, optional): Plot title.
        ylabels (str or list of str, optional): Y-axis label(s).
                                                If attributes is a list, ylabels can be a corresponding list.
                                                If attributes is a str, ylabels should be a str.
        use_secondary_yaxis (bool, optional): If True and plotting 2 attributes for a single civ, 
                                            uses a secondary y-axis. Defaults to True.
        save_path (str, optional): Path to save plot. If None, shows plot. Defaults to None.
    """
    if not historical_data:
        print("Historical data is empty. Cannot generate line chart.")
        return

    fig, ax1 = plt.subplots(figsize=(12, 7))
    plt.xlabel("Turn")
    plot_title_text = title
    lines_for_legend = []
    colors = plt.cm.get_cmap('tab10').colors
    turns = [data['turn'] for data in historical_data]

    if isinstance(attributes, str):
        attribute_name = attributes
        target_civ_ids = []
        if civ_ids is None:
            all_ids = set()
            for data_turn in historical_data:
                if civ_data_key in data_turn:
                    all_ids.update(data_turn[civ_data_key].keys())
            target_civ_ids = sorted(list(all_ids))
        elif isinstance(civ_ids, list):
            target_civ_ids = civ_ids
        else: 
            target_civ_ids = [civ_ids]

        if not target_civ_ids:
            print(f"No civs specified or found for attribute '{attribute_name}'.")
            plt.close(fig)
            return
            
        ax1.set_ylabel(ylabels if isinstance(ylabels, str) else attribute_name.replace('_', ' ').capitalize())
        if not plot_title_text:
            plot_title_text = f'{attribute_name.replace("_", " ").capitalize()} Over Time'

        for i, civ_id_val in enumerate(target_civ_ids):
            attr_values = []
            valid_turns = []
            for turn_idx, data_turn in enumerate(historical_data):
                civ_data = data_turn.get(civ_data_key, {}).get(civ_id_val)
                if civ_data and civ_data.get('status') != 'eliminated' and attribute_name in civ_data:
                    attr_values.append(civ_data[attribute_name])
                    valid_turns.append(turns[turn_idx])
            if valid_turns:
                line, = ax1.plot(valid_turns, attr_values, marker='.', linestyle='-', label=f'Civ {civ_id_val}', color=colors[i % len(colors)])
                lines_for_legend.append(line)

    elif isinstance(attributes, list) and not isinstance(civ_ids, list) and civ_ids is not None:
        attribute_names = attributes
        civ_id_val = civ_ids
        if not plot_title_text:
            plot_title_text = f'Attributes for Civ {civ_id_val} Over Time'

        civ_data_over_time = {attr: [] for attr in attribute_names}
        valid_turns_for_plot = []
        processed_turns_indices = set()

        for turn_idx, data_turn in enumerate(historical_data):
            actual_turn = turns[turn_idx]
            if actual_turn in processed_turns_indices: continue
            civ_specific_data = data_turn.get(civ_data_key, {}).get(civ_id_val)
            if civ_specific_data and civ_specific_data.get('status') != 'eliminated':
                all_attrs_present = True
                current_turn_val_dict = {}
                for attr_name in attribute_names:
                    if attr_name in civ_specific_data:
                        current_turn_val_dict[attr_name] = civ_specific_data[attr_name]
                    else:
                        all_attrs_present = False; break
                if all_attrs_present:
                    valid_turns_for_plot.append(actual_turn)
                    processed_turns_indices.add(actual_turn)
                    for attr_name in attribute_names:
                        civ_data_over_time[attr_name].append(current_turn_val_dict[attr_name])
        
        if valid_turns_for_plot:
            sorted_indices = np.argsort(valid_turns_for_plot)
            valid_turns_for_plot = [valid_turns_for_plot[i] for i in sorted_indices]
            for attr_name in attribute_names:
                civ_data_over_time[attr_name] = [civ_data_over_time[attr_name][i] for i in sorted_indices]
        
        if not valid_turns_for_plot:
            print(f"No data found for Civ {civ_id_val} for attributes {attribute_names}."); plt.close(fig); return

        attr1_name = attribute_names[0]
        ylabel1_text = (ylabels[0] if isinstance(ylabels, list) and len(ylabels) > 0 else attr1_name.replace('_',' ').capitalize())
        color1 = colors[0]
        ax1.set_ylabel(ylabel1_text, color=color1)
        line1, = ax1.plot(valid_turns_for_plot, civ_data_over_time[attr1_name], color=color1, marker='.', linestyle='-', label=attr1_name.replace('_',' ').capitalize())
        ax1.tick_params(axis='y', labelcolor=color1); lines_for_legend.append(line1)

        if len(attribute_names) == 2 and use_secondary_yaxis:
            attr2_name = attribute_names[1]
            ylabel2_text = (ylabels[1] if isinstance(ylabels, list) and len(ylabels) > 1 else attr2_name.replace('_',' ').capitalize())
            color2 = colors[1]; ax2 = ax1.twinx(); ax2.set_ylabel(ylabel2_text, color=color2)
            line2, = ax2.plot(valid_turns_for_plot, civ_data_over_time[attr2_name], color=color2, marker='x', linestyle='--', label=attr2_name.replace('_',' ').capitalize())
            ax2.tick_params(axis='y', labelcolor=color2); lines_for_legend.append(line2)
        elif len(attribute_names) > 1:
            for i, attr_name in enumerate(attribute_names[1:], start=1):
                label_i_text = (ylabels[i] if isinstance(ylabels, list) and len(ylabels) > i else attr_name.replace('_',' ').capitalize())
                color_i = colors[i % len(colors)]; marker_i = ['o', 's', '^', 'D', 'v'][i % 5]
                line_i, = ax1.plot(valid_turns_for_plot, civ_data_over_time[attr_name], color=color_i, marker=marker_i, linestyle=':', label=label_i_text)
                lines_for_legend.append(line_i)
    else:
        print("Invalid combination of 'attributes' and 'civ_ids' parameters for plot_line_chart.")
        print("Usage: attributes=str, civ_ids=list/None OR attributes=list, civ_ids=single_id"); plt.close(fig); return

    plt.title(plot_title_text)
    if lines_for_legend: ax1.legend(handles=lines_for_legend, loc='best')
    ax1.grid(True); fig.tight_layout()
    if save_path: plt.savefig(save_path); print(f"Line chart saved to {save_path}"); plt.close(fig)
    else: plt.show()

def plot_scatter(historical_data, x_attribute, y_attribute, civ_ids=None, civ_data_key='civ_data', color_attribute=None, size_attribute=None, title=None, xlabel=None, ylabel=None, save_path=None, colorbar_label=None):
    """
    Generates a scatter plot from historical simulation data for specified civilizations.
    Args:
        historical_data (list): List of turn data snapshots.
        x_attribute (str): Attribute for the X-axis.
        y_attribute (str): Attribute for the Y-axis.
        civ_ids (list, optional): Specific civ_ids to include. If None, uses all civs from all turns.
        civ_data_key (str, optional): Key in historical_data for civ data. Defaults to 'civ_data'.
        color_attribute (str, optional): Attribute to use for coloring points. Can be categorical or numerical.
        size_attribute (str, optional): Attribute to use for sizing points.
        title (str, optional): Plot title.
        xlabel (str, optional): X-axis label.
        ylabel (str, optional): Y-axis label.
        save_path (str, optional): Path to save the plot. If None, shows the plot.
        colorbar_label (str, optional): Label for the color bar (if color_attribute is numerical).
    """
    if not historical_data: print("Historical data is empty. Cannot generate scatter plot."); return
    x_values, y_values, color_values, size_values, point_labels = [], [], [], [], []
    all_civ_ids_in_history = set()
    for data_turn in historical_data:
        if civ_data_key in data_turn: all_civ_ids_in_history.update(data_turn[civ_data_key].keys())
    
    ids_to_process = civ_ids
    if ids_to_process is None: ids_to_process = sorted(list(all_civ_ids_in_history))
    elif not isinstance(ids_to_process, list): ids_to_process = [ids_to_process]

    for data_turn in historical_data:
        turn = data_turn['turn']
        for civ_id_val in ids_to_process:
            civ_data = data_turn.get(civ_data_key, {}).get(civ_id_val)
            if civ_data and civ_data.get('status') != 'eliminated' and x_attribute in civ_data and y_attribute in civ_data:
                x_values.append(civ_data[x_attribute]); y_values.append(civ_data[y_attribute])
                point_labels.append(f"C{civ_id_val} T{turn}") # Reverted to C for Civ
                if color_attribute: color_values.append(civ_data.get(color_attribute))
                if size_attribute: size_val = civ_data.get(size_attribute); size_values.append(size_val * 50 if size_val is not None else 50)
    
    if not x_values: print(f"No data for '{x_attribute}' vs '{y_attribute}' under '{civ_data_key}'."); return
    plt.figure(figsize=(12, 7)); scatter_kwargs = {}; is_numeric_color = False
    if color_attribute and color_values:
        non_none_cv = [cv for cv in color_values if cv is not None]
        if non_none_cv: is_numeric_color = all(isinstance(cv, (int, float)) for cv in non_none_cv)
        if is_numeric_color: scatter_kwargs['c'] = [cv if isinstance(cv, (int,float)) else np.nan for cv in color_values]; scatter_kwargs['cmap'] = 'viridis'
        else: 
            unique_cats = sorted(list(set(non_none_cv))); cat_to_color = {cat: cm.get_cmap('tab10')(i % 10) for i, cat in enumerate(unique_cats)}
            scatter_kwargs['c'] = [cat_to_color.get(cv) for cv in color_values]
            for cat, color_val in cat_to_color.items(): plt.scatter([], [], color=color_val, label=str(cat))
            plt.legend(title=color_attribute.replace('_', ' ').capitalize())
    if size_attribute and size_values: scatter_kwargs['s'] = size_values
    elif not size_attribute: scatter_kwargs['s'] = 50
    plt.scatter(x_values, y_values, **scatter_kwargs, alpha=0.7, edgecolors='k', linewidth=0.5)
    plt.xlabel(xlabel if xlabel else x_attribute.replace('_', ' ').capitalize()); plt.ylabel(ylabel if ylabel else y_attribute.replace('_', ' ').capitalize())
    plt.title(title if title else f'{y_attribute.replace("_", " ").capitalize()} vs. {x_attribute.replace("_", " ").capitalize()}')
    if color_attribute and 'c' in scatter_kwargs and is_numeric_color:
        cbar = plt.colorbar(); cbar.set_label(colorbar_label if colorbar_label else color_attribute.replace('_', ' ').capitalize())
    plt.grid(True); plt.tight_layout()
    if save_path: plt.savefig(save_path); print(f"Scatter plot saved to {save_path}"); plt.close()
    else: plt.show()

def plot_bar_chart(data, categories=None, title=None, xlabel=None, ylabel=None, legend_title=None, save_path=None, bar_width=0.35, is_grouped=False, group_labels=None):
    """
    Generates a bar chart (simple or grouped) from provided data.

    Args:
        data (dict or list of lists/tuples): 
            For simple bar chart: A dict like {'cat1': val1, 'cat2': val2} or a list of values [val1, val2].
            For grouped bar chart: A dict like {'cat1': [grp1_val, grp2_val], 'cat2': [grp1_val, grp2_val]},
                                   or a list of lists/tuples, e.g., [[cat1_grp1, cat1_grp2], [cat2_grp1, cat2_grp2]].
                                   The inner lists/tuples represent values for each group within a category.
        categories (list of str, optional): Labels for the categories (x-axis ticks). 
                                          If None and data is a dict, keys are used.
                                          Required if data is a list of values/list of lists.
        title (str, optional): The title of the plot.
        xlabel (str, optional): Label for the x-axis.
        ylabel (str, optional): Label for the y-axis.
        legend_title (str, optional): Title for the legend (used in grouped charts).
        save_path (str, optional): Path to save the plot image. If None, shows the plot.
        bar_width (float, optional): Width of the bars. Defaults to 0.35.
        is_grouped (bool, optional): True if generating a grouped bar chart. Defaults to False.
        group_labels (list of str, optional): Labels for the groups in a grouped bar chart. Required if is_grouped is True.
    """
    if not data:
        print("Data is empty. Cannot generate bar chart.")
        return

    fig, ax = plt.subplots(figsize=(10, 7))

    if isinstance(data, dict):
        if not categories:
            categories = list(data.keys())
        values = list(data.values())
    elif isinstance(data, list):
        if not categories:
            # If data is [val1, val2], categories should be provided or auto-generated as indices
            if not all(isinstance(item, (list, tuple)) for item in data): # Simple list of values
                 categories = [str(i) for i in range(len(data))]
            # For grouped, categories list must be provided matching the outer list length

        values = data
    else:
        print("Data format not recognized. Use dict or list of values/lists.")
        return
    
    if not categories:
        print("Categories must be provided if data is a list.")
        return

    x = np.arange(len(categories))

    if is_grouped:
        if not group_labels:
            print("group_labels are required for a grouped bar chart.")
            return
        num_groups = len(group_labels)
        if not values or not isinstance(values[0], (list, tuple)) or len(values[0]) != num_groups:
            print(f"For grouped chart, data for each category must be a list/tuple of {num_groups} values.")
            return
        
        total_width = bar_width * num_groups
        # Calculate offsets for each group
        offsets = np.arange(-(total_width - bar_width) / 2, (total_width - bar_width) / 2 + bar_width, bar_width)
        if len(offsets) > num_groups: # Adjust if arange overshoots due to float precision
            offsets = offsets[:num_groups]
        elif len(offsets) < num_groups:
             print("Error in calculating bar offsets for grouped chart.") # Should not happen with correct num_groups and bar_width
             return

        rects_list = []
        for i, label in enumerate(group_labels):
            group_values = [val[i] for val in values]
            rects = ax.bar(x + offsets[i], group_values, bar_width, label=label)
            rects_list.append(rects)
        
        if legend_title:
            ax.legend(title=legend_title)
        else:
            ax.legend()

    else: # Simple bar chart
        if values and isinstance(values[0], (list, tuple)):
            print("For a simple bar chart, data for each category should be a single value, not a list/tuple. Set is_grouped=True if this is intended.")
            return
        rects = ax.bar(x, values, bar_width)

    ax.set_ylabel(ylabel if ylabel else 'Values')
    ax.set_xlabel(xlabel if xlabel else 'Categories')
    ax.set_title(title if title else 'Bar Chart')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Bar chart saved to {save_path}")
        plt.close(fig)
    else:
        plt.show()

def plot_network_graph(nodes_data, edges_data, title=None, save_path=None, show_edge_labels=True, node_size=700, layout_type='spring'):
    """
    Generates and plots a network graph.

    Args:
        nodes_data (list): A list of node identifiers (e.g., [0, 1, 2] for civ_ids).
                           Alternatively, a list of tuples (node_id, attr_dict) for node attributes.
        edges_data (list of tuples): A list of edges. Each edge can be a simple (source, target) tuple,
                                     or (source, target, attr_dict) where attr_dict can contain 'weight',
                                     'label', 'color', etc. for the edge.
        title (str, optional): The title of the plot.
        save_path (str, optional): Path to save the plot image. If None, shows the plot.
        show_edge_labels (bool, optional): If True, attempts to draw edge labels (e.g., from 'label' or 'weight' attribute).
        node_size (int, optional): Size of the nodes in the plot.
        layout_type (str, optional): Layout algorithm from networkx (e.g., 'spring', 'circular', 'kamada_kawai').
    """
    if not nodes_data:
        print("Nodes data is empty. Cannot generate network graph.")
        return

    G = nx.Graph() # Or nx.DiGraph() for directed graphs

    # Add nodes
    node_ids = []
    for node_entry in nodes_data:
        if isinstance(node_entry, tuple) and len(node_entry) == 2 and isinstance(node_entry[1], dict):
            G.add_node(node_entry[0], **node_entry[1])
            node_ids.append(node_entry[0])
        else:
            G.add_node(node_entry)
            node_ids.append(node_entry)
    
    # Add edges
    parsed_edges = []
    for edge in edges_data:
        if len(edge) == 2:
            G.add_edge(edge[0], edge[1])
            parsed_edges.append((edge[0], edge[1], {}))
        elif len(edge) == 3 and isinstance(edge[2], dict):
            G.add_edge(edge[0], edge[1], **edge[2])
            parsed_edges.append(edge)
        else:
            print(f"Skipping invalid edge format: {edge}")

    plt.figure(figsize=(10, 8))

    # Choose layout
    if layout_type == 'spring':
        pos = nx.spring_layout(G, k=0.5, iterations=50) # k adjusts spacing, iterations for convergence
    elif layout_type == 'circular':
        pos = nx.circular_layout(G)
    elif layout_type == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G) # Default

    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color='skyblue', alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=10)

    # Edge drawing with customization
    edge_widths = [G[u][v].get('weight', 1) for u,v in G.edges()] # Default weight 1
    edge_colors = [G[u][v].get('color', 'gray') for u,v in G.edges()] # Default color gray
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, alpha=0.6)

    if show_edge_labels:
        edge_labels = {}
        for u, v, attrs in parsed_edges:
            label_val = attrs.get('label', attrs.get('weight')) # Prefer 'label', fallback to 'weight'
            if label_val is not None:
                edge_labels[(u,v)] = str(label_val)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    plt.title(title if title else 'Network Graph')
    plt.axis('off') # Turn off the axis
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path)
        print(f"Network graph saved to {save_path}")
        plt.close()
    else:
        plt.show()

def generate_h1_plots(historical_data, civ_data_key='civ_data', save_path_prefix='h1_', N_TURNS_LOOKAHEAD_H1=5):
    """
    Generates and saves plots specific to Hypothesis 1:
    H1: Rapid tech growth accelerates military power, increasing war initiation risk.
    
    This involves:
    1. Pre-processing data to add 'did_initiate_war_in_next_5_turns'.
    2. Generating a scatter plot of Tech vs. Military, colored by war initiation.
    3. Generating correlated line charts for selected civs for Tech, Military, and War Initiations.
    """
    if not historical_data:
        print("H1 Plots: Historical data is empty. Cannot generate plots.")
        return

    # --- Pre-processing for H1: Add 'did_initiate_war_in_next_5_turns' --- 
    # Create a deep copy to avoid modifying the original mock_historical_data if it's used elsewhere
    processed_historical_data = [turn.copy() for turn in historical_data] # Shallow copy of list
    for i in range(len(processed_historical_data)):
        processed_historical_data[i][civ_data_key] = processed_historical_data[i].get(civ_data_key, {}).copy() # Shallow copy of civ_data dict
        for civ_id_key in processed_historical_data[i][civ_data_key]:
            processed_historical_data[i][civ_data_key][civ_id_key] = processed_historical_data[i][civ_data_key][civ_id_key].copy() # Shallow copy of individual civ attributes

    for i, current_turn_data_entry in enumerate(processed_historical_data):
        current_turn_civ_data_map = current_turn_data_entry.get(civ_data_key, {})
        for civ_id_key, civ_attributes in current_turn_civ_data_map.items():
            if civ_attributes.get('status') == 'eliminated':
                civ_attributes['did_initiate_war_in_next_5_turns'] = False
                continue
            
            initiated_war_in_lookahead = False
            # Ensure we use the original historical_data for lookahead, not the progressively modified one
            for j in range(1, N_TURNS_LOOKAHEAD_H1 + 1):
                future_turn_index = i + j
                if future_turn_index < len(historical_data):
                    future_turn_data_entry = historical_data[future_turn_index] # Use original for lookahead
                    civ_future_data = future_turn_data_entry.get(civ_data_key, {}).get(civ_id_key)
                    if civ_future_data and civ_future_data.get('status') != 'eliminated' and civ_future_data.get('war_initiations', 0) > 0:
                        initiated_war_in_lookahead = True
                        break 
                else: # No more future turns to check
                    break
            civ_attributes['did_initiate_war_in_next_5_turns'] = initiated_war_in_lookahead
    print(f"H1 Plots: Pre-processed data to add 'did_initiate_war_in_next_5_turns'.")

    # --- H1.1: Scatter plot --- 
    print("H1.1: Generating scatter plot for Tech vs. Military, colored by war initiation...")
    plot_scatter(
        historical_data=processed_historical_data,
        x_attribute='tech',
        y_attribute='military',
        civ_ids=None, 
        civ_data_key=civ_data_key,
        color_attribute='did_initiate_war_in_next_5_turns',
        title='H1: Tech vs. Military (Colored by War Initiation in Next 5 Turns)',
        xlabel='Technology Level',
        ylabel='Military Strength',
        save_path=f'{save_path_prefix}scatter_tech_military_war_init.png',
        colorbar_label='Initiated War in Next 5 Turns (True/False)'
    )

    # --- H1.2: Correlated line charts for selected civs (e.g., Civ 0 and Civ 1 from mock) --- 
    # These IDs are hardcoded based on the mock data expectation for demonstration.
    # In a real scenario, you might select civs dynamically or pass them as parameters.
    example_civ_ids_for_h1_lines = [0, 1]
    for civ_id_to_plot in example_civ_ids_for_h1_lines:
        print(f"H1.2: Generating correlated line chart for Civ {civ_id_to_plot} (Tech, Military, War Initiations)...")
        plot_line_chart(
            historical_data=processed_historical_data, # Use the processed data
            attributes=['tech', 'military', 'war_initiations'],
            civ_ids=civ_id_to_plot,
            civ_data_key=civ_data_key,
            title=f'H1: Civ {civ_id_to_plot} - Tech, Military & War Initiations Over Time',
            ylabels=['Technology Level', 'Military Strength', 'War Initiations (Count)'],
            use_secondary_yaxis=False, 
            save_path=f'{save_path_prefix}line_civ{civ_id_to_plot}_tech_military_war.png'
        )
    print("H1 Plots: Generation complete.")

def generate_h2_plots(historical_data, civ_data_key='civ_data', save_path_prefix='h2_', turns_before_war=2):
    """
    Generates and saves plots specific to Hypothesis 2:
    H2: Economic desperation increases war probability to acquire resources.

    This involves:
    1. Stacked bar chart: For civs initiating war, show components of their Resource Pressure 
       (food, energy, minerals pressure) leading up to the war.
    2. Event-triggered plots: When a war starts, generate a snapshot bar chart of the attacker's resource deficits.
    """
    if not historical_data:
        print("H2 Plots: Historical data is empty. Cannot generate plots.")
        return

    print(f"\n--- Generating plots for H2 (Economic Desperation) ---")
    processed_civ_war_events = set() # To avoid plotting multiple times if a war spans turns with war_initiations > 0

    for turn_idx, current_turn_data in enumerate(historical_data):
        current_turn_number = current_turn_data['turn']
        civ_data_map = current_turn_data.get(civ_data_key, {})

        for civ_id, civ_attributes in civ_data_map.items():
            if civ_attributes.get('status') == 'eliminated':
                continue

            if civ_attributes.get('war_initiations', 0) > 0:
                war_event_key = (civ_id, current_turn_number) # Uniquely identify this war initiation event instance
                if war_event_key in processed_civ_war_events:
                    continue
                processed_civ_war_events.add(war_event_key)

                print(f"H2: Detected war initiation by Civ {civ_id} at Turn {current_turn_number}.")

                # H2.1: Grouped Bar Chart for pressure components leading up to war
                pressure_components = ['food_pressure', 'energy_pressure', 'minerals_pressure']
                categories_h2_1 = []
                data_h2_1 = [] # List of lists, outer for categories (turns), inner for group_labels (pressures)
                
                for i in range(turns_before_war, -1, -1): # From T-turns_before_war to T_war
                    lookback_turn_idx = turn_idx - i
                    if lookback_turn_idx >= 0:
                        lookback_turn_data = historical_data[lookback_turn_idx]
                        lookback_civ_attrs = lookback_turn_data.get(civ_data_key, {}).get(civ_id)
                        if lookback_civ_attrs and lookback_civ_attrs.get('status') != 'eliminated':
                            turn_label = f"T-{i}" if i > 0 else "War Turn"
                            categories_h2_1.append(f"{lookback_turn_data['turn']} ({turn_label})")
                            current_turn_pressures = [lookback_civ_attrs.get(pc, 0) for pc in pressure_components]
                            data_h2_1.append(current_turn_pressures)
                
                if data_h2_1 and categories_h2_1:
                    plot_bar_chart(
                        data=data_h2_1,
                        categories=categories_h2_1,
                        is_grouped=True,
                        group_labels=[pc.replace('_', ' ').capitalize() for pc in pressure_components],
                        title=f'H2.1: Resource Pressures for Civ {civ_id}\nLeading to War at Turn {current_turn_number}',
                        xlabel='Turn Relative to War Initiation',
                        ylabel='Pressure Level (0-1)',
                        legend_title='Pressure Components',
                        save_path=f'{save_path_prefix}civ{civ_id}_war_turn{current_turn_number}_pressures.png'
                    )
                else:
                    print(f"H2.1: Not enough data to plot pressure components for Civ {civ_id} war at Turn {current_turn_number}.")

                # H2.2: Simple Bar Chart for resource deficits at war initiation
                deficit_attributes = ['food_deficit', 'energy_deficit', 'minerals_deficit']
                deficit_data_h2_2 = {}
                attacker_data_at_war = current_turn_data.get(civ_data_key, {}).get(civ_id)
                if attacker_data_at_war:
                    for da in deficit_attributes:
                        deficit_data_h2_2[da.replace('_',' ').capitalize()] = attacker_data_at_war.get(da, 0)
                
                if deficit_data_h2_2 and any(v > 0 for v in deficit_data_h2_2.values()): # Plot if there are any deficits
                    plot_bar_chart(
                        data=deficit_data_h2_2,
                        title=f'H2.2: Resource Deficits for Civ {civ_id}\at War Initiation (Turn {current_turn_number})',
                        xlabel='Resource Type',
                        ylabel='Deficit Amount',
                        save_path=f'{save_path_prefix}civ{civ_id}_war_turn{current_turn_number}_deficits.png'
                    )
                else:
                    print(f"H2.2: No deficit data or zero deficits for Civ {civ_id} at Turn {current_turn_number} for war initiation.")
    print("H2 Plots: Generation attempt complete.")

def generate_h3_plots(historical_data, civ_data_key='civ_data', save_path_prefix='h3_'):
    """
    Generates and saves plots specific to Hypothesis 3:
    H3: Population pressure acts as a catalyst for conflict when civilizations cannot expand territorially.

    This involves:
    H3.2: Scatter plot: Average Population Pressure (Pp_i) vs. Total Number of Conflicts Initiated.
    """
    if not historical_data:
        print("H3 Plots: Historical data is empty. Cannot generate plots.")
        return

    print(f"\n--- Generating plots for H3 (Population Pressure) ---")

    civ_summary_data = {}
    # {civ_id: {'pop_pressure_sum': 0, 'pop_pressure_count': 0, 'total_wars': 0, 'active_turns':0}}

    for turn_data in historical_data:
        civ_data_map = turn_data.get(civ_data_key, {})
        for civ_id, civ_attributes in civ_data_map.items():
            if civ_attributes.get('status') != 'active': # Only consider active turns for averaging pressure
                # Still count wars even if civ becomes eliminated later, if war_initiations is logged before elimination
                if civ_id not in civ_summary_data:
                     civ_summary_data[civ_id] = {'pop_pressure_sum': 0, 'pop_pressure_count': 0, 'total_wars': 0, 'active_turns': 0, 'id': civ_id}
                civ_summary_data[civ_id]['total_wars'] += civ_attributes.get('war_initiations', 0)
                continue

            if civ_id not in civ_summary_data:
                civ_summary_data[civ_id] = {'pop_pressure_sum': 0, 'pop_pressure_count': 0, 'total_wars': 0, 'active_turns': 0, 'id': civ_id}
            
            civ_summary_data[civ_id]['pop_pressure_sum'] += civ_attributes.get('population_pressure', 0)
            civ_summary_data[civ_id]['pop_pressure_count'] += 1
            civ_summary_data[civ_id]['total_wars'] += civ_attributes.get('war_initiations', 0)
            civ_summary_data[civ_id]['active_turns'] +=1

    avg_pressures = []
    total_wars_list = []
    civ_ids_for_plot = [] # For potential labeling, if plot_scatter supported it directly

    for civ_id, summary in civ_summary_data.items():
        if summary['pop_pressure_count'] > 0:
            avg_p = summary['pop_pressure_sum'] / summary['pop_pressure_count']
        else:
            avg_p = 0 # Avoid division by zero if a civ was never active or had no pressure data
        
        avg_pressures.append(avg_p)
        total_wars_list.append(summary['total_wars'])
        civ_ids_for_plot.append(civ_id)

    if not avg_pressures or not total_wars_list:
        print("H3.2: No data to plot average population pressure vs. total wars initiated.")
        return

    # We need to adapt plot_scatter or prepare data differently if we want to use civ_ids as point labels.
    # For now, plot_scatter doesn't directly use a list of x and y values and separate labels.
    # We'll create a temporary historical_data-like structure for plot_scatter.
    temp_plot_data = [] 
    if avg_pressures and total_wars_list and len(avg_pressures) == len(total_wars_list):
        for i in range(len(avg_pressures)):
            # Creating a simplified structure that plot_scatter can digest for this specific case.
            # Each "civ" is now a single data point with these two attributes.
            # The 'turn' and 'civ_data_key' are somewhat artificial here but needed by plot_scatter structure.
            temp_plot_data.append({
                'turn': 0, # Dummy turn
                civ_data_key: {
                    civ_ids_for_plot[i]: { # Use actual civ_id as key
                         'avg_population_pressure': avg_pressures[i],
                         'total_wars_initiated': total_wars_list[i]
                    }
                }
            })
    
    if temp_plot_data:
        print("H3.2: Generating scatter plot for Average Population Pressure vs. Total Wars Initiated...")
        plot_scatter(
            historical_data=temp_plot_data,
            x_attribute='avg_population_pressure',
            y_attribute='total_wars_initiated',
            civ_ids=None, # Process all effective "civs" in temp_plot_data
            civ_data_key=civ_data_key,
            title='H3.2: Avg. Population Pressure vs. Total Wars Initiated',
            xlabel='Average Population Pressure (Pp_i)',
            ylabel='Total Number of Wars Initiated',
            save_path=f'{save_path_prefix}avg_pop_pressure_vs_total_wars.png'
        )
    else:
        print("H3.2: Failed to prepare data for scatter plot.")
    
    print("H3 Plots: Generation attempt complete.")

def generate_h4_plots(historical_data, civ_data_key='civ_data', relations_data_key='relations_data', save_path_prefix='h4_', snapshot_turn=-1):
    """
    Generates and saves plots specific to Hypothesis 4:
    H4: Cultural similarity promotes diplomacy and trade, reducing conflicts.

    This involves:
    H4.1: Enhanced network graph with edge color/thickness for cultural similarity and interaction type.
    H4.2: Bar chart of average cultural difference by interaction type.
    """
    if not historical_data:
        print("H4 Plots: Historical data is empty. Cannot generate plots.")
        return

    print(f"\n--- Generating plots for H4 (Cultural Similarity & Diplomacy) ---")

    # --- H4.1: Enhanced Network Graph --- 
    # Use data from a specific turn (e.g., last turn, or specified snapshot_turn)
    target_turn_data = historical_data[snapshot_turn] # Default to last turn if snapshot_turn is -1
    
    nodes_h4_1 = []
    if civ_data_key in target_turn_data:
        for civ_id, civ_attrs in target_turn_data[civ_data_key].items():
            if civ_attrs.get('status') == 'active': # Only active civs for the graph
                 nodes_h4_1.append(civ_id)
    
    edges_h4_1 = []
    if relations_data_key in target_turn_data and nodes_h4_1:
        relations = target_turn_data[relations_data_key]
        for pair, attributes in relations.items():
            civ1, civ2 = pair
            if civ1 in nodes_h4_1 and civ2 in nodes_h4_1: # Ensure both civs are active for the edge
                sim = attributes.get('cultural_similarity', 0)
                interaction_type = attributes.get('type', 'neutral').lower()
                edge_attr = {'weight': (sim * 5) + 0.5, 'label': f"{interaction_type[:3]}\nSim:{sim:.2f}"}
                
                if interaction_type == 'trade': edge_attr['color'] = 'green'
                elif interaction_type == 'alliance': edge_attr['color'] = 'blue'
                elif interaction_type == 'war': edge_attr['color'] = 'red'
                else: edge_attr['color'] = 'grey'
                edges_h4_1.append((civ1, civ2, edge_attr))
    
    if nodes_h4_1 and edges_h4_1:
        plot_network_graph(
            nodes_data=nodes_h4_1,
            edges_data=edges_h4_1,
            title=f'H4.1: Civ Network (Turn {target_turn_data["turn"]})\nColor=Type, Thickness~Similarity',
            save_path=f'{save_path_prefix}network_turn{target_turn_data["turn"]}_similarity.png',
            show_edge_labels=True,
            node_size=800
        )
    else:
        print(f"H4.1: Not enough data for network graph at turn {target_turn_data['turn']}.")

    # --- H4.2: Bar Chart of Average Cultural Difference by Interaction Type ---
    cultural_differences_by_type = {'trade': [], 'alliance': [], 'war': [], 'neutral': []}
    
    for turn_data in historical_data:
        if relations_data_key in turn_data:
            relations = turn_data[relations_data_key]
            active_civs_in_turn = {cid for cid, cattrs in turn_data.get(civ_data_key, {}).items() if cattrs.get('status') == 'active'}
            for pair, attributes in relations.items():
                civ1, civ2 = pair
                if not (civ1 in active_civs_in_turn and civ2 in active_civs_in_turn):
                    continue # Only consider interactions between active civs for this analysis

                sim = attributes.get('cultural_similarity', 0)
                cultural_diff = 1 - sim # As per formula, diff = 1 - sim
                interaction_type = attributes.get('type', 'neutral').lower()
                if interaction_type in cultural_differences_by_type:
                    cultural_differences_by_type[interaction_type].append(cultural_diff)
                else: # Should not happen if types are predefined
                    cultural_differences_by_type['neutral'].append(cultural_diff) # Default to neutral if unknown

    avg_cultural_diff_data_h4_2 = {}
    # Combine 'trade' and 'alliance' for the plot
    trade_alliance_diffs = cultural_differences_by_type['trade'] + cultural_differences_by_type['alliance']
    if trade_alliance_diffs:
        avg_cultural_diff_data_h4_2['Trade/Alliance'] = np.mean(trade_alliance_diffs)
    
    if cultural_differences_by_type['war']:
        avg_cultural_diff_data_h4_2['War'] = np.mean(cultural_differences_by_type['war'])

    if avg_cultural_diff_data_h4_2:
        plot_bar_chart(
            data=avg_cultural_diff_data_h4_2,
            title='H4.2: Avg Cultural Difference by Interaction Type (War vs Trade/Alliance)',
            xlabel='Interaction Type',
            ylabel='Average Cultural Difference (1 - Similarity)',
            save_path=f'{save_path_prefix}avg_cultural_diff_by_interaction_trade_war.png'
        )
    else:
        print("H4.2: Not enough data for Trade/Alliance or War categories to plot average cultural difference.")
    
    print("H4 Plots: Generation attempt complete.")

def generate_h5_plots(historical_data, civ_data_key='civ_data', relations_data_key='relations_data', save_path_prefix='h5_'):
    """
    Generates plots for H5: Civilizations with higher initial friendliness and 
    cultural development are more likely to establish enduring trade networks, 
    leading to long-term stability and growth.
    """
    if not historical_data or len(historical_data) == 0:
        print("H5 Plots: Historical data is empty or insufficient.")
        return

    print(f"\n--- Generating plots for H5 (Initial Conditions & Long-Term Outcomes) ---")

    initial_conditions = {} 
    if historical_data[0].get('turn') == 1:
        first_turn_civ_data = historical_data[0].get(civ_data_key, {})
        for civ_id, data in first_turn_civ_data.items():
            if data.get('status', 'eliminated') != 'eliminated':
                initial_conditions[civ_id] = {
                    'friendliness': data.get('friendliness', 0),
                    'culture': data.get('culture', 0)
                }
    
    if not initial_conditions:
        print("H5 Plots: Could not determine initial conditions from turn 1 data.")
        return

    friendliness_threshold_h5 = 0.6
    culture_threshold_h5 = 55.0 
    cohorts = {'high_potential': [], 'other': []}
    for civ_id, conditions in initial_conditions.items():
        if conditions['friendliness'] >= friendliness_threshold_h5 and \
           conditions['culture'] >= culture_threshold_h5:
            cohorts['high_potential'].append(civ_id)
        else:
            cohorts['other'].append(civ_id)

    print(f"H5 Cohorts: High Potential: {cohorts['high_potential']}, Other: {cohorts['other']}")
    if not cohorts['high_potential'] or not cohorts['other']:
        print("H5 Plots: Insufficient civs in one or both cohorts for comparison. Skipping H5 plots.")
        return

    turns_list = [data['turn'] for data in historical_data]
    cohort_metrics_timeseries = {
        cohort_name: {
            'avg_trade_partners': [], 'avg_peacefulness': [],
            'avg_population': [], 'avg_total_resources': []
        } for cohort_name in cohorts
    }

    for turn_data_entry in historical_data:
        current_civ_data_map_h5 = turn_data_entry.get(civ_data_key, {})
        for cohort_name, civ_ids_in_cohort in cohorts.items():
            active_civs_in_cohort_this_turn = [cid for cid in civ_ids_in_cohort if current_civ_data_map_h5.get(cid, {}).get('status') == 'active']
            
            if not active_civs_in_cohort_this_turn:
                for metric_key_h5 in cohort_metrics_timeseries[cohort_name]: 
                    cohort_metrics_timeseries[cohort_name][metric_key_h5].append(np.nan)
                continue

            trade_partners_sum, war_civ_count, pop_sum, resources_sum = 0.0, 0.0, 0.0, 0.0
            for civ_id in active_civs_in_cohort_this_turn:
                civ_attrs = current_civ_data_map_h5.get(civ_id, {})
                trade_partners_sum += civ_attrs.get('num_trade_partners', 0)
                if civ_attrs.get('is_at_war', False): war_civ_count += 1
                pop_sum += civ_attrs.get('population', 0)
                resources_sum += civ_attrs.get('food_stock', 0) + civ_attrs.get('energy_stock', 0) + civ_attrs.get('minerals_stock', 0)
            
            num_active_h5 = float(len(active_civs_in_cohort_this_turn))
            cohort_metrics_timeseries[cohort_name]['avg_trade_partners'].append(trade_partners_sum / num_active_h5 if num_active_h5 > 0 else np.nan)
            cohort_metrics_timeseries[cohort_name]['avg_peacefulness'].append((1.0 - (war_civ_count / num_active_h5)) * 100.0 if num_active_h5 > 0 else np.nan)
            cohort_metrics_timeseries[cohort_name]['avg_population'].append(pop_sum / num_active_h5 if num_active_h5 > 0 else np.nan)
            cohort_metrics_timeseries[cohort_name]['avg_total_resources'].append(resources_sum / num_active_h5 if num_active_h5 > 0 else np.nan)
            
    metrics_to_plot_h5 = [
        ('avg_trade_partners', 'Avg. Number of Trade Partners', 'Number of Partners'),
        ('avg_peacefulness', 'Avg. Peacefulness Index', 'Peacefulness (%)'),
        ('avg_population', 'Avg. Population Growth', 'Population'),
        ('avg_total_resources', 'Avg. Total Resource Stock', 'Total Resources')
    ]

    for metric_key_plot, plot_title_plot, ylabel_plot in metrics_to_plot_h5:
        plt.figure(figsize=(12, 7))
        for cohort_name_plot, data_series_plot in cohort_metrics_timeseries.items():
            # Filter out NaNs for plotting if any cohort was empty for some turns
            valid_turns_plot = [turns_list[i] for i, val in enumerate(data_series_plot[metric_key_plot]) if not np.isnan(val)]
            valid_values_plot = [val for val in data_series_plot[metric_key_plot] if not np.isnan(val)]
            if valid_turns_plot and valid_values_plot:
                 plt.plot(valid_turns_plot, valid_values_plot, marker='.', linestyle='-', label=f'{cohort_name_plot.replace("_", " ").title()} Cohort')
        
        plt.title(f'H5: {plot_title_plot} by Initial Cohort')
        plt.xlabel('Turn'); plt.ylabel(ylabel_plot)
        plt.legend(); plt.grid(True); plt.tight_layout()
        plot_save_path_h5 = f"{save_path_prefix}{metric_key_plot}_by_cohort.png"
        plt.savefig(plot_save_path_h5); print(f"H5 Plot saved to {plot_save_path_h5}"); plt.close()
    print("H5 Plots: Generation attempt complete.")

def generate_h6_plots(historical_data, civ_data_key='civ_data', save_path_prefix='h6_'):
    """
    Generates plots for H6: Repeated victories decrease friendliness and increase aggressiveness, 
    potentially triggering a cycle of escalating conflicts.
    
    Plots line charts for selected civs showing: victories, friendliness, and war_initiations over time.
    """
    if not historical_data:
        print("H6 Plots: Historical data is empty.")
        return

    print(f"\n--- Generating plots for H6 (Victories, Friendliness, Conflict Escalation) ---")

    # Select civs that have interesting war/victory patterns in mock data
    # Civ 0 initiates war at t=16, Civ 1 initiates at t=8
    civ_ids_for_h6_plots = [0, 1] 

    for civ_id_plot in civ_ids_for_h6_plots:
        # Check if the civ exists in the data to avoid errors if mock data changes
        civ_exists = any(civ_id_plot in turn_data.get(civ_data_key, {}) for turn_data in historical_data)
        if not civ_exists:
            print(f"H6 Plots: Civ {civ_id_plot} not found consistently in historical data. Skipping this civ.")
            continue

        print(f"H6 Plots: Generating line chart for Civ {civ_id_plot} (Victories, Friendliness, War Initiations)...")
        plot_line_chart(
            historical_data=historical_data,
            attributes=['victories', 'friendliness', 'war_initiations'],
            civ_ids=civ_id_plot, # Single civ ID for this function call
            civ_data_key=civ_data_key,
            title=f'H6: Civ {civ_id_plot} - Victories, Friendliness & War Initiations',
            ylabels=['Victories (Count)', 'Friendliness (0-1)', 'War Initiations (Count)'],
            use_secondary_yaxis=False, # Plot all on primary for now, or let plot_line_chart decide based on num attributes
            save_path=f'{save_path_prefix}civ{civ_id_plot}_victory_friendliness_war.png'
        )
    
    print("H6 Plots: Generation attempt complete.")

if __name__ == '__main__':
    print("Running plotting.py in test mode with mock data...")
    mock_historical_data = []
    num_mock_turns = 20
    mock_civ_ids_main = [0, 1, 2]
    civ_data_key_for_mock_main = 'civ_data'
    relations_data_key_for_mock_main = 'relations_data'
    initial_stocks = {'food_stock': 1000, 'energy_stock': 500, 'minerals_stock': 300}

    for t in range(1, num_mock_turns + 1):
        turn_entry = {'turn': t, civ_data_key_for_mock_main: {}, relations_data_key_for_mock_main: {}}
        temp_civ_cultures_this_turn = {}

        for civ_id_val_main in mock_civ_ids_main:
            if civ_id_val_main == 2 and t > 12:
                turn_entry[civ_data_key_for_mock_main][civ_id_val_main] = {
                    'status': 'eliminated', 'tech': 0, 'military': 0, 'culture': 0, 'war_initiations':0, 
                    'war_initiated_predictor_flag': False,
                    'food_pressure': 0, 'energy_pressure': 0, 'minerals_pressure': 0,
                    'food_deficit': 0, 'energy_deficit': 0, 'minerals_deficit': 0,
                    'population_pressure': 0,
                    'food_stock': 0, 'energy_stock': 0, 'minerals_stock': 0, 
                    'num_trade_partners': 0, 'is_at_war': False
                }
                temp_civ_cultures_this_turn[civ_id_val_main] = 0
                continue
            
            pop_val = 100 + t * (civ_id_val_main + 1) * 5 - (civ_id_val_main * 20 if civ_id_val_main == 1 and t > 6 else 0)
            tech_val = 10 + t * (civ_id_val_main + 1) * 1.5 + (15 if civ_id_val_main == 0 and t > 5 else 0)
            mil_val = 20 + t * (civ_id_val_main * 2 + 1) + np.random.randint(-5, 5)
            
            # H5 Tweak: Culture adjustment
            cult_val = 50 + t * (civ_id_val_main + 1)*2.5 + np.random.randint(-3,4) - (t*1.5 if civ_id_val_main == 0 else 0)
            cult_val = max(1, cult_val)
            temp_civ_cultures_this_turn[civ_id_val_main] = cult_val

            # H5 Tweak: Friendliness decay adjustment
            friendliness_decay_rate = 0.03
            if civ_id_val_main in [1, 2]: # High potential cohort gets slower decay
                friendliness_decay_rate = 0.015
            friend_val = max(0.1, min(1.0, 0.5 + (civ_id_val_main * 0.15) - t * friendliness_decay_rate + np.random.rand() * 0.05))
            
            food_p = np.clip(0.2 + (t / num_mock_turns)*0.5 + np.random.rand()*0.3 - (civ_id_val_main*0.1), 0, 1)
            energy_p = np.clip(0.3 + (t / num_mock_turns)*0.4 + np.random.rand()*0.4 - (civ_id_val_main*0.05), 0, 1)
            minerals_p = np.clip(0.1 + (t / num_mock_turns)*0.6 + np.random.rand()*0.2 - (civ_id_val_main*0.15), 0, 1)
            if civ_id_val_main == 1 and t > 7 and t < 12: food_p = np.clip(food_p + 0.3, 0,1); minerals_p = np.clip(minerals_p + 0.2,0,1)
            if civ_id_val_main == 0 and t > 13 and t < 18: energy_p = np.clip(energy_p + 0.4, 0,1)
            
            war_init_count = 0
            if civ_id_val_main == 0: war_init_count = 1 if t == 16 else 0
            elif civ_id_val_main == 1: war_init_count = 1 if t == 8 else 0
            
            deficit_threshold = 0.65; deficit_scale = 100
            food_d = max(0, food_p - deficit_threshold) * deficit_scale if war_init_count > 0 else 0
            energy_d = max(0, energy_p - deficit_threshold) * deficit_scale if war_init_count > 0 else 0
            minerals_d = max(0, minerals_p - deficit_threshold) * deficit_scale if war_init_count > 0 else 0
            if civ_id_val_main == 0 and t == 16: food_d, energy_d, minerals_d = np.random.randint(30,70), np.random.randint(40,80), np.random.randint(20,60)
            if civ_id_val_main == 1 and t == 8: food_d, energy_d, minerals_d = np.random.randint(40,80), np.random.randint(30,70), np.random.randint(30,70)
            
            current_status = 'active'
            if civ_id_val_main == 2 and t > 12: current_status = 'eliminated'

            # H5 Tweak: Resource stock adjustments
            deficit_impact_food, deficit_impact_energy, deficit_impact_minerals = 0.5, 0.5, 0.5
            rand_food_low, rand_food_high = -20, 20
            rand_energy_low, rand_energy_high = -15, 15
            rand_minerals_low, rand_minerals_high = -10, 10

            if civ_id_val_main in [1, 2]: # High potential cohort
                deficit_impact_food, deficit_impact_energy, deficit_impact_minerals = 0.3, 0.3, 0.3
                rand_food_low, rand_food_high = -15, 25
                rand_energy_low, rand_energy_high = -10, 20
                rand_minerals_low, rand_minerals_high = -5, 15

            fs = initial_stocks['food_stock'] + t*10 - food_d * deficit_impact_food + (np.random.randint(rand_food_low, rand_food_high) if current_status=='active' else 0)
            es = initial_stocks['energy_stock'] + t*5 - energy_d * deficit_impact_energy + (np.random.randint(rand_energy_low, rand_energy_high) if current_status=='active' else 0)
            ms = initial_stocks['minerals_stock'] + t*2 - minerals_d * deficit_impact_minerals + (np.random.randint(rand_minerals_low, rand_minerals_high) if current_status=='active' else 0)
            
            # H6: Adjusted 'victories' based on mock war events for this turn
            # Initialize victories if not present (for t=1 or if loaded differently)
            if t == 1:
                current_victories = 0
            else:
                # Get victories from previous turn for this civ
                prev_turn_data = next((item for item in mock_historical_data if item["turn"] == t-1), None)
                if prev_turn_data and civ_id_val_main in prev_turn_data.get(civ_data_key_for_mock_main, {}):
                    current_victories = prev_turn_data[civ_data_key_for_mock_main][civ_id_val_main].get('victories', 0)
                else:
                    current_victories = 0 # Should ideally not happen if data is consistent
            
            # Add a victory if this civ initiated a war this turn based on our hardcoded events
            if civ_id_val_main == 1 and war_init_count > 0 and t == 8: # Civ 1 initiated war at t=8
                current_victories += 1
            elif civ_id_val_main == 0 and war_init_count > 0 and t == 16: # Civ 0 initiated war at t=16
                current_victories += 1
            # Note: This doesn't model defender victories or ongoing accumulation from a single war.
            # It's a simplified way to get some victory points correlated with war initiations for H6 plotting.

            turn_entry[civ_data_key_for_mock_main][civ_id_val_main] = {
                'population': pop_val, 'tech': tech_val, 'military': mil_val, 'culture': cult_val,
                'friendliness': friend_val, 
                'victories': current_victories, # H6: Updated victories
                'population_pressure': max(0, (pop_val - 1500*(1+0.2*civ_id_val_main)) / (1500*(1+0.2*civ_id_val_main))),
                'resource_pressure': (food_p + energy_p + minerals_p) / 3,
                'war_initiated_predictor_flag': (civ_id_val_main == 1 and 5 < t < 10) or (civ_id_val_main == 0 and t > 15 and tech_val > 30 and mil_val > 60),
                'war_initiations': war_init_count, # H6: Used for plotting and victory logic
                'status': current_status,
                'food_pressure': food_p, 'energy_pressure': energy_p, 'minerals_pressure': minerals_p,
                'food_deficit': food_d, 'energy_deficit': energy_d, 'minerals_deficit': minerals_d,
                'food_stock': max(0, fs), 'energy_stock': max(0, es), 'minerals_stock': max(0, ms),
                'num_trade_partners': 0, 'is_at_war': False
            }

        # --- Part 2: Determine Inter-Civ Relations (H4 logic) ---
        active_civs_for_relations = [cid for cid, cdata in turn_entry[civ_data_key_for_mock_main].items() if cdata.get('status') == 'active']
        for i in range(len(active_civs_for_relations)):
            for j in range(i + 1, len(active_civs_for_relations)):
                id1, id2 = active_civs_for_relations[i], active_civs_for_relations[j]
                c1_cult = temp_civ_cultures_this_turn.get(id1, 1)
                c2_cult = temp_civ_cultures_this_turn.get(id2, 1)
                cultural_sim = 1 - (abs(c1_cult - c2_cult) / max(c1_cult, c2_cult)) if max(c1_cult, c2_cult) > 0 else 0
                cultural_sim = round(cultural_sim, 2)
                pair_key = tuple(sorted((id1, id2)))
                relation_type = 'neutral'
                is_specific_war_event = False
                if pair_key == (0,1) and t == 8 and turn_entry[civ_data_key_for_mock_main].get(1, {}).get('war_initiations', 0) > 0:
                    is_specific_war_event = True
                elif pair_key == (0,2) and t == 16 and turn_entry[civ_data_key_for_mock_main].get(0, {}).get('war_initiations', 0) > 0:
                    is_specific_war_event = True
                
                if is_specific_war_event: relation_type = 'war'
                else:
                    sim_alliance_thr, sim_trade_thr, sim_war_thr = 0.75, 0.50, 0.25
                    if cultural_sim >= sim_alliance_thr: relation_type = 'alliance'
                    elif cultural_sim >= sim_trade_thr: relation_type = 'trade'
                    elif cultural_sim < sim_war_thr and np.random.rand() < 0.6: relation_type = 'war'
                    if pair_key == (0,1) and t < 8 and relation_type not in ['war', 'alliance']: relation_type = 'trade'
                
                turn_entry[relations_data_key_for_mock_main][pair_key] = {'type': relation_type, 'cultural_similarity': cultural_sim}

        # --- Part 3: Update Civ Data with H5 metrics (num_trade_partners, is_at_war) based on relations ---
        current_relations_for_h5 = turn_entry.get(relations_data_key_for_mock_main, {})
        civ_trade_partners_update_map = {cid: 0 for cid in mock_civ_ids_main}
        civ_at_war_update_map = {cid: False for cid in mock_civ_ids_main}

        for pair, relation_details in current_relations_for_h5.items():
            c1_id_h5, c2_id_h5 = pair
            rel_type_h5 = relation_details.get('type')
            if c1_id_h5 in turn_entry[civ_data_key_for_mock_main] and c2_id_h5 in turn_entry[civ_data_key_for_mock_main] and \
               turn_entry[civ_data_key_for_mock_main][c1_id_h5].get('status') == 'active' and \
               turn_entry[civ_data_key_for_mock_main][c2_id_h5].get('status') == 'active':
                if rel_type_h5 == 'trade' or rel_type_h5 == 'alliance':
                    civ_trade_partners_update_map[c1_id_h5] += 1
                    civ_trade_partners_update_map[c2_id_h5] += 1
                elif rel_type_h5 == 'war':
                    civ_at_war_update_map[c1_id_h5] = True
                    civ_at_war_update_map[c2_id_h5] = True
        
        for civ_id_to_update_h5 in mock_civ_ids_main:
            if civ_id_to_update_h5 in turn_entry[civ_data_key_for_mock_main]:
                turn_entry[civ_data_key_for_mock_main][civ_id_to_update_h5]['num_trade_partners'] = civ_trade_partners_update_map.get(civ_id_to_update_h5, 0)
                turn_entry[civ_data_key_for_mock_main][civ_id_to_update_h5]['is_at_war'] = civ_at_war_update_map.get(civ_id_to_update_h5, False)

        mock_historical_data.append(turn_entry)

    if mock_historical_data:
        print(f"\nGenerated {len(mock_historical_data)} turns of mock historical data for plot testing.")
        
        print("\n--- Generating plots for H1 via dedicated function ---")
        generate_h1_plots(mock_historical_data, civ_data_key_for_mock_main, save_path_prefix='h1_mock_')

        print("\n--- Generating plots for H2 via dedicated function ---")
        generate_h2_plots(mock_historical_data, civ_data_key_for_mock_main, save_path_prefix='h2_mock_')

        print("\n--- Generating plots for H3 via dedicated function ---")
        generate_h3_plots(mock_historical_data, civ_data_key_for_mock_main, save_path_prefix='h3_mock_')

        print("\n--- Generating plots for H4 via dedicated function ---")
        generate_h4_plots(mock_historical_data, civ_data_key_for_mock_main, relations_data_key_for_mock_main, save_path_prefix='h4_mock_')
        
        print("\n--- Generating plots for H5 via dedicated function ---")
        generate_h5_plots(mock_historical_data, civ_data_key_for_mock_main, relations_data_key_for_mock_main, save_path_prefix='h5_mock_')
        
        print("\n--- Generating plots for H6 via dedicated function ---")
        generate_h6_plots(mock_historical_data, civ_data_key_for_mock_main, save_path_prefix='h6_mock_')
        
        print("\nMock H1, H2, H3, H4, H5 & H6 plots generation attempted. Check for .png files in the directory.")
