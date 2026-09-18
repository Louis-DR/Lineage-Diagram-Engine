from ..base import PoliticalParty, Date
from ..constants import *

#region[communisme]


federation_des_travailleurs_socialistes_de_france = PoliticalParty(
  symbol        = "FPTSF FTSF",
  color         = "#FF0000",
  creation_date = Date(1879,4,30),
  initial_name  = "Fédération du Parti des Travailleurs Socialistes de France",
  initial_prominence_tier    = "major",
  initial_political_position = +1.20+gauche_offset,
)
federation_des_travailleurs_socialistes_de_france.name_change(Date(1883,10,7), "Fédération des Travailleurs Socialistes de France")

federation_des_groupes_socialistes_revolutionnaires_independants = PoliticalParty(
  symbol        = "FGSRI",
  color         = "#FF0000",
  creation_date = Date(1898,12,4),
  initial_name  = "Fédération des Groupes Socialistes Révolutionnaires Indépendants",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.85+gauche_offset,
)
federation_des_socialistes_revolutionnaires_independants_de_france = PoliticalParty(
  symbol        = "FSRI FSRIF",
  color         = "#FF0000",
  creation_date = Date(1899,1,1),
  initial_name  = "Fédération des Socialistes Indépendants de France",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.75+gauche_offset,
)
federation_des_socialistes_revolutionnaires_independants_de_france.name_change(Date(1900,3,27), "Fédération des Socialistes Révolutionnaires Indépendants de France")

federation_socialiste_revolutionnaire_de_france = PoliticalParty(
  symbol        = "FSR",
  color         = "#FF0000",
  creation_date = Date(1901,8,5),
  initial_name  = "Fédération Socialiste Révolutionnaire de France",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.80+gauche_offset,
  merge_from = [
    federation_des_socialistes_revolutionnaires_independants_de_france,
    federation_des_groupes_socialistes_revolutionnaires_independants,
  ],
)

parti_socialiste_francais = PoliticalParty(
  symbol        = "PSF",
  color         = "#FF0000",
  creation_date = Date(1902,3,4),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "major",
  initial_political_position = +1.00+gauche_offset,
  merge_from = [
    federation_socialiste_revolutionnaire_de_france,
    federation_des_travailleurs_socialistes_de_france,
  ],
)


parti_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "CRC PSR",
  color         = "#FF0000",
  creation_date = Date(1881,6,26),
  initial_name  = "Comité Révolutionnaire Central",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.70+gauche_offset,
)
parti_socialiste_revolutionnaire.name_change(Date(1898,7,1), "Parti Socialiste Révolutionnaire")

comite_central_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "CCSR",
  color         = "#FF0000",
  creation_date = Date(1889,8,20),
  initial_name  = "Comité Central Socialiste Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.00+gauche_offset, # boulangistes, rejoint le nationalisme
  secede_from = {
    parti_socialiste_revolutionnaire: {
      "ratio": 0,
    }
  }
)
comite_central_socialiste_revolutionnaire.dissolve(Date(1896,12))

parti_ouvrier_francais = PoliticalParty(
  symbol        = "PO POF",
  color         = "#FF0000",
  creation_date = Date(1882,9,30),
  initial_name  = "Parti Ouvrier",
  initial_prominence_tier    = "major",
  initial_political_position = +1.60+gauche_offset,
  secede_from = {
    federation_des_travailleurs_socialistes_de_france: {
      "ratio": 0,
      "source_new_position": +0.60+gauche_offset
    }
  }
)
parti_ouvrier_francais.name_change(Date(1893,9,19), "Parti Ouvrier Français")

parti_socialiste_de_france = PoliticalParty(
  symbol        = "USR PSdF",
  color         = "#FF0000",
  creation_date = Date(1901,6,30),
  initial_name  = "Unité Socialiste Révolutionnaire",
  initial_prominence_tier    = "major",
  initial_political_position = +1.65+gauche_offset,
  merge_from = [
    parti_socialiste_revolutionnaire,
    parti_ouvrier_francais,
  ],
)
parti_socialiste_de_france.name_change(Date(1901,11,3), "Parti Socialiste de France")



