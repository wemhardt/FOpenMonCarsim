# =========================================================
# FRENCH OPEN 2026 MONTE CARLO SIMULATION
# VERSION 2
# =========================================================
#
# VERSION 2 IMPROVEMENTS:
# - Realistic Grand Slam seeding
# - Top 32 seeds protected
# - Blended FinalStrength model
# - Best-of-5 variance adjustment
# - Randomized seeded draw structure
#
# REQUIRED CSV STRUCTURE:
#
# Player_ID,Rank,FinalStrength
#
# Example:
#
# JannikSinner,1,2.84
# CarlosAlcaraz,2,2.71
# NovakDjokovic,5,1.93
#
# =========================================================

import pandas as pd
import numpy as np
import random

# =========================================================
# 1. LOAD DATA
# =========================================================

players_df = pd.read_csv("/Users/willemhardt/Downloads/FrenchOpenuptoMadridMCSimulation - Version 2.csv")

players_df = players_df.dropna(
    subset=["Player_ID", "Seed", "BlendedStrength"]
)

# Ensure numeric
players_df["Seed"] = pd.to_numeric(players_df["Seed"])
players_df["BlendedStrength"] = pd.to_numeric(
    players_df["BlendedStrength"]
)

# =========================================================
# 2. CREATE STRENGTH DICTIONARY
# =========================================================

strength_dict = dict(
    zip(
        players_df["Player_ID"],
        players_df["BlendedStrength"]
    )
)

# =========================================================
# 3. SORT PLAYERS BY RANK
# =========================================================

players_df = players_df.sort_values("Seed")

# =========================================================
# 4. CREATE SEED GROUPS
# =========================================================

seeded_players = (
    players_df[players_df["Seed"] <= 32]
    ["Player_ID"]
    .tolist()
)

unseeded_players = (
    players_df[players_df["Seed"] > 32]
    ["Player_ID"]
    .tolist()
)

# =========================================================
# 5. WIN PROBABILITY FUNCTION
# =========================================================
#
# VERSION 2:
# Increased K_FACTOR for BO5 realism
#
# Higher K:
# - fewer upsets
# - stronger favorites
# - more realistic Slam dynamics
#
# =========================================================

K_FACTOR = 1.45

def win_probability(playerA, playerB):

    strengthA = strength_dict[playerA]
    strengthB = strength_dict[playerB]

    probabilityA = 1 / (
        1 + np.exp(
            -K_FACTOR * (strengthA - strengthB)
        )
    )

    return probabilityA

# =========================================================
# 6. SIMULATE MATCH
# =========================================================

def simulate_match(playerA, playerB):

    probabilityA = win_probability(playerA, playerB)

    rand = random.random()

    if rand < probabilityA:
        return playerA
    else:
        return playerB

# =========================================================
# 7. CREATE SEEDED GRAND SLAM DRAW
# =========================================================

def generate_seeded_bracket(players_df):

    bracket = [None] * 128

    # -----------------------------------------------------
    # GET SEEDS
    # -----------------------------------------------------

    seeds = (
        players_df[players_df["Seed"] <= 32]
        .sort_values("Seed")
    )

    seed_players = seeds["Player_ID"].tolist()

    # -----------------------------------------------------
    # SEED 1 + SEED 2
    # -----------------------------------------------------

    bracket[0] = seed_players[0]
    bracket[127] = seed_players[1]

    # -----------------------------------------------------
    # SEEDS 3-4
    # -----------------------------------------------------

    seed_3_4_positions = [32, 95]

    random.shuffle(seed_3_4_positions)

    bracket[seed_3_4_positions[0]] = seed_players[2]
    bracket[seed_3_4_positions[1]] = seed_players[3]

    # -----------------------------------------------------
    # SEEDS 5-8
    # -----------------------------------------------------

    seed_5_8_positions = [16, 48, 79, 111]

    random.shuffle(seed_5_8_positions)

    for i in range(4):

        bracket[seed_5_8_positions[i]] = seed_players[i + 4]

    # -----------------------------------------------------
    # SEEDS 9-16
    # -----------------------------------------------------

    seed_9_16_positions = [
        8,24,40,56,
        71,87,103,119
    ]

    random.shuffle(seed_9_16_positions)

    for i in range(8):

        bracket[seed_9_16_positions[i]] = seed_players[i + 8]

    # -----------------------------------------------------
    # SEEDS 17-32
    # -----------------------------------------------------

    remaining_positions = [
        i for i in range(128)
        if bracket[i] is None
    ]

    random.shuffle(remaining_positions)

    for i in range(16):

        bracket[remaining_positions[i]] = seed_players[i + 16]

    # -----------------------------------------------------
    # ADD UNSEEDED PLAYERS
    # -----------------------------------------------------

    unseeded = (
        players_df[players_df["Seed"] > 32]
        ["Player_ID"]
        .tolist()
    )

    random.shuffle(unseeded)

    remaining_positions = [
        i for i in range(128)
        if bracket[i] is None
    ]

    for i in range(len(unseeded)):

        bracket[remaining_positions[i]] = unseeded[i]

    return bracket

