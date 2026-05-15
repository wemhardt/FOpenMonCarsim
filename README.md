# FOpenMonCarsim
Monte Carlo simulation of upcoming French Open
Overview
This project builds a Monte Carlo simulation framework to estimate advancement and title probabilities for the 2026 French Open men's singles tournament. Rather than relying only on rankings, the model combines match-level performance metrics, opponent quality, recency effects, surface-specific form, Grand Slam seeding logic, and matchup interactions.

The simulation estimates probabilities for:
Tournament Champion
Finals
Semifinals
Quarterfinals
Round of 16
Round of 32
Round of 64

Data Collection
Match-level data for the top 128 ATP players was scraped from Tennis Abstract using custom Python scripts.
Data collected included:
  Return Points Won %
  First Serve Return Points Won %
  Second Serve Return Points Won %
  Break Point Conversion/Saved
  Opponent Rank
  Match Dates
  Surface Information
  Additional performance metrics
  Feature Engineering


Raw match data was transformed into predictive player features.
  Key engineered variables:
    Break Points Forced
    Break Points Faced
    Opponent quality weighting
    Recency weighting
    Surface-specific statistics
    Rank normalization
    Opponent weighting:
      OpponentWeight = 1 / ln(vRank + 1)
    Recency weighting:
      TimeWeight = exp(-0.003 × DaysAgo)
    Combined match weight:
    CombinedWeight = OpponentWeight × TimeWeight

This weighting system emphasizes:
Recent form
Strong opponents
Relevant pre-tournament performance



Strength Model
Two player strength systems were created:
Clay Strength
Clay-only performance metrics
Overall Strength
All-surface weighted metrics

Final player strength:
FinalStrength = approx. 0.70 × ClayStrength + approx. 0.30 × OverallStrength (weights=1)
This blend captures both clay specialization and long-term player quality.

Matchup Interaction Effects
Clay-specific interaction terms were introduced to capture stylistic matchups:
  Return Pressure Edge
  Clay_RPW(A) − Clay_SecondServeWon(B)
  Measures how effectively a player attacks an opponent's weaker service points.

  Second Serve Stability Edge
  Clay_SecondServeWon(A) − Clay_SecondServeWon(B)
  Measures comparative second-serve quality.


Tournament Simulation
The simulation includes realistic Grand Slam seeding:
Seeds 1–2 opposite halves
Seeds 3–4 opposite quarters
Protected top 32 seeds
Randomized unseeded placement
Match probabilities are modeled using a logistic function and adjusted for best-of-5 Grand Slam dynamics.
10,000+ tournament simulations are run to generate advancement probabilities.


Technologies Used
Python
Pandas
NumPy
Playwright
Google Sheets

Future Improvements
Planned enhancements:
Set-level best-of-5 simulation
Historical calibration
Injury adjustments
Surface Elo systems
Bayesian uncertainty modeling
Head-to-head effects

This project was built as a sports analytics and predictive modeling exercise focused on combining domain expertise with probabilistic simulation methods.
