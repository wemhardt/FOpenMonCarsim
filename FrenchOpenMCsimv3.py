# =========================================================
# FRENCH OPEN 2026 MONTE CARLO SIMULATION
# VERSION 4
# =========================================================
#
# VERSION 4 UPGRADES:
# - Realistic Grand Slam seeding
# - Clay + overall blended strength
# - Opponent + recency weighted metrics
# - Clay-specific matchup interactions
# - BO5 variance adjustment
#
# =========================================================
# REQUIRED CSV STRUCTURE
# =========================================================
#
# Player_ID
# Version4Strength
# Seed
# Clay_RPW
# Clay_SecondServeWon
#
# Example:
#
# Player_ID,Version4Strength,Seed,Clay_RPW,Clay_SecondServeWon
# JannikSinner,2.81,1,0.46,0.57
# CarlosAlcaraz,2.73,2,0.45,0.56
#
# =========================================================

import pandas as pd
import numpy as np
import random

# =========================================================
# 1. LOAD DATA
# =========================================================

players_df = pd.read_csv("/Users/willemhardt/Downloads/FrenchOpenuptoMadridMCSimulation - Version 3.csv")

players_df = players_df.dropna(
    subset=[
        "Player_ID",
        "RecencyAdjStrength",
        "Seed",
        "Clay_RPW",
        "Clay_2ndservewin"
    ]
)

# =========================================================
# 2. ENSURE NUMERIC TYPES
# =========================================================

numeric_cols = [
    "RecencyAdjStrength",
    "Seed",
    "Clay_RPW",
    "Clay_2ndservewin"
]

for col in numeric_cols:

    players_df[col] = pd.to_numeric(
        players_df[col],
        errors="coerce"
    )

# =========================================================
# 3. PLAYER DICTIONARIES
# =========================================================

strength_dict = dict(
    zip(
        players_df["Player_ID"],
        players_df["RecencyAdjStrength"]
    )
)

seed_dict = dict(
    zip(
        players_df["Player_ID"],
        players_df["Seed"]
    )
)

player_metrics = {}

for _, row in players_df.iterrows():

    player_metrics[row["Player_ID"]] = {

        "Clay_RPW":
            row["Clay_RPW"],

        "Clay_2ndservewin":
            row["Clay_2ndservewin"]
    }

# =========================================================
# 4. SORT PLAYERS BY SEED
# =========================================================

players_df = players_df.sort_values("Seed")

# =========================================================
# 5. MODEL PARAMETERS
# =========================================================

# Best-of-5 adjustment
K_FACTOR = 1.45

# Matchup interaction coefficients
RETURN_PRESSURE_COEF = 0.25
SECOND_SERVE_COEF = 0.10

# =========================================================
# 6. WIN PROBABILITY FUNCTION
# =========================================================
#
# INTERACTION 1:
# Return Pressure Edge
#
# PlayerA Clay RPW
# minus
# PlayerB Clay 2nd Serve Won %
#
# Measures:
# how effectively Player A attacks
# Player B's vulnerable serve points
#
# ---------------------------------------------------------
#
# INTERACTION 2:
# Second Serve Stability Edge
#
# PlayerA Clay 2nd Serve Won %
# minus
# PlayerB Clay 2nd Serve Won %
#
# Measures:
# relative serve stability on clay
#
# =========================================================