parti_ouvrier_socialiste_revolutionnaire = PoliticalParty(
  symbol        = "POSR",
  color         = "#FF0000",
  creation_date = Date(1890,10,15),
  initial_name  = "Parti Ouvrier Socialiste Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.45+gauche_offset,
  secede_from = {
    federation_des_travailleurs_socialistes_de_france: {
      "ratio": 0,
    }
  }
)

alliance_communiste_revolutionnaire = PoliticalParty(
  symbol        = "ACR",
  color         = "#FF0000",
  creation_date = Date(1896,9,25),
  initial_name  = "Alliance Communiste Révolutionnaire",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.52+gauche_offset,
  secede_from = {
    parti_ouvrier_socialiste_revolutionnaire: {
      "ratio": 0,
    }
  }
)
alliance_communiste_revolutionnaire.merge_into(Date(1897,9), parti_socialiste_revolutionnaire, 0)



section_francaise_de_linternationale_ouvriere = PoliticalParty(
  symbol        = "SFIO",
  color         = "#FF0000",
  creation_date = Date(1905,4,25),
  initial_name  = "Section Française de 'Internationale Ouvrière",
  initial_prominence_tier    = "major",
  initial_political_position = +1.40+gauche_offset,
  merge_from = [
    parti_socialiste_de_france,
    parti_socialiste_francais,
    parti_ouvrier_socialiste_revolutionnaire,
  ],
)

section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1906),   7.26)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1920,9), 8.78)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1932),  14.67)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1939),  16.70)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1947),  51.19, True)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1953),  37.77)
section_francaise_de_linternationale_ouvriere.set_results_presidential_election(Date(1969),   5.01)

section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1906),    10.0,  54)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1910),    12.9,  75)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1914),    16.8, 102)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1919),    21.2,  68)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1924),    20.1, 104, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1928),    18.0, 100)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1932),    20.5, 132)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1936),    19.2, 149, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1945),    23.4, 134, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1946,6),  21.1, 128, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1946,11), 17.9, 102, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1951),    14.5, 107, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1956),    14.9,  95, True)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1958),    17.2,  47)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1962),    12.4,  66)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1967),    18.8,  76)
section_francaise_de_linternationale_ouvriere.set_results_legislative_election(Date(1968),    16.5,  40)

section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1959), 61)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1952), 52)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1965), 52)
section_francaise_de_linternationale_ouvriere.set_results_senatorial_election(Date(1968), 52)


parti_ouvrier_1914 = PoliticalParty(
  symbol        = "PO(1914)",
  color         = "#FF0000",
  creation_date = Date(1914,1,28),
  initial_name  = "Parti Ouvrier",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.50+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0,
    }
  }
)
parti_ouvrier_1914.merge_into(Date(1917,11), section_francaise_de_linternationale_ouvriere, 0)


parti_republicain_socialiste_1910 = PoliticalParty(
  symbol        = "PSR PRS(1910)",
  color         = "#FF0000",
  creation_date = Date(1907,3,31),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.40+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.3
    }
  },
)
parti_republicain_socialiste_1910.name_change(Date(1910,10,8), "Parti Républicain Socialiste")
parti_republicain_socialiste_1910.name_change(Date(1914,2,8),  "Parti Républicain Socialiste (briandiste)")
parti_republicain_socialiste_1914 = PoliticalParty(
  symbol        = "PRS(1914)",
  color         = "#FF0000",
  creation_date = Date(1914,2,8),
  initial_name  = "Parti Républicain Socialiste (augagneuriste)",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    parti_republicain_socialiste_1910: {
      "ratio": 0.3
    }
  },
)
parti_republicain_socialiste_1910.dissolve(Date(1915))
parti_republicain_socialiste_1914.dissolve(Date(1915))
parti_socialiste_national = PoliticalParty(
  symbol        = "PSN",
  color         = "#FF0000",
  creation_date = Date(1917,12,23),
  initial_name  = "Parti Socialiste National",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.10+gauche_offset,
)
parti_socialiste_national.dissolve(Date(1921))
parti_republicain_socialiste_1923 = PoliticalParty(
  symbol        = "PRS-1923",
  color         = "#FF0000",
  creation_date = Date(1923,4,15),
  initial_name  = "Parti Républicain Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.40+gauche_offset,
)

