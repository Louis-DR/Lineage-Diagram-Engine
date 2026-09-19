from ..base import PoliticalParty, PoliticalFederation, Date
from ..constants import *
from .socialisme import la_convention_federation, territoires_de_progres
from .gaullisme import union_pour_un_mouvement_populaire, les_republicains, republicains_independants
from radicalisme import parti_radical

#region[centralisme]

centre_des_democrates_sociaux = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Centre_des_d%C3%A9mocrates_sociaux
  # https://www.france-politique.fr/centre-des-democrates-sociaux.htm
  symbol        = "CDS",
  color         = "#4f4591",
  creation_date = Date(1962,12,2),
  initial_name  = "Centre des Démocrates Sociaux",
  initial_prominence_tier    = "minor",
  initial_political_position = -0.60+centre_offset,
  merge_from = [
    # centre_democrate,
    # centre_democrate_et_progres,
  ]
)

union_pour_la_democratie_francaise = PoliticalFederation(
  symbol        = "UDF",
  color         = "#00FFFF",
  creation_date = Date(1978,2,1),
  initial_name  = "Union pour la Démocratie Française",
  initial_political_position = -0.50+centre_offset,
  initial_members = [
    republicains_independants,
    parti_radical,
  ],
)

parti_radical.leave(Date(2002,10,27), union_pour_la_democratie_francaise)
parti_radical.join( Date(2002,10,27), union_pour_un_mouvement_populaire)

nouvelle_union_pour_la_democratie_francaise = PoliticalParty(
  symbol        = "NUDF",
  color         = "#F07400",
  creation_date = Date(1998,11,29),
  initial_name  = "Union pour la Démocratie Française",
  initial_prominence_tier    = "major",
  initial_political_position = -0.50+centre_offset,
)

nouvelle_union_pour_la_democratie_francaise.set_results_presidential_election(Date(2002),  6.84)
nouvelle_union_pour_la_democratie_francaise.set_results_presidential_election(Date(2007), 18.57)

nouvelle_union_pour_la_democratie_francaise.set_results_legislative_election(Date(2002), 4.86, 27)

nouvelle_union_pour_la_democratie_francaise.set_results_european_election(Date(2004), 11.96, 11)

mouvement_democrate = PoliticalParty(
  symbol        = "MoDem",
  color         = "#EF5222",
  creation_date = Date(2007,5,10),
  initial_name  = "Union pour un Mouvement Populaire",
  initial_prominence_tier    = "major",
  initial_political_position = -0.90+centre_offset,
  merge_from = [
    nouvelle_union_pour_la_democratie_francaise
  ]
)

mouvement_democrate.set_results_presidential_election(Date(2012), 9.13)

mouvement_democrate.set_results_legislative_election(Date(2007), 7.61,  3)
mouvement_democrate.set_results_legislative_election(Date(2012), 1.77,  2)
mouvement_democrate.set_results_legislative_election(Date(2017), 4.11, 42, True)
mouvement_democrate.set_results_legislative_election(Date(2022), 4.62, 46, True)
mouvement_democrate.set_results_legislative_election(Date(2024), 3.80, 36, True)

mouvement_democrate.set_results_european_election(Date(2009),  8.46, 6)
mouvement_democrate.set_results_european_election(Date(2014),  9.94, 4) # Au sein de L'Alternative avec l'Union des démocrates et indépendants (3 sièges).
mouvement_democrate.set_results_european_election(Date(2019), 22.42, 5) # Liste commune avec La République en marche (11 sièges), Agir (1 siège), le Mouvement radical, social et libéral (1 siège) et Alliance centriste, avec 3 élus sans étiquette.
mouvement_democrate.set_results_european_election(Date(2024), 14.60, 4) # Liste commune avec Renaissance (5 sièges), Horizons (2 sièges), l'UDI (1 siège) et le Parti radical avec 1 élu sans étiquette.

renaissance = PoliticalParty(
  symbol        = "EM LREM RE",
  color         = "#FFD600",
  creation_date = Date(2016,4,6),
  initial_name  = "En Marche",
  initial_prominence_tier    = "major",
  initial_political_position = -0.50+centre_offset,
)
renaissance.name_change(Date(2017,8, 4), "La République En Marche")
renaissance.name_change(Date(2022,9,17), "Renaissance")

renaissance.set_results_presidential_election(Date(2017), 24.01, True)
renaissance.set_results_presidential_election(Date(2022), 27.85, True)

renaissance.set_results_legislative_election(Date(2017), 28.21, 308, True)
renaissance.set_results_legislative_election(Date(2022), 16.52, 157, True)
renaissance.set_results_legislative_election(Date(2024), 12.32,  92, True)

renaissance.set_results_senatorial_election(Date(2017), 21)
renaissance.set_results_senatorial_election(Date(2020), 21)
renaissance.set_results_senatorial_election(Date(2023), 22)

renaissance.set_results_european_election(Date(2019), 22.42, 12)
renaissance.set_results_european_election(Date(2024), 14.60,  5)

renaissance.shift_political_position(Date(2018), Date(2022), -1.30+centre_offset)

en_commun = PoliticalParty(
  symbol        = "EC",
  color         = "#DC6863",
  creation_date = Date(2020,10,14),
  initial_name  = "En Commun",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.35+centre_offset,
  secede_from = {
    renaissance: {
      "ratio": 0.0,
    }
  }
)
en_commun.join(Date(2025,4), la_convention_federation)

territoires_de_progres.join(Date(2022,9,17), renaissance)

agir = PoliticalParty(
  symbol        = "Agir",
  color         = "#43519E",
  creation_date = Date(2017,11,26),
  initial_name  = "En Commun",
  initial_prominence_tier    = "minor",
  initial_political_position = -1.62+centre_offset,
  secede_from = {
    les_republicains: {
      "ratio": 0.0,
    }
  }
)

agir.join(Date(2022,9,17), renaissance)

horizon = PoliticalParty(
  symbol        = "HOR",
  color         = "#0000BA",
  creation_date = Date(2021,10,9),
  initial_name  = "Horizon",
  initial_prominence_tier    = "major",
  initial_political_position = -1.68+centre_offset,
  secede_from = {
    renaissance: {
      "ratio": 0.0,
    },
    agir: {
      "ratio": 0.0,
    }
  }
)

#endregion