def win_probability(playerA, playerB):

    # -----------------------------------------------------
    # BASE STRENGTHS
    # -----------------------------------------------------

    strengthA = strength_dict[playerA]
    strengthB = strength_dict[playerB]

    # -----------------------------------------------------
    # MATCHUP INTERACTION 1
    # RETURN PRESSURE EDGE
    # -----------------------------------------------------

    return_pressure_edge = (

        player_metrics[playerA]["Clay_RPW"]

        -

        player_metrics[playerB]["Clay_2ndservewin"]
    )

    # -----------------------------------------------------
    # MATCHUP INTERACTION 2
    # SECOND SERVE EDGE
    # -----------------------------------------------------

    second_serve_edge = (

        player_metrics[playerA]["Clay_2ndservewin"]

        -

        player_metrics[playerB]["Clay_2ndservewin"]
    )

    # -----------------------------------------------------
    # APPLY INTERACTIONS
    # -----------------------------------------------------

    adjusted_strengthA = (

        strengthA

        +

        RETURN_PRESSURE_COEF
        * return_pressure_edge

        +

        SECOND_SERVE_COEF
        * second_serve_edge
    )

    # Player B remains baseline
    adjusted_strengthB = strengthB

    # -----------------------------------------------------
    # LOGISTIC WIN PROBABILITY
    # -----------------------------------------------------

    probabilityA = 1 / (

        1 + np.exp(

            -K_FACTOR
            * (
                adjusted_strengthA
                -
                adjusted_strengthB
            )
        )
    )

    return probabilityA

# =========================================================
# 7. SIMULATE MATCH
# =========================================================

def simulate_match(playerA, playerB):

    probabilityA = win_probability(playerA, playerB)

    rand = random.random()

    if rand < probabilityA:
        return playerA
    else:
        return playerB

# =========================================================
# 8. GENERATE SEEDED GRAND SLAM DRAW
# =========================================================

def generate_seeded_bracket(players_df):

    bracket = [None] * 128

    # -----------------------------------------------------
    # GET SEEDED PLAYERS
    # -----------------------------------------------------

    seeds = (
        players_df[players_df["Seed"] <= 32]
        .sort_values("Seed")
    )

    seed_players = seeds["Player_ID"].tolist()

    # -----------------------------------------------------
    # SEED 1 + 2
    # -----------------------------------------------------

    bracket[0] = seed_players[0]
    bracket[127] = seed_players[1]

    # -----------------------------------------------------
    # SEEDS 3-4
    # -----------------------------------------------------

    positions_3_4 = [32, 95]

    random.shuffle(positions_3_4)

    bracket[positions_3_4[0]] = seed_players[2]
    bracket[positions_3_4[1]] = seed_players[3]

    # -----------------------------------------------------
    # SEEDS 5-8
    # -----------------------------------------------------

    positions_5_8 = [16, 48, 79, 111]

    random.shuffle(positions_5_8)

    for i in range(4):

        bracket[positions_5_8[i]] = seed_players[i + 4]

    # -----------------------------------------------------
    # SEEDS 9-16
    # -----------------------------------------------------

    positions_9_16 = [
        8,24,40,56,
        71,87,103,119
    ]

    random.shuffle(positions_9_16)

    for i in range(8):

        bracket[positions_9_16[i]] = seed_players[i + 8]

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
# 9. PLAY ROUND
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
# 10. SIMULATE TOURNAMENT
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
# 11. INITIALIZE RESULTS
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
# 12. RUN MONTE CARLO
# =========================================================

print("===================================")
print("RUNNING VERSION 4 MONTE CARLO")
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
# 13. CREATE OUTPUT
# =========================================================

output = []

for player in players_df["Player_ID"]:

    output.append({

        "Player": player,

        "Strength":
            strength_dict[player],

        "Seed":
            seed_dict[player],

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
# 14. SORT RESULTS
# =========================================================

results_df = results_df.sort_values(
    by="TitlePct",
    ascending=False
)

# =========================================================
# 15. SAVE RESULTS
# =========================================================

results_df.to_csv(
    "french_open_2026_monte_carlo_resultsv3.csv",
    index=False
)

# =========================================================
# 16. DISPLAY RESULTS
# =========================================================

print()
print("===================================")
print("VERSION 4 COMPLETE")
print("===================================")
print()

print(results_df.head(30))

print()
print("Saved Results:")
print("french_open_2026_monte_carlo_resultsv3.csv")