parti_republicain_socialiste_1928 = PoliticalParty(
  symbol        = "PRS-1928",
  color         = "#FF0000",
  creation_date = Date(1928,5,20),
  initial_name  = "Parti Républicain Socialiste",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.40+gauche_offset,
)

parti_socialiste_francais_1920 = PoliticalParty(
  symbol        = "PSF-1920",
  color         = "#FF0000",
  creation_date = Date(1920,3,13),
  initial_name  = "Parti Socialiste Français",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.60+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  },
)
parti_socialiste_francais_1929 = PoliticalParty(
  symbol        = "PRSSF PSF(1929)",
  color         = "#FF0000",
  creation_date = Date(1926,5,30),
  initial_name  = "Parti Républicain Socialiste et Socialiste Français",
  initial_prominence_tier    = "major",
  initial_political_position = +0.50+gauche_offset,
  merge_from = [
    parti_socialiste_francais_1920,
    parti_republicain_socialiste_1923,
  ],
)
parti_socialiste_francais_1929.name_change(Date(1929,12,8), "Parti Socialiste Français")

parti_socialiste_de_france_union_jean_jaures = PoliticalParty(
  symbol        = "PSdF-UJJ",
  color         = "#FF0000",
  creation_date = Date(1933,11,5),
  initial_name  = "Parti Socialiste de France - Union Jean Jaurès",
  initial_prominence_tier    = "major",
  initial_political_position = +0.30+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.4
    }
  },
)

union_socialiste_républicaine = PoliticalParty(
  symbol        = "USR",
  color         = "#FF0000",
  creation_date = Date(1935,11,3),
  initial_name  = "Union Socialiste Républicaine",
  initial_prominence_tier    = "major",
  initial_political_position = +0.40+gauche_offset,
  merge_from = [
    parti_socialiste_francais_1929,
    parti_republicain_socialiste_1928,
    parti_socialiste_de_france_union_jean_jaures,
  ],
)
union_socialiste_républicaine.dissolve(Date(1940,7,10)) # Dissolution pendant la guerre





parti_communiste_francais = PoliticalParty(
  symbol        = "PCF",
  color         = "#FF0000",
  creation_date = Date(1920,12,30),
  initial_name  = "Section Française de l'Internationale Communiste",
  initial_prominence_tier    = "major",
  initial_political_position = +1.8+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0.2,
      "source_new_position": +1.00+gauche_offset
    }
  },
)

parti_communiste_francais.set_results_presidential_election(Date(1924),  2.5)
parti_communiste_francais.set_results_presidential_election(Date(1931),  1.1)
parti_communiste_francais.set_results_presidential_election(Date(1932),  1.0)
parti_communiste_francais.set_results_presidential_election(Date(1939),  8.2)
parti_communiste_francais.set_results_presidential_election(Date(1953), 12.2)
parti_communiste_francais.set_results_presidential_election(Date(1958), 13.03)
parti_communiste_francais.set_results_presidential_election(Date(1969), 21.27)
parti_communiste_francais.set_results_presidential_election(Date(1981), 15.35)
parti_communiste_francais.set_results_presidential_election(Date(1988),  6.76)
parti_communiste_francais.set_results_presidential_election(Date(1995),  8.64)
parti_communiste_francais.set_results_presidential_election(Date(2002),  3.37)
parti_communiste_francais.set_results_presidential_election(Date(2007),  1.93)
parti_communiste_francais.set_results_presidential_election(Date(2012), 11.10) # Jean-Luc Mélanchon
parti_communiste_francais.set_results_presidential_election(Date(2022),  2.28)

