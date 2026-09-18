from ..base import PoliticalParty, Date
from ..constants import *

#region[trotskisme]

lutte_ouvriere = PoliticalParty(
  symbol        = "LO",
  color         = "#770000",
  creation_date = Date(1956,11,26),
  initial_name  = "Voix Ouvrière",
  initial_prominence_tier    = "minor",
  initial_political_position = +2.30+extreme_gauche_offset,
)

lutte_ouvriere.set_results_presidential_election(Date(1974), 2.33)
lutte_ouvriere.set_results_presidential_election(Date(1981), 2.30)
lutte_ouvriere.set_results_presidential_election(Date(1988), 1.99)
lutte_ouvriere.set_results_presidential_election(Date(1995), 5.30)
lutte_ouvriere.set_results_presidential_election(Date(2002), 5.72)
lutte_ouvriere.set_results_presidential_election(Date(2007), 1.33)
lutte_ouvriere.set_results_presidential_election(Date(2012), 0.56)
lutte_ouvriere.set_results_presidential_election(Date(2017), 0.64)
lutte_ouvriere.set_results_presidential_election(Date(2022), 0.56)

lutte_ouvriere.set_results_legislative_election(Date(1973), 2.29)
lutte_ouvriere.set_results_legislative_election(Date(1978), 1.70)
lutte_ouvriere.set_results_legislative_election(Date(1981), 1.11)
lutte_ouvriere.set_results_legislative_election(Date(1986), 0.63)
lutte_ouvriere.set_results_legislative_election(Date(1993), 2.15)
lutte_ouvriere.set_results_legislative_election(Date(1997), 3.86)
lutte_ouvriere.set_results_legislative_election(Date(2002), 1.20)
lutte_ouvriere.set_results_legislative_election(Date(2007), 0.86)
lutte_ouvriere.set_results_legislative_election(Date(2012), 0.51)
lutte_ouvriere.set_results_legislative_election(Date(2017), 0.72)
lutte_ouvriere.set_results_legislative_election(Date(2022), 1.01)
lutte_ouvriere.set_results_legislative_election(Date(2024), 1.09)

lutte_ouvriere.set_results_european_election(Date(1979), 3.08, 0)
lutte_ouvriere.set_results_european_election(Date(1984), 2.07, 0)
lutte_ouvriere.set_results_european_election(Date(1989), 1.43, 0)
lutte_ouvriere.set_results_european_election(Date(1994), 2.27, 0)
lutte_ouvriere.set_results_european_election(Date(1999), 5.18, 3)
lutte_ouvriere.set_results_european_election(Date(2004), 2.60, 0)
lutte_ouvriere.set_results_european_election(Date(2009), 1.20, 0)
lutte_ouvriere.set_results_european_election(Date(2014), 1.17, 0)
lutte_ouvriere.set_results_european_election(Date(2019), 0.78, 0)
lutte_ouvriere.set_results_european_election(Date(2024), 0.49, 0)

#endregion
