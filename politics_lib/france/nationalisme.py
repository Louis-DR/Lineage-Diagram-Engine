from ..base import PoliticalParty, Date
from ..constants import *
from .gaullisme import les_republicains

#region[nationalisme]

front_national = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Rassemblement_national
  # https://www.france-politique.fr/chronologie-fn.htm
  symbol        = "FN RN",
  color         = "#8A5928",
  creation_date = Date(1972,10,5),
  initial_name  = "Front National",
  initial_prominence_tier    = "major",
  initial_political_position = -2.80+extreme_droite_offset,
)
rassemblement_national = front_national.name_change(Date(2018,6,1), "Rassemblement National")

front_national        .set_results_presidential_election(Date(1974),  0.75)
front_national        .set_results_presidential_election(Date(1988), 14.39)
front_national        .set_results_presidential_election(Date(1995), 15.00)
front_national        .set_results_presidential_election(Date(2002), 16.86)
front_national        .set_results_presidential_election(Date(2007), 10.44)
front_national        .set_results_presidential_election(Date(2012), 17.90)
front_national        .set_results_presidential_election(Date(2017), 21.30)
rassemblement_national.set_results_presidential_election(Date(2022), 23.15)

front_national        .set_results_legislative_election(Date(1973),  1.33,   0)
front_national        .set_results_legislative_election(Date(1978),  0.29,   0)
front_national        .set_results_legislative_election(Date(1981),  0.18,   0)
front_national        .set_results_legislative_election(Date(1986),  9.65,  35)
front_national        .set_results_legislative_election(Date(1988),  9.66,   1)
front_national        .set_results_legislative_election(Date(1993), 12.42,   0)
front_national        .set_results_legislative_election(Date(1997), 14.94,   1)
front_national        .set_results_legislative_election(Date(2002), 11.34,   0)
front_national        .set_results_legislative_election(Date(2007),  4.29,   0)
front_national        .set_results_legislative_election(Date(2012), 13.60,   1)
front_national        .set_results_legislative_election(Date(2017), 13.20,   7)
rassemblement_national.set_results_legislative_election(Date(2022), 18.61,  82)
rassemblement_national.set_results_legislative_election(Date(2024), 28.05, 119)

front_national        .set_results_senatorial_election(Date(2014), 2)
front_national        .set_results_senatorial_election(Date(2017), 2)
rassemblement_national.set_results_senatorial_election(Date(2020), 1)
rassemblement_national.set_results_senatorial_election(Date(2023), 3)

front_national        .set_results_european_election(Date(1984), 11.95, 10)
front_national        .set_results_european_election(Date(1989), 11.73, 10)
front_national        .set_results_european_election(Date(1994), 10.52, 11)
front_national        .set_results_european_election(Date(1999),  5.69,  5)
front_national        .set_results_european_election(Date(2004),  9.81,  7)
front_national        .set_results_european_election(Date(2009),  6.34,  4)
front_national        .set_results_european_election(Date(2014), 24.86, 24)
rassemblement_national.set_results_european_election(Date(2019), 23.34, 21)
rassemblement_national.set_results_european_election(Date(2024), 31.37, 30)

# rassemblement_national                        Date(1972,10,5)         -2.80+extreme_droite_offset  # Creation
rassemblement_national.shift_political_position(Date(1982), Date(1986), -2.75+extreme_droite_offset) #
rassemblement_national.shift_political_position(Date(2013), Date(2017), -2.60+extreme_droite_offset) # Marine LePen, changement de nom
rassemblement_national.shift_political_position(Date(2018), Date(2023), -2.50+extreme_droite_offset) # Dédiablisation

union_des_droites_pour_la_republique = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Union_des_droites_pour_la_R%C3%A9publique
  # https://www.france-politique.fr/wiki/Union_des_Droites_pour_la_R%C3%A9publique_(UDR)
  symbol        = "UDR",
  color         = "#0045B0",
  creation_date = Date(2024,6,30),
  initial_name  = "Union des Droites pour la République",
  initial_prominence_tier    = "minor",
  initial_political_position = -2.50+extreme_droite_offset,
  secede_from = {
    les_republicains: {
      "ratio": 0.3
    }
  },
  inside_entity = rassemblement_national,
)

#endregion