parti_communiste_francais.set_results_legislative_election(Date(1924),     9.82,  26)
parti_communiste_francais.set_results_legislative_election(Date(1928),    11.26,  12)
parti_communiste_francais.set_results_legislative_election(Date(1932),     8.32,  23)
parti_communiste_francais.set_results_legislative_election(Date(1936),    15.23,  72, True)
parti_communiste_francais.set_results_legislative_election(Date(1945),    26.23, 159, True)
parti_communiste_francais.set_results_legislative_election(Date(1946,6),  25.98, 153, True)
parti_communiste_francais.set_results_legislative_election(Date(1946,11), 28.26, 182, True)
parti_communiste_francais.set_results_legislative_election(Date(1951),    25.90, 103)
parti_communiste_francais.set_results_legislative_election(Date(1956),    25.36, 150)
parti_communiste_francais.set_results_legislative_election(Date(1958),    18.90,  10)
parti_communiste_francais.set_results_legislative_election(Date(1962),    21.84,  41)
parti_communiste_francais.set_results_legislative_election(Date(1967),    22.51,  73)
parti_communiste_francais.set_results_legislative_election(Date(1968),    20.02,  34)
parti_communiste_francais.set_results_legislative_election(Date(1973),    21.41,  73)
parti_communiste_francais.set_results_legislative_election(Date(1978),    20.61,  86)
parti_communiste_francais.set_results_legislative_election(Date(1981),    16.17,  44, True)
parti_communiste_francais.set_results_legislative_election(Date(1986),     9.78,  35)
parti_communiste_francais.set_results_legislative_election(Date(1988),    11.32,  27, True)
parti_communiste_francais.set_results_legislative_election(Date(1993),     9.30,  24)
parti_communiste_francais.set_results_legislative_election(Date(1997),     9.92,  35, True)
parti_communiste_francais.set_results_legislative_election(Date(2002),     4.82,  21)
parti_communiste_francais.set_results_legislative_election(Date(2007),     4.29,  15)
parti_communiste_francais.set_results_legislative_election(Date(2012),     6.91,   7)
parti_communiste_francais.set_results_legislative_election(Date(2017),     2.72,  11)
parti_communiste_francais.set_results_legislative_election(Date(2022),     2.29,  12)
parti_communiste_francais.set_results_legislative_election(Date(2024),     2.35,   8)

parti_communiste_francais.set_results_senatorial_election(Date(1995), 14)
parti_communiste_francais.set_results_senatorial_election(Date(1998), 14)
parti_communiste_francais.set_results_senatorial_election(Date(2001), 18)
parti_communiste_francais.set_results_senatorial_election(Date(2004), 20)
parti_communiste_francais.set_results_senatorial_election(Date(2008), 21)
parti_communiste_francais.set_results_senatorial_election(Date(2011), 19)
parti_communiste_francais.set_results_senatorial_election(Date(2014), 16)
parti_communiste_francais.set_results_senatorial_election(Date(2017), 12)
parti_communiste_francais.set_results_senatorial_election(Date(2020), 14)
parti_communiste_francais.set_results_senatorial_election(Date(2023), 14)

parti_communiste_francais.set_results_european_election(Date(1979), 20.52, 19)
parti_communiste_francais.set_results_european_election(Date(1984), 11.21, 10)
parti_communiste_francais.set_results_european_election(Date(1989),  7.72,  7)
parti_communiste_francais.set_results_european_election(Date(1994),  6.89,  7)
parti_communiste_francais.set_results_european_election(Date(1999),  6.78,  6)
parti_communiste_francais.set_results_european_election(Date(2004),  5.88,  2)
parti_communiste_francais.set_results_european_election(Date(2009),  6.48,  2) # Front de Gauche
parti_communiste_francais.set_results_european_election(Date(2014),  6.61,  1) # Front de Gauche
parti_communiste_francais.set_results_european_election(Date(2019),  2.49,  0)
parti_communiste_francais.set_results_european_election(Date(2024),  2.36,  0)




union_federative_socialiste = PoliticalParty(
  symbol        = "UFS",
  color         = "#FF0000",
  creation_date = Date(1922,10,19),
  initial_name  = "Union Fédérative Socialiste",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.40+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_communiste_unitaire = PoliticalParty(
  symbol        = "CDC CUC PCU",
  color         = "#FF0000",
  creation_date = Date(1923,1,3),
  initial_name  = "Comité de Défense Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.40+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_communiste_unitaire.name_change(Date(1923,1,10), "Comité d'Unité Communiste")
parti_communiste_unitaire.name_change(Date(1923,1,17), "Parti Communiste Unitaire")
parti_socialiste_communiste = PoliticalParty(
  symbol        = "PSC",
  color         = "#FF0000",
  creation_date = Date(1923,4,30),
  initial_name  = "Parti Socialiste Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.40+gauche_offset,
  merge_from = [
    union_federative_socialiste,
    parti_communiste_unitaire,
  ],
)
parti_socialiste_communiste.secede_into(Date(1927,10), section_francaise_de_linternationale_ouvriere, 0, visual_width=2)
parti_ouvrier_et_paysan = PoliticalParty(
  symbol        = "POP",
  color         = "#FF0000",
  creation_date = Date(1929,11,24),
  initial_name  = "Parti Ouvrier et Paysan",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.50+gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  },
)
parti_de_lunite_proletarienne = PoliticalParty(
  symbol        = "PUP",
  color         = "#FF0000",
  creation_date = Date(1930,12,21),
  initial_name  = "Parti de l'Unité Prolétarienne",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.45+gauche_offset,
  merge_from = [
    parti_socialiste_communiste,
    parti_ouvrier_et_paysan,
  ],
)
parti_de_lunite_proletarienne.shift_political_position(Date(1934), Date(1936), +1.30+gauche_offset) # Front Populaire
parti_de_lunite_proletarienne.merge_into(Date(1937,1,31), section_francaise_de_linternationale_ouvriere, 0)



parti_socialiste_ouvrier_et_paysan = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Socialiste_Ouvrier_et_Paysan_(PSOP)
  symbol        = "PSOP",
  color         = "#FF0000",
  creation_date = Date(1938,6,8),
  initial_name  = "Parti Socialiste Ouvrier et Paysan",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.20+gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  }
)
parti_socialiste_ouvrier_et_paysan.dissolve(Date(1940))

