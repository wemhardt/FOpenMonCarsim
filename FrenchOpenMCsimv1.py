# =========================================================
# FRENCH OPEN 2026 MONTE CARLO SIMULATION
# VERSION 1
# =========================================================

import pandas as pd
import numpy as np
import random

# =========================================================
# 1. LOAD PLAYER STRENGTH TABLE
# =========================================================
# CSV should contain at minimum:
#
# Player_ID,Strength
# JannikSinner,2.18
# CarlosAlcaraz,2.04
# NovakDjokovic,1.41
#

players_df = pd.read_csv("/Users/willemhardt/Downloads/FrenchOpenuptoMadridMCSimulation - Version1.csv")

# Remove missing values just in case
players_df = players_df.dropna(subset=["Player_ID", "Strength"])

# =========================================================
# 2. CREATE PLAYER LIST + STRENGTH DICTIONARY
# =========================================================

players = players_df["Player_ID"].tolist()

strength_dict = dict(
    zip(
        players_df["Player_ID"],
        players_df["Strength"]
    )
)

print("===================================")
print("PLAYERS LOADED")
print("===================================")
print(f"Total Players: {len(players)}")
print()

# =========================================================
# 3. WIN PROBABILITY FUNCTION
# =========================================================
# Logistic model:
#
# P(A) = 1 / (1 + e^(-k*(A-B)))
#
# k controls upset frequency
#
# Higher k:
# favorites dominate more
#
# Lower k:
# more randomness
#
# Recommended starting range:
# 1.0 - 1.5
#

K_FACTOR = 1.2

def win_probability(playerA, playerB):

    strengthA = strength_dict[playerA]
    strengthB = strength_dict[playerB]

    probA = 1 / (
        1 + np.exp(
            -K_FACTOR * (strengthA - strengthB)
        )
    )

    return probA

# =========================================================
# 4. SIMULATE INDIVIDUAL MATCH
# =========================================================

def simulate_match(playerA, playerB):

    probA = win_probability(playerA, playerB)

    rand = random.random()

    if rand < probA:
        return playerA
    else:
        return playerB

# =========================================================
# 5. GENERATE RANDOM TOURNAMENT DRAW
# =========================================================
# VERSION 1:
# fully randomized bracket
#
# Future versions can include:
# - Grand Slam seeding
# - protected seeds
# - draw constraints
#

def generate_bracket(players):

    bracket = players.copy()

    random.shuffle(bracket)

    return bracket

# =========================================================
# 6. PLAY ONE ROUND
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
# 7. SIMULATE ENTIRE TOURNAMENT
# =========================================================

def simulate_tournament(players):

    bracket = generate_bracket(players)

    # -----------------------------
    # ROUND OF 128
    # -----------------------------
    round64 = play_round(bracket)

    # -----------------------------
    # ROUND OF 64
    # -----------------------------
    round32 = play_round(round64)

    # -----------------------------
    # ROUND OF 32
    # -----------------------------
    round16 = play_round(round32)

    # -----------------------------
    # ROUND OF 16
    # -----------------------------
    quarterfinals = play_round(round16)

    # -----------------------------
    # QUARTERFINALS
    # -----------------------------
    semifinals = play_round(quarterfinals)

    # -----------------------------
    # SEMIFINALS
    # -----------------------------
    finals = play_round(semifinals)

    # -----------------------------
    # FINAL
    # -----------------------------
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
# 8. INITIALIZE RESULT TRACKING
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
    for player in players
}

# =========================================================
# 9. RUN MONTE CARLO SIMULATION
# =========================================================

print("===================================")
print("RUNNING MONTE CARLO")
print("===================================")
print(f"Simulations: {NUM_SIMS}")
print()

for sim in range(NUM_SIMS):

    outcome = simulate_tournament(players)

    # -----------------------------
    # TITLE
    # -----------------------------
    champion = outcome["Champion"]

    results[champion]["Titles"] += 1

    # -----------------------------
    # FINALS
    # -----------------------------
    for player in outcome["Finalists"]:
        results[player]["Finals"] += 1

    # -----------------------------
    # SEMIS
    # -----------------------------
    for player in outcome["Semifinalists"]:
        results[player]["Semis"] += 1

    # -----------------------------
    # QUARTERS
    # -----------------------------
    for player in outcome["Quarterfinalists"]:
        results[player]["Quarters"] += 1

    # -----------------------------
    # ROUND OF 16
    # -----------------------------
    for player in outcome["Round16"]:
        results[player]["Round16"] += 1

    # -----------------------------
    # ROUND OF 32
    # -----------------------------
    for player in outcome["Round32"]:
        results[player]["Round32"] += 1

    # -----------------------------
    # ROUND OF 64
    # -----------------------------
    for player in outcome["Round64"]:
        results[player]["Round64"] += 1

    # Optional progress updates
    if (sim + 1) % 1000 == 0:
        print(f"Completed {sim + 1} simulations")

# =========================================================
# 10. CREATE OUTPUT DATAFRAME
# =========================================================

output = []

for player in players:

    output.append({

        "Player": player,

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
            results[player]["Round64"] / NUM_SIMS,

        "Strength":
            strength_dict[player]
    })

results_df = pd.DataFrame(output)

# =========================================================
# 11. SORT RESULTS
# =========================================================

results_df = results_df.sort_values(
    by="TitlePct",
    ascending=False
)

# =========================================================
# 12. SAVE RESULTS
# =========================================================

results_df.to_csv(
    "french_open_2026_monte_carlo_resultsv1.csv",
    index=False
)

# =========================================================
# 13. DISPLAY RESULTS
# =========================================================

print()
print("===================================")
print("MONTE CARLO COMPLETE")
print("===================================")
print()

print(results_df.head(20))

print()
print("Results saved to:")
print("french_open_2026_monte_carlo_resultsv1.csv")