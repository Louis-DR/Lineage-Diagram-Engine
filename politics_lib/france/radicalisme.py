from ..base import PoliticalParty, Date
from ..constants import *
from .socialisme import la_convention_federation
from .centralisme import union_pour_la_democratie_francaise

#region[radicalisme]

parti_radical = PoliticalParty(
  symbol        = "PRAD MR PRV",
  color         = "#C71982",
  creation_date = Date(1901,6,21),
  initial_name  = "Parti Radical et Radical-Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.20,
)

parti_radical.set_results_presidential_election(Date(1906),   43.8)
parti_radical.set_results_presidential_election(Date(1913),   37.7)
parti_radical.set_results_presidential_election(Date(1920,1),  0.0)
parti_radical.set_results_presidential_election(Date(1920,9),  0.0)
parti_radical.set_results_presidential_election(Date(1924),   60.4, True)
parti_radical.set_results_presidential_election(Date(1931),   49.3, True)
parti_radical.set_results_presidential_election(Date(1932),    0.0)
parti_radical.set_results_presidential_election(Date(1939),    5.5)
parti_radical.set_results_presidential_election(Date(1947),   13.8)
parti_radical.set_results_presidential_election(Date(1953),   13.9)
parti_radical.set_results_presidential_election(Date(1958),    0.0)
parti_radical.set_results_presidential_election(Date(1965),    0.0) # Soutien à François Mitterrand
parti_radical.set_results_presidential_election(Date(1969),    0.0) # Soutien à Alain Poher
parti_radical.set_results_presidential_election(Date(1974),    0.0) # Soutien à Valéry Giscard d'Estaing
parti_radical.set_results_presidential_election(Date(1981),    0.0) # Soutien à Valéry Giscard d'Estaing
parti_radical.set_results_presidential_election(Date(1988),    0.0) # Soutien à Raymond Barre
parti_radical.set_results_presidential_election(Date(1995),    0.0) # Soutien à Édouard Balladur
parti_radical.set_results_presidential_election(Date(2002),    0.0) # Soutien à Jacques Chirac
parti_radical.set_results_presidential_election(Date(2007),    0.0) # Soutien à Nicolas Sarkozy
parti_radical.set_results_presidential_election(Date(2012),    0.0) # Soutien à Nicolas Sarkozy
parti_radical.set_results_presidential_election(Date(2017),    0.0) # Soutien à François Fillon
parti_radical.set_results_presidential_election(Date(2022),    0.0) # Soutien à Emmanuel Macron

parti_radical.set_results_legislative_election(Date(1902),        17.7,      104, True)
parti_radical.set_results_legislative_election(Date(1906),        28.53,     132, True)
parti_radical.set_results_legislative_election(Date(1910),        39.17,     261, True)
parti_radical.set_results_legislative_election(Date(1914),        18.15,     192, True)
parti_radical.set_results_legislative_election(Date(1919),        17.47,      86, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1924),        17.86,     139, True)
parti_radical.set_results_legislative_election(Date(1928),        17.77,     125, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1932),        19.18,     160, True)
parti_radical.set_results_legislative_election(Date(1936),        15.17,     115, True)
parti_radical.set_results_legislative_election(Date(1945),        10.54,      60)       # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1946,6),      11.61,      32)       # Coalition du RGR, résultat partagé, opposition
parti_radical.set_results_legislative_election(Date(1946,11),     11.12,      42, True) # Coalition du RGR, résultat partagé
parti_radical.set_results_legislative_election(Date(1951),        11.13,      90, True) # Coalition du RGR, résultat partagé
parti_radical.set_results_legislative_election(Date(1956),        10.99,      54, True) # Coalition du FR, résultat partagé avec l'UDSR
parti_radical.set_results_legislative_election(Date(1958),         8.40,      57, True) # Parfois dans l'opposition
parti_radical.set_results_legislative_election(Date(1962),         7.42,      41)
parti_radical.set_results_legislative_election(Date(1967), 75/429*18.90,      24) # Coalition de la FGDS, 75 circonscriptions sur 429
parti_radical.set_results_legislative_election(Date(1968), 77/442*16.54+0.36, 15) # Coalition de la FGDS, 77 circonscriptions sur 442, plus non-coalisés
parti_radical.set_results_legislative_election(Date(1973),   4/31*13.26,       4) # Coalition du MR, 4 sièges sur 31
parti_radical.set_results_legislative_election(Date(1978),  9/128*21.5,        9) # Composante de l'UDF,  9 sièges sur 128
parti_radical.set_results_legislative_election(Date(1981),   2/65*19.2,        2) # Composante de l'UDF,  2 sièges sur  65
parti_radical.set_results_legislative_election(Date(1986),  7/127*21.4,        7) # Composante de l'UDF,  7 sièges sur 127
parti_radical.set_results_legislative_election(Date(1988),  3/129*18.5,        3) # Composante de l'UDF,  3 sièges sur 129
parti_radical.set_results_legislative_election(Date(1993), 14/215*18.6,       14) # Composante de l'UDF, 14 sièges sur 215
parti_radical.set_results_legislative_election(Date(1997),  3/114*14.2,        3) # Composante de l'UDF,  3 sièges sur 114
parti_radical.set_results_legislative_election(Date(2002),  9/358*33.30,       9) # Composante de l'UMP,  9 sièges sur 358
parti_radical.set_results_legislative_election(Date(2007), 16/313*39.54,      16) # Composante de l'UMP, 16 sièges sur 313
parti_radical.set_results_legislative_election(Date(2012),         1.24,       6)
parti_radical.set_results_legislative_election(Date(2017),    3/18*3.03,       3) # Composante de l'UDI
parti_radical.set_results_legislative_election(Date(2022),         0.52,       5)
parti_radical.set_results_legislative_election(Date(2024),         0.54,       2)

