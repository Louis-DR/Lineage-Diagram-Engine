from ..base import PoliticalParty, PoliticalFederation, Date
from ..constants import *
from .communisme import section_francaise_de_linternationale_ouvriere, parti_communiste_francais

#region[socialisme]

union_des_clubs_pour_le_renouveau_de_la_gauche = PoliticalParty(
  symbol        = "UCRG",
  color         = "#FF0000",
  creation_date = Date(1966,2),
  initial_name  = "Union des Clubs pour le Renouveau de la Gauche",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.45+gauche_offset,
)

union_des_groupes_et_clubs_socialistes = PoliticalParty(
  symbol        = "UGCS",
  color         = "#FF0000",
  creation_date = Date(1967),
  initial_name  = "Union des Groupes et Clubs Socialistes",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.40+gauche_offset,
)

parti_socialiste = PoliticalParty(
  symbol        = "PS",
  color         = "#E3265B",
  creation_date = Date(1969,8,4),
  initial_name  = "Parti Socialiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.80+gauche_offset,
  merge_from = [
    section_francaise_de_linternationale_ouvriere,
    union_des_clubs_pour_le_renouveau_de_la_gauche,
    union_des_groupes_et_clubs_socialistes,
  ],
)

convention_des_institutions_republicaines = PoliticalParty(
  symbol        = "CIR",
  color         = "#FF0000",
  creation_date = Date(1964,6,11),
  initial_name  = "Convention des Institutions Républicaines",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.30+gauche_offset,
)
convention_des_institutions_republicaines.merge_into(Date(1971,6,13), parti_socialiste, 0)

parti_socialiste.set_results_presidential_election(Date(1969),  5.01)
parti_socialiste.set_results_presidential_election(Date(1974), 43.25)
parti_socialiste.set_results_presidential_election(Date(1981), 25.85, True)
parti_socialiste.set_results_presidential_election(Date(1988), 34.10, True)
parti_socialiste.set_results_presidential_election(Date(1995), 23.30)
parti_socialiste.set_results_presidential_election(Date(2002), 16.18)
parti_socialiste.set_results_presidential_election(Date(2007), 25.87)
parti_socialiste.set_results_presidential_election(Date(2012), 28.63, True)
parti_socialiste.set_results_presidential_election(Date(2017),  6.36)
parti_socialiste.set_results_presidential_election(Date(2022),  1.75)

parti_socialiste.set_results_legislative_election(Date(1973), 18.9,   89)
parti_socialiste.set_results_legislative_election(Date(1978), 22.8,  104)
parti_socialiste.set_results_legislative_election(Date(1981), 36.0,  267, True)
parti_socialiste.set_results_legislative_election(Date(1986), 31.0,  203)
parti_socialiste.set_results_legislative_election(Date(1988), 34.8,  275, True)
parti_socialiste.set_results_legislative_election(Date(1993), 17.6,   59)
parti_socialiste.set_results_legislative_election(Date(1997), 23.53, 255, True)
parti_socialiste.set_results_legislative_election(Date(2002), 24.11, 140)
parti_socialiste.set_results_legislative_election(Date(2007), 24.73, 186)
parti_socialiste.set_results_legislative_election(Date(2012), 29.35, 280, True)
parti_socialiste.set_results_legislative_election(Date(2017),  7.44,  30)
parti_socialiste.set_results_legislative_election(Date(2022),  3.86,  28)
parti_socialiste.set_results_legislative_election(Date(2024),  8.65,  65)

parti_socialiste.set_results_senatorial_election(Date(1971),  49)
parti_socialiste.set_results_senatorial_election(Date(1974),  51)
parti_socialiste.set_results_senatorial_election(Date(1977),  62)
parti_socialiste.set_results_senatorial_election(Date(1980),  69)
parti_socialiste.set_results_senatorial_election(Date(1983),  70)
parti_socialiste.set_results_senatorial_election(Date(1986),  64)
parti_socialiste.set_results_senatorial_election(Date(1989),  66)
parti_socialiste.set_results_senatorial_election(Date(1992),  70)
parti_socialiste.set_results_senatorial_election(Date(1995),  75)
parti_socialiste.set_results_senatorial_election(Date(1998),  78)
parti_socialiste.set_results_senatorial_election(Date(2001),  83)
parti_socialiste.set_results_senatorial_election(Date(2004),  97)
parti_socialiste.set_results_senatorial_election(Date(2008), 116)
parti_socialiste.set_results_senatorial_election(Date(2011), 140, True)
parti_socialiste.set_results_senatorial_election(Date(2014), 111)
parti_socialiste.set_results_senatorial_election(Date(2017),  78)
parti_socialiste.set_results_senatorial_election(Date(2020),  64)
parti_socialiste.set_results_senatorial_election(Date(2023),  64)

parti_socialiste.set_results_european_election(Date(1979), 23.53, 20)
parti_socialiste.set_results_european_election(Date(1984), 20.75, 20)
parti_socialiste.set_results_european_election(Date(1989), 23.61, 17)
parti_socialiste.set_results_european_election(Date(1994), 14.49, 15)
parti_socialiste.set_results_european_election(Date(1999), 21.95, 18)
parti_socialiste.set_results_european_election(Date(2004), 28.90, 31)
parti_socialiste.set_results_european_election(Date(2009), 16.48, 14)
parti_socialiste.set_results_european_election(Date(2014), 13.98, 12)
parti_socialiste.set_results_european_election(Date(2019),  6.19,  3)
parti_socialiste.set_results_european_election(Date(2024), 13.83, 10)

