from ..base import PoliticalParty, Date
from ..constants import *
from .socialisme import parti_socialiste, gauche_democratique_et_sociale

#region[insoumission]

la_france_insoumise = PoliticalParty(
  symbol        = "PdG LFI",
  color         = "#CC2443",
  creation_date = Date(2008,11,29),
  initial_name  = "Parti de Gauche",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.80+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

la_france_insoumise.set_prominence_tier(Date(2016,2,10), "major")
la_france_insoumise.shift_political_position(Date(2015), Date(2018), +1.20+gauche_offset) # Fin du Front de Gauche

la_france_insoumise.set_results_presidential_election(Date(2012), 11.10) # Jean-Luc Mélanchon investi par le PCF
la_france_insoumise.set_results_presidential_election(Date(2017), 19.58)
la_france_insoumise.set_results_presidential_election(Date(2022), 21.95)

la_france_insoumise.set_results_legislative_election(Date(2012), 6.91*102/577, 1)
la_france_insoumise.set_results_legislative_election(Date(2017), 11.03, 17)
la_france_insoumise.set_results_legislative_election(Date(2022), 14.22, 75)
la_france_insoumise.set_results_legislative_election(Date(2024), 10.49, 71)

la_france_insoumise.set_results_senatorial_election(Date(2014), 0)
la_france_insoumise.set_results_senatorial_election(Date(2017), 0)
la_france_insoumise.set_results_senatorial_election(Date(2020), 0)
la_france_insoumise.set_results_senatorial_election(Date(2023), 0)

la_france_insoumise.set_results_european_election(Date(2009), 6.48, 2) # Front de Gauche
la_france_insoumise.set_results_european_election(Date(2014), 6.61, 4) # Front de Gauche
la_france_insoumise.set_results_european_election(Date(2019), 6.31, 6)
la_france_insoumise.set_results_european_election(Date(2024), 9.89, 9)

lapres = PoliticalParty(
  symbol        = "L'A",
  color         = "#F39E36",
  creation_date = Date(2024,5,21),
  initial_name  = "L'Après",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.05+gauche_offset,
  secede_from = {
    la_france_insoumise: {
      "ratio": 0
    }
  },
)

gauche_democratique_et_sociale.merge_into(Date(2025,2,1), lapres, 0.0)

#endregion
