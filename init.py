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
import re


logs_folder = "output/logs"
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)

records = []
relation_records = []  # for H4

def safe_parse_log_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

        # Fix single quotes to double quotes for JSON
        content = re.sub(r"'", '"', content)

        # Fix tuple keys in relations_data to string keys
        content = re.sub(r'\(\s*(\d+)\s*,\s*(\d+)\s*\)', r'"\1-\2"', content)

        # Truncate at the last ] to avoid trailing garbage
        last_bracket = content.rfind("]")
        if last_bracket != -1:
            content = content[:last_bracket + 1]

        try:
            log = json.loads(content)
            return log
        except Exception as e:
            print(f"Failed to parse {path}: {e}")
            return None

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
    print("Choose scenario mode: friendzone, thunderdome, juggernaut, wolf, or press enter for random")
    scenario = input("Scenario: ").strip().lower()
    clear_folder("output/logs")
    clear_folder("output/plots")
    simulation_model = Model(num_planets=15, grid_height=30, grid_width=30, scenario=scenario, generate_plots_controller=True)
    visualize_simulation(simulation_model)
    simulation_model.generate_sim_log()


def run_multiple_simulations(num_runs):
    print("Choose scenario mode for all simulations: friendzone, thunderdome, juggernaut, wolf, or press enter for random")
    scenario = input("Scenario: ").strip().lower()
    clear_folder("output/logs")
    clear_folder("output/plots")
    parameters = (15, 30, 30, scenario)
    sim_list = [Model(*parameters, generate_plots_controller=False) for _ in range(num_runs)]
    start = time()
    special_wins = 0

    for i in range(num_runs):
        Civ.id_iter = 0
        Planet.id_iter = 0
        for _ in sim_list[i].run_simulation():
            pass
        clear_folder("output/plots")
        sim_list[i].generate_sim_log()

        if scenario in ["juggernaut", "wolf"] and sim_list[i].winner_id == 0:
            special_wins += 1


    if scenario in ["juggernaut", "wolf"]:
        print(f"Civilization 0 won {special_wins} out of {num_runs} simulations.")
        ends = [sim.end_type for sim in sim_list]
        counts = [ends.count("Culture"), ends.count("Military"), ends.count("Stalemate")]
        end = time()
        print(f"{num_runs} trials ran in {end - start :.4f} seconds.")
        bar(["Culture", "Military", "Stalemate"], counts)
        show()
    else:
        ends = [sim.end_type for sim in sim_list]
        counts = [ends.count("Culture"), ends.count("Military"), ends.count("Stalemate")]
        bar(["Culture", "Military", "Stalemate"], counts)
        show()
        analyze_logs()

def analyze_logs():
    for filename in os.listdir(logs_folder):
        if filename.endswith((".json", ".txt")):
            path = os.path.join(logs_folder, filename)
            log = safe_parse_log_file(path)
            if not log:
                continue
            for entry in log:
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

                    # Defensive: Only process if relations_data is present
                    relations = entry.get("relations_data", {})
                    if isinstance(relations, dict):
                        for key, rel in relations.items():
                            # Handle stringified keys like "1,2"
                            if isinstance(key, str) and "," in key:
                                try:
                                    civ_a, civ_b = map(int, key.split(","))
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
                                    print(f"Failed to parse key '{key}': {e}")



    df = pd.DataFrame(records)
    rel_df = pd.DataFrame(relation_records)
    filtered_rel_df = rel_df[rel_df["relation_type"].isin(["war", "trade"])]

    def bin_and_plot(df, feature, target, bins=10, title="", ylabel=""):
        df = df.copy()
        df_grouped = df.groupby("civ_id").mean(numeric_only=True).reset_index()
        df_grouped["bin"] = pd.cut(df_grouped[feature], bins=bins)
        grouped = df_grouped.groupby("bin", observed=True)[target].mean().reset_index()
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
                    trade_counts[civ] = trade_counts.get(civ, set())
                    trade_counts[civ].add(rel["turn"])

        civ_initial = (
            df[df["turn"] == df["turn"].min()]
            .groupby("civ_id")
            .first()
            .reset_index()
        )
        civ_initial["num_trade_partners"] = civ_initial["civ_id"].map(lambda x: len(trade_counts.get(x, set())))

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
        plt.ylabel("Number of Trade Turns")
        plt.grid(True)
        plt.legend(title="Friendliness")
        plt.show()

        df_agg = df.groupby("civ_id").agg({"victories": "max", "war_initiations": "mean", "friendliness": "mean"}).reset_index()

        fig, axs = plt.subplots(1, 2, figsize=(12, 6))
        sns.barplot(data=df_agg, x="victories", y="war_initiations", ax=axs[0])
        axs[0].set_title("H6: Victories vs Avg War Initiations")
        axs[0].set_xlabel("Victories")
        axs[0].set_ylabel("Avg War Initiations")

        sns.barplot(data=df_agg, x="victories", y="friendliness", ax=axs[1])
        axs[1].set_title("H6: Victories vs Avg Friendliness")
        axs[1].set_xlabel("Victories")
        axs[1].set_ylabel("Avg Friendliness")

        plt.tight_layout()
        plt.show()



if __name__ == "__main__":
    print("Welcome to Civilization Diplomacy!")
    print("1. Run a single simulation (with visualization)")
    print("2. Run multiple simulations (with hypothesis analysis)")
    print("3. Analyze Existing Logs Only")
    choice = input("Choose an option (1, 2 or 3): ").strip()

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