groupe_bolchevik_leniniste = PoliticalParty(
  # https://www.france-politique.fr/wiki/Groupe_Bolchevik-L%C3%A9niniste_(GBL)
  symbol        = "LC GBL",
  color         = "#770000",
  creation_date = Date(1930,12,21),
  initial_name  = "Ligue Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  secede_from = {
    parti_communiste_francais: {
      "ratio": 0
    }
  }
)
groupe_bolchevik_leniniste.name_change(Date(1934,8,24), "Groupe Bolchevik-Léniniste")
jeunesses_socialistes_revolutionnaires = PoliticalParty(
  # https://www.france-politique.fr/wiki/Jeunesses_Socialistes_R%C3%A9volutionnaires_(JSR)
  symbol        = "JSR",
  color         = "#770000",
  creation_date = Date(1935,7,30),
  initial_name  = "Jeunesses Socialistes Révolutionnaires",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      "ratio": 0
    }
  }
)
parti_ouvrier_revolutionnaire = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Ouvrier_R%C3%A9volutionnaire_(POR)
  symbol        = "POR",
  color         = "#770000",
  creation_date = Date(1936,4,12),
  initial_name  = "Parti Ouvrier Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  merge_from = [
    groupe_bolchevik_leniniste,
    jeunesses_socialistes_revolutionnaires,
  ],
)
# parti_communiste_internationaliste_1936 = PoliticalParty(
#   # https://www.france-politique.fr/wiki/Comit%C3%A9_Communiste_Internationaliste_pour_la_Construction_de_la_Quatri%C3%A8me_Internationale_(CCI)
#   symbol        = "CQI PCI(1936)",
#   color         = "#770000",
#   creation_date = Date(1936,1,16),
#   initial_name  = "Comité pour la Quatrième Internationale",
#   initial_prominence_tier    = "minor",
#   initial_political_position = +2.05+extreme_gauche_offset,
#   secede_from = {
#     section_francaise_de_linternationale_ouvriere: {
#       "ratio": 0
#     }
#   }
# )
# parti_communiste_internationaliste_1936.name_change(Date(1936,3,8), "Parti Communiste Internationaliste")
parti_ouvrier_internationaliste = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Ouvrier_Internationaliste_(POI)_1936
  symbol        = "POI",
  color         = "#770000",
  creation_date = Date(1936,6,2),
  initial_name  = "Parti Ouvrier Internationaliste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  # merge_from = [
  #   parti_ouvrier_revolutionnaire,
  #   parti_communiste_internationaliste_1936,
  # ],
  secede_from = {
    section_francaise_de_linternationale_ouvriere: {
      # This is the PCI-1936
      "ratio": 0
    }
  }
)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale = PoliticalParty(
  # https://www.france-politique.fr/wiki/Comit%C3%A9_Communiste_Internationaliste_pour_la_Construction_de_la_Quatri%C3%A8me_Internationale_(CCI)
  symbol        = "PCI CCI",
  color         = "#770000",
  creation_date = Date(1936,10,12),
  initial_name  = "Parti Communiste Internationaliste",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
  # secede_from = {
  #   parti_ouvrier_internationaliste: {
  #     "ratio": 0
  #   }
  # }
)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale.shift_political_position(Date(1936,10,12), Date(1936,10,12)+160, +1.95+extreme_gauche_offset)
comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale.name_change(Date(1943,4,1), "Comité Communiste Internationaliste pour la Construction de la Quatrième Internationale")
groupe_octobre = PoliticalParty(
  # https://www.france-politique.fr/wiki/Octobre
  symbol        = "GO",
  color         = "#770000",
  creation_date = Date(1942),
  initial_name  = "Groupe Octobre",
  initial_prominence_tier    = "micro",
  initial_political_position = +2.05+extreme_gauche_offset,
  secede_from = {
    comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale: {
      "ratio": 0
    }
  }
)
parti_communiste_internationaliste_1944 = PoliticalParty(
  # https://www.france-politique.fr/wiki/Parti_Communiste_Internationaliste_(PCI)_1944
  symbol        = "PCI-1944",
  color         = "#770000",
  creation_date = Date(1944,3),
  initial_name  = "Parti Communiste Internationaliste",
  initial_prominence_tier    = "minor",
  initial_political_position = +2.10+extreme_gauche_offset,
  merge_from = [
    parti_ouvrier_internationaliste,
    comite_communiste_internationaliste_pour_la_construction_de_la_quatrieme_internationale,
    groupe_octobre,
  ],
)

jeunesse_communiste_revolutionnaire = PoliticalParty(
  # https://www.france-politique.fr/wiki/Jeunesse_Communiste_R%C3%A9volutionnaire_(JCR)
  symbol        = "JCR",
  color         = "#770000",
  creation_date = Date(1966,4,2),
  initial_name  = "Jeunesse Communiste Révolutionnaire",
  initial_prominence_tier    = "minor",
  initial_political_position = +1.90+extreme_gauche_offset,
)

ligue_communiste = PoliticalParty(
  # https://www.france-politique.fr/nouveau-parti-anticapitaliste.htm
  symbol        = "LC FCR LCR NPA",
  color         = "#770000",
  creation_date = Date(1969,4,8),
  initial_name  = "Ligue Communiste",
  initial_prominence_tier    = "minor",
  initial_political_position = +2.00+extreme_gauche_offset,
  merge_from = [
    parti_communiste_internationaliste_1944,
    jeunesse_communiste_revolutionnaire,
  ],
)
# ligue_communiste dissoute le Date(1973,6,28)
front_communiste_revolutionnaire = ligue_communiste                 .name_change(Date(1974,4,10),  "Front Communiste Révolutionnaire")
ligue_communiste_revolutionnaire = front_communiste_revolutionnaire .name_change(Date(1974,12,22), "Ligue Communiste Révolutionnaire")
nouveau_parti_anticapitaliste    = ligue_communiste_revolutionnaire .name_change(Date(2009,2,5),   "Nouveau Parti Anticapitaliste")

#endregion