# =========================================================
# 8. PLAY ROUND
# =========================================================

def play_round(player_list):

    winners = []

    for i in range(0, len(player_list), 2):

        playerA = player_list[i]
        playerB = player_list[i + 1]

        winner = simulate_match(playerA, playerB)

        winners.append(winner)

    return winners

# =========================================================
# 9. SIMULATE TOURNAMENT
# =========================================================

def simulate_tournament(players_df):

    bracket = generate_seeded_bracket(players_df)

    # ROUND OF 128
    round64 = play_round(bracket)

    # ROUND OF 64
    round32 = play_round(round64)

    # ROUND OF 32
    round16 = play_round(round32)

    # ROUND OF 16
    quarterfinals = play_round(round16)

    # QUARTERFINALS
    semifinals = play_round(quarterfinals)

    # SEMIFINALS
    finals = play_round(semifinals)

    # FINAL
    champion = play_round(finals)[0]

    return {

        "Champion": champion,

        "Finalists": finals,

        "Semifinalists": semifinals,

        "Quarterfinalists": quarterfinals,

        "Round16": round16,

        "Round32": round32,

        "Round64": round64
    }

# =========================================================
# 10. INITIALIZE RESULTS
# =========================================================

NUM_SIMS = 10000

results = {

    player: {

        "Titles": 0,
        "Finals": 0,
        "Semis": 0,
        "Quarters": 0,
        "Round16": 0,
        "Round32": 0,
        "Round64": 0

    }

    for player in players_df["Player_ID"]
}

# =========================================================
# 11. RUN MONTE CARLO
# =========================================================

print("===================================")
print("RUNNING VERSION 2 MONTE CARLO")
print("===================================")
print()

for sim in range(NUM_SIMS):

    outcome = simulate_tournament(players_df)

    champion = outcome["Champion"]

    results[champion]["Titles"] += 1

    for player in outcome["Finalists"]:
        results[player]["Finals"] += 1

    for player in outcome["Semifinalists"]:
        results[player]["Semis"] += 1

    for player in outcome["Quarterfinalists"]:
        results[player]["Quarters"] += 1

    for player in outcome["Round16"]:
        results[player]["Round16"] += 1

    for player in outcome["Round32"]:
        results[player]["Round32"] += 1

    for player in outcome["Round64"]:
        results[player]["Round64"] += 1

    if (sim + 1) % 1000 == 0:

        print(f"Completed {sim + 1} simulations")

# =========================================================
# 12. CREATE RESULTS DATAFRAME
# =========================================================

output = []

for player in players_df["Player_ID"]:

    output.append({

        "Player": player,

        "Strength":
            strength_dict[player],

        "TitlePct":
            results[player]["Titles"] / NUM_SIMS,

        "FinalPct":
            results[player]["Finals"] / NUM_SIMS,

        "SemiPct":
            results[player]["Semis"] / NUM_SIMS,

        "QuarterPct":
            results[player]["Quarters"] / NUM_SIMS,

        "Round16Pct":
            results[player]["Round16"] / NUM_SIMS,

        "Round32Pct":
            results[player]["Round32"] / NUM_SIMS,

        "Round64Pct":
            results[player]["Round64"] / NUM_SIMS
    })

results_df = pd.DataFrame(output)

# =========================================================
# 13. SORT RESULTS
# =========================================================

results_df = results_df.sort_values(
    by="TitlePct",
    ascending=False
)

# =========================================================
# 14. SAVE RESULTS
# =========================================================

results_df.to_csv(
    "french_open_2026_monte_carlo_resultsv2.csv",
    index=False
)

# =========================================================
# 15. DISPLAY RESULTS
# =========================================================

print()
print("===================================")
print("VERSION 2 COMPLETE")
print("===================================")
print()

print(results_df.head(25))

print()
print("Saved Results:")
print("french_open_2026_monte_carlo_resultsv2.csv")