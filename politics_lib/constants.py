from .date import Date

# Importance calculation constants
IMPORTANCE_CHANGE_DURATION = Date(0,9,0)
MINIMAL_IMPORTANCE                     = 1.00
IMPORTANCE_POWER                       = 1.00 # Exponentiation of the total importance
IMPORTANCE_MULTIPLIER                  = 1.00 # Multiplier on the total importance
PRESIDENTIAL_IMPORTANCE_MULTIPLIER     = 0.20 # Multiplier on the presidential importance
LEGISLATIVE_IMPORTANCE_MULTIPLIER      = 0.60 # Multiplier on the legislative importance
SENATORIAL_IMPORTANCE_MULTIPLIER       = 0.10 # Multiplier on the senatorial importance
EUROPEAN_IMPORTANCE_MULTIPLIER         = 0.10 # Multiplier on the european importance
PRESIDENTIAL_IMPORTANCE_VOTES_WEIGHT   = 0.50 # Weight of the first turn votes on presidential importance
PRESIDENTIAL_IMPORTANCE_VICTORY_WEIGHT = 0.50 # Weight of the victory on the presidential importance
LEGISLATIVE_IMPORTANCE_VOTES_WEIGHT    = 0.40 # Weight of the votes in first turn on legislative importance
LEGISLATIVE_IMPORTANCE_SEATS_WEIGHT    = 0.40 # Weight of the seat representation on legislative importance
LEGISLATIVE_IMPORTANCE_MAJORITY_WEIGHT = 0.20 # Weight of the majority on legislative importance
SENATORIAL_IMPORTANCE_SEATS_WEIGHT     = 0.80 # Weight of the seat representation on senatorial importance
SENATORIAL_IMPORTANCE_MAJORITY_WEIGHT  = 0.20 # Weight of the majority on senatorial importance
EUROPEAN_IMPORTANCE_VOTES_WEIGHT       = 0.40 # Weight of the votes in first turn on european importance
EUROPEAN_IMPORTANCE_SEATS_WEIGHT       = 0.60 # Weight of the seat representation on european importance

# Prominence tier bonuses (additive before exponentiation)
IMPORTANCE_TIER_BONUS_MICRO = 1.0
IMPORTANCE_TIER_BONUS_MINOR = 2.0
IMPORTANCE_TIER_BONUS_MAJOR = 5.0

# Ideological offsets
extreme_gauche_offset = +0.5
gauche_offset         = +0.3
centre_offset         = +0.1
droite_offset         =  0.0
extreme_droite_offset = +0.1