# parti_radical                        Date(1901,6,21)              +0.20  # Création
parti_radical.shift_political_position(Date(1946), Date(1958),      +0.05) # Glissement pendant la IVe
parti_radical.shift_political_position(Date(1958), Date(1972),      -0.10) # Glissement du début de la Ve
# parti_radical                        Date(1971,11,17)             -0.50  # Scission de l'aile gauche
parti_radical.shift_political_position(Date(2017), Date(2017,12,9), -1.10+centre_offset) # Mouvement Radical

parti_radical.set_prominence_tier(Date(1967), "minor")
parti_radical.set_prominence_tier(Date(2019), "micro")

parti_radical.name_change(Date(2017,12, 9), "Mouvement Radical")
parti_radical.name_change(Date(2021, 9,12), "Parti Radical")

parti_radical.shift_political_position(Date(1972), Date(1973), -0.50) # Scission de l'aile gauche

parti_radical_de_gauche_1971 = PoliticalParty(
  symbol        = "MGRS MRG RAD PRS PRG(1971)",
  color         = "#C71982",
  creation_date = Date(1971,11,17),
  initial_name  = "Groupe d'Études et d'Action Radical-Socialiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    parti_radical: {
      "ratio": 0.5, # 7 députés sur 15
      "source_new_position": -0.50
    }
  }
)
parti_radical_de_gauche_1971.name_change(Date(1972,10, 4), "Mouvement de la Gauche Radicale-Socialiste")
parti_radical_de_gauche_1971.name_change(Date(1973, 1),    "Mouvement des Radicaux de Gauche")
parti_radical_de_gauche_1971.name_change(Date(1994,11, 5), "Radical")
parti_radical_de_gauche_1971.name_change(Date(1996, 8, 6), "Parti Radical Socialiste")
parti_radical_de_gauche_1971.name_change(Date(1998, 1,13), "Parti Radical de Gauche")

# parti_radical_de_gauche_1971                        Date(1971,11,17)        +0.30+gauche_offset  # Creation
parti_radical_de_gauche_1971.shift_political_position(Date(1981), Date(1984), +0.10+gauche_offset) # Tournant de la rigueur
parti_radical_de_gauche_1971.shift_political_position(Date(1995), Date(1997), -0.10+gauche_offset) # Troisième voie du PS
parti_radical_de_gauche_1971.shift_political_position(Date(2012), Date(2017), -0.30+gauche_offset) # Quinquennat Hollande

parti_radical_de_gauche_1971.merge_into(Date(2017,12,9), parti_radical, 0.5) # Mouvement Radical

parti_radical_de_gauche_2019 = PoliticalParty(
  symbol        = "PRG(2019)",
  color         = "#C71982",
  creation_date = Date(2019,2,6),
  initial_name  = "Parti Radical de Gauche",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.10+gauche_offset,
  secede_from = {
    parti_radical: {
      "ratio": 0.5,
      "source_new_position": -1.57+centre_offset,
    }
  }
)
parti_radical_de_gauche_2019.join(Date(2023,3,14), la_convention_federation)

#endregion
