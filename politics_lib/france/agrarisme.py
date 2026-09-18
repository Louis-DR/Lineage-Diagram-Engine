from ..base import PoliticalParty, PoliticalFederation, Date
from ..constants import *


#region[agrarisme]

parti_agraire_et_paysan_francais = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_agraire_et_paysan_fran%C3%A7ais
  # https://www.france-politique.fr/wiki/Parti_Agraire_et_Paysan_Fran%C3%A7ais_(PAPF)
  symbol        = "PAPF",
  color         = "#255D32",
  creation_date = Date(1927,11,26),
  initial_name  = "Parti Agraire et Paysan Français",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
)

parti_republicain_agraire_et_social = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_r%C3%A9publicain_agraire_et_social
  # https://www.france-politique.fr/wiki/Parti_R%C3%A9publicain_Agraire_et_Social_(PRAS)
  symbol        = "PRAS",
  color         = "#255D32",
  creation_date = Date(1936,2,5),
  initial_name  = "Parti Républicain Agraire et Social",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
  secede_from = {
    parti_agraire_et_paysan_francais: {
      "ratio": 0
    }
  },
)
parti_republicain_agraire_et_social.dissolve(Date(1940))

parti_paysan_dunion_sociale = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Parti_paysan_d%27union_sociale
  # https://www.france-politique.fr/wiki/Mouvement_D%C3%A9mocrate_et_Paysan_(MDP)
  symbol        = "PPUS",
  color         = "#255D32",
  creation_date = Date(1945,3,12),
  initial_name  = "Parti Paysan d'Union Sociale",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
  merge_from = [
    parti_agraire_et_paysan_francais,
  ]
)

comites_de_defense_paysane = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Comit%C3%A9s_de_d%C3%A9fense_paysanne
  # https://www.france-politique.fr/wiki/Comit%C3%A9s_de_D%C3%A9fense_Paysanne_(DP)
  symbol        = "DP",
  color         = "#013502",
  creation_date = Date(1948,10,10),
  initial_name  = "Comités de Défense Paysanne",
  initial_prominence_tier    = "micro",
  initial_political_position = -1.20+droite_offset,
)

# https://www.france-politique.fr/wiki/Rassemblement_Paysan_(RP)

centre_national_des_independants_et_paysans = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Centre_national_des_ind%C3%A9pendants_et_paysans
  # https://www.france-politique.fr/chronologie-cnip.htm
  symbol        = "CNI CNIP",
  color         = "#255D32",
  creation_date = Date(1949,1,6),
  initial_name  = "Centre National des Indépendants",
  initial_prominence_tier    = "major",
  initial_political_position = -1.20+droite_offset,
)
parti_paysan_dunion_sociale.merge_into(Date(1951,2,15), centre_national_des_independants_et_paysans)
centre_national_des_independants_et_paysans.name_change(Date(1951,2,15), "Centre National des Indépendants et Paysans")

#endregion