##### DEPENDENCIES #####
from model import Model, log_to_plots
from visualize import visualize_simulation
from civ import Civ
from planet import Planet
from matplotlib.pyplot import bar, show
from time import time

import os
import shutil
import seaborn as sns
import matplotlib.pyplot as plt
import json
import pandas as pd
import ast
import numpy as np

logs_folder = "output/logs"
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

records = []
relation_records = []  # for H4

def clear_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
    else:
        os.makedirs(folder_path)

def run_single_simulation():
    clear_folder("output/logs")
    clear_folder("output/plots")
    simulation_model = Model(num_planets=15, grid_height=30, grid_width=30, scenario="Thunderdome", generate_plots_controller=True)
    visualize_simulation(simulation_model)
    simulation_model.generate_sim_log()

def run_multiple_simulations(num_runs):
    clear_folder("output/logs")
    clear_folder("output/plots")
    parameters = (15, 30, 30, "")
    sim_list = [Model(*parameters, generate_plots_controller=False) for _ in range(num_runs)]
    start = time()

    for i in range(num_runs):
        Civ.id_iter = 0
        Planet.id_iter = 0
        for _ in sim_list[i].run_simulation():
            pass
        clear_folder("output/plots")
        sim_list[i].generate_sim_log()

    ends = [sim.end_type for sim in sim_list]
    counts = [ends.count("Culture"), ends.count("Military"), ends.count("Stalemate")]
    end = time()
    print(f"{num_runs} trials ran in {end - start :.4f} seconds.")
    bar(["Culture", "Military", "Stalemate"], counts)
    show()

    analyze_logs()

def analyze_logs():
    for filename in os.listdir(logs_folder):
        if filename.endswith((".json", ".txt")):
            with open(os.path.join(logs_folder, filename)) as f:
                try:
                    log = ast.literal_eval(f.read())
                    for entry in log:
                        turn = entry.get("turn", -1)
                        civ_data = entry.get("civ_data", {})
                        for civ_id, civ in civ_data.items():
                            if civ.get("status", "").lower() == "active":
                                records.append({
                                    "turn": turn,
                                    "civ_id": int(civ_id),
                                    "tech": civ.get("tech", 0),
                                    "military": civ.get("military", 0),
                                    "war_initiations": civ.get("war_initiations", 0),
                                    "desperation_value": civ.get("desperation_value", 0),
                                    "population_pressure": civ.get("population_pressure", 0),
                                    "culture": civ.get("culture", 0),
                                    "friendliness": civ.get("friendliness", 0),
                                    "victories": civ.get("victories", 0),
                                    "is_at_war": int(bool(civ.get("is_at_war", False)))
                                })

                        relations = entry.get("relations_data", {})
                        for (civ_a, civ_b), rel in relations.items():
                            rel_type = rel.get("type")
                            similarity = rel.get("cultural_similarity")
                            if rel_type and similarity is not None:
                                relation_records.append({
                                    "turn": turn,
                                    "civ_a": civ_a,
                                    "civ_b": civ_b,
                                    "relation_type": rel_type,
                                    "cultural_similarity": similarity
                                })
                except Exception as e:
                    print(f"Skipping file {filename} due to error: {e}")

    df = pd.DataFrame(records)
    rel_df = pd.DataFrame(relation_records)
    filtered_rel_df = rel_df[rel_df["relation_type"].isin(["war", "trade"])]

    # Visualization helper
    def bin_and_plot(df, feature, target, bins=10, title="", ylabel=""):
        df = df.copy()
        df["bin"] = pd.cut(df[feature], bins=bins)
        grouped = df.groupby("bin", observed=True)[target].mean().reset_index()
        grouped["bin_mid"] = grouped["bin"].apply(lambda x: x.mid)

        plt.figure()
        sns.lineplot(data=grouped, x="bin_mid", y=target, marker="o")
        plt.title(title)
        plt.xlabel(feature)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

    if not df.empty:
        fig, axs = plt.subplots(1, 2)
        sns.scatterplot(data=df, x="tech", y="military", ax=axs[0]).set(title="H1: Tech vs Military Power")
        bin_and_plot(df, "tech", "war_initiations", 10, "H1: Tech vs War Initiations", "Avg War Initiations")
        plt.tight_layout()
        plt.show()

        bin_and_plot(df, "desperation_value", "is_at_war", 10, "H2: Desperation vs War Likelihood", "Probability of Being at War")
        bin_and_plot(df, "population_pressure", "war_initiations", 10, "H3: Population Pressure vs War Initiations", "Avg War Initiations")

        plt.figure(figsize=(10, 5))
        sns.boxplot(data=filtered_rel_df, x="relation_type", y="cultural_similarity")
        plt.title("H4: Cultural Similarity for War vs Trade")
        plt.xlabel("Relationship Type")
        plt.ylabel("Cultural Similarity")
        plt.grid(True)
        plt.show()

        trade_counts = {}
        for rel in relation_records:
            if rel["relation_type"] == "trade":
                for civ in [rel["civ_a"], rel["civ_b"]]:
                    trade_counts[civ] = trade_counts.get(civ, 0) + 1

        civ_initial = (
            df.sort_values("turn")
            .groupby("civ_id")
            .first()
            .reset_index()
        )
        civ_initial["num_trade_partners"] = civ_initial["civ_id"].map(trade_counts).fillna(0)

        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=civ_initial,
            x="culture",
            y="num_trade_partners",
            hue="friendliness",
            palette="viridis",
            s=100
        )
        plt.title("H5: Culture vs Trade Partners (Color: Friendliness)")
        plt.xlabel("Initial Culture")
        plt.ylabel("Number of Trade Partners")
        plt.grid(True)
        plt.legend(title="Friendliness")
        plt.show()

        bin_and_plot(df, "victories", "war_initiations", bins=np.arange(0, df["victories"].max() + 1.1, 1), 
                     title="H6: Victories vs War Initiations", ylabel="Avg War Initiations")

if __name__ == "__main__":
    print("Welcome to Civilization Diplomacy!")
    print("1. Run a single simulation (with visualization)")
    print("2. Run multiple simulations (with hypothesis analysis)")
    print("3. Analyze Existing Logs Only")
    choice = input("Choose an option (1 or 2): ").strip()

    if choice == "1":
        run_single_simulation()
    elif choice == "2":
        try:
            num_runs = int(input("How many simulations do you want to run? "))
            run_multiple_simulations(num_runs)
        except ValueError:
            print("Invalid input. Please enter an integer.")
    elif choice == "3":
        analyze_logs()
    else:
        print("Invalid choice. Please enter 1 or 2.")