# section_francaise_de_linternationale_ouvriere                        Date(1905,4,25)         +1.40+gauche_offset  # Création
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1914), Date(1915), +1.10+gauche_offset) # L'Union Sacrée et gouvernement, nationalisme pour la guerre
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1918), Date(1920), +1.40+gauche_offset) # Fin de la guerre et de l'Union Sacrée
# section_francaise_de_linternationale_ouvriere                        Date(1920,12,30)        +1.00+gauche_offset  # Scission de la SFIC/PCF, le reste est social-démocratie réformiste
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1934), Date(1936), +0.90+gauche_offset) # Front Populaire, modération stratégique
section_francaise_de_linternationale_ouvriere.shift_political_position(Date(1944), Date(1945), +0.80+gauche_offset) # Libération, refondation

# parti_communiste_francais                        Date(1920,12,30)        +1.80+gauche_offset  # Scission depuis la SFIO
parti_communiste_francais.shift_political_position(Date(1934), Date(1936), +1.60+gauche_offset) # Front Populaire, soutien sans participation
parti_communiste_francais.shift_political_position(Date(1939), Date(1941), +1.80+gauche_offset) # Pacte germano-soviétique, fin du Front Populaire
parti_communiste_francais.shift_political_position(Date(1970), Date(1972), +1.60+gauche_offset) # Négociation du Programme Commun, Eurocommunisme
parti_communiste_francais.shift_political_position(Date(1981), Date(1984), +1.50+gauche_offset) # Participation au gouvernement Mauroy, sortie avec le tournant de la rigueur
parti_communiste_francais.shift_political_position(Date(1991), Date(1997), +1.00+gauche_offset) # Chute de l'URSS jusqu'à la Gauche Plurielle, abandon Léninisme, changement symboles
parti_communiste_francais.shift_political_position(Date(2015), Date(2018), +0.80+gauche_offset) # Fin du Front de Gauche, Rousselisation jusqu'à la NUPES

# parti_socialiste                        Date(1969,8,4)              +0.80+gauche_offset  # Création
parti_socialiste.shift_political_position(Date(1969,8,4), Date(1972), +0.90+gauche_offset) # De Épinay au Programme Commun
parti_socialiste.shift_political_position(Date(1983),     Date(1984), +0.40+gauche_offset) # Tournant de la rigueur
parti_socialiste.shift_political_position(Date(1995),     Date(1997), +0.20+gauche_offset) # Troisième voie
parti_socialiste.shift_political_position(Date(2013),     Date(2015),  0.00+gauche_offset) # Virage social libéral
parti_socialiste.shift_political_position(Date(2017),     Date(2022), +0.30+gauche_offset) # Retour à gauche

nouvelle_donne = PoliticalParty(
  symbol        = "ND",
  color         = "#C23089",
  creation_date = Date(2013,11,28),
  initial_name  = "Nouvelle Donne",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.42+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

generations = PoliticalParty(
  symbol        = "G·s",
  color         = "#D9185D",
  creation_date = Date(2017,7,1),
  initial_name  = "Génération·s",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.50+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

gauche_democratique_et_sociale = PoliticalParty(
  symbol        = "GDS",
  color         = "#EE3437",
  creation_date = Date(2017,11,21),
  initial_name  = "Gauche Démocratique et Sociale",
  initial_prominence_tier    = "micro",
  initial_political_position = +1.00+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

place_publique = PoliticalParty(
  symbol        = "PP",
  color         = "#FEF10A",
  creation_date = Date(2018,11,6),
  initial_name  = "Place Publique",
  initial_prominence_tier    = "minor",
  initial_political_position = +0.05+gauche_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
  inside_entity = parti_socialiste,
)

territoires_de_progres = PoliticalParty(
  # https://fr.wikipedia.org/wiki/D%C3%A9mocrates_et_progressistes
  symbol        = "TdP",
  color         = "#E1435E",
  creation_date = Date(2020,2,1),
  initial_name  = "Territoires de Progrès",
  initial_prominence_tier    = "minor",
  initial_political_position = -0.70+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

collectif_des_sociaux_democrates_reformateurs = PoliticalParty(
  # https://fr.wikipedia.org/wiki/D%C3%A9mocrates_et_progressistes
  symbol        = "CSDR",
  color         = "#8307BD",
  # creation_date = Date(2022,12,1),
  creation_date = Date(2022,12,1)-160,
  initial_name  = "Collectif des Sociaux-Démocrates Réformateurs",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.70+centre_offset,
  secede_from = {
    territoires_de_progres: {
      "ratio": 0
    }
  },
)

federation_progressiste = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Fran%C3%A7ois_Rebsamen#F%C3%A9d%C3%A9ration_progressiste_et_retour_au_gouvernement
  symbol        = "FP",
  color         = "#FB0057",
  creation_date = Date(2022,5,19),
  initial_name  = "La Convention",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.60+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
)

la_convention_federation = PoliticalFederation(
  # https://fr.wikipedia.org/wiki/Bernard_Cazeneuve#Retour_actif_en_politique_et_La_Convention_(depuis_2022)
  # Virtual for the federation around La Convention
  symbol        = "CONV_FED",
  color         = "#5D1354",
  creation_date = Date(2022), # Virtual for transitions
  initial_name  = "La Convention",
  initial_political_position = -0.20+centre_offset,
)
la_convention = PoliticalParty(
  # https://fr.wikipedia.org/wiki/Bernard_Cazeneuve#Retour_actif_en_politique_et_La_Convention_(depuis_2022)
  symbol        = "CONV",
  color         = "#5D1354",
  creation_date = Date(2023,2,1),
  initial_name  = "La Convention",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.20+centre_offset,
  secede_from = {
    parti_socialiste: {
      "ratio": 0
    }
  },
  inside_entity = la_convention_federation
)

collectif_des_sociaux_democrates_reformateurs.join(Date(2023,3,14), la_convention_federation)
federation_progressiste.join(Date(2025,6), la_convention_federation)

#endregion
