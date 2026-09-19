from ..base import PoliticalParty, PoliticalFederation, Date
from ..constants import *
from .radicalisme import parti_radical
# from .centralisme import union_pour_la_democratie_francaise
from .agrarisme import centre_national_des_independants_et_paysans

#region[gaullisme]

republicains_independants = PoliticalParty(
  symbol        = "RI FNRI PR DL",
  color         = "#002153",
  creation_date = Date(1962,12,2),
  initial_name  = "Républicains Indépendants",
  initial_prominence_tier    = "minor",
  initial_political_position = -0.70+centre_offset,
  secede_from = {
    centre_national_des_independants_et_paysans: {
      "ratio": 0.2, # TBD
    }
  }
)
federation_nationale_des_republicains_independants         = republicains_independants                          .name_change(Date(1966,6,1),  "Fédération Nationale des Républicains Indépendants")
parti_republicain                                          = federation_nationale_des_republicains_independants .name_change(Date(1977,5,20), "Parti Républicain")
democratie_liberale                                        = parti_republicain                                  .name_change(Date(1997,6,24), "Démocratie Libérale")
# democratie_liberale.leave(Date(1998,5,16), union_pour_la_democratie_francaise)
# democratie_liberale fusionne dans l'UMP peu après sa création


rassemblement_pour_la_republique = PoliticalParty(
  symbol        = "RPF",
  color         = "#021A6F",
  creation_date = Date(1976,12,5),
  initial_name  = "Rassemblement Pour la République",
  initial_prominence_tier    = "major",
  initial_political_position = -1.45+droite_offset,
)

rassemblement_pour_la_republique.set_results_presidential_election(Date(1981), 18.00)
rassemblement_pour_la_republique.set_results_presidential_election(Date(1988), 19.94)
rassemblement_pour_la_republique.set_results_presidential_election(Date(1995), 20.84 + 18.58, True) # Chirac et Balladur au premier tour
rassemblement_pour_la_republique.set_results_presidential_election(Date(2002), 19.88, True)

rassemblement_pour_la_republique.set_results_legislative_election(Date(1978), 22.5, 150, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1981), 20.8,  85)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1986), 11.2, 147, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1988), 19.2, 127)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1993), 19.8, 245, True)
rassemblement_pour_la_republique.set_results_legislative_election(Date(1997), 15.7, 139)

# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1977), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1980), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1983), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1986), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1989), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1992), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1995), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(1998), )
# rassemblement_pour_la_republique.set_results_senatorial_election(Date(2001), )

rassemblement_pour_la_republique.set_results_european_election(Date(1979), 16.3, 15)
rassemblement_pour_la_republique.set_results_european_election(Date(1984), 43.0, 20)
rassemblement_pour_la_republique.set_results_european_election(Date(1989), 28.9, 13)
rassemblement_pour_la_republique.set_results_european_election(Date(1994), 25.6, 14)
rassemblement_pour_la_republique.set_results_european_election(Date(1999), 12.8, 12)

union_pour_un_mouvement_populaire = PoliticalParty(
  symbol        = "UMP LR",
  color         = "#0045B0",
  creation_date = Date(2002,4,23),
  initial_name  = "Union pour un Mouvement Populaire",
  initial_prominence_tier    = "major",
  initial_political_position = -1.45+droite_offset,
  merge_from = [
    rassemblement_pour_la_republique,
    democratie_liberale, # Date(2002,11,17)
  ]
)
les_republicains = union_pour_un_mouvement_populaire.name_change(Date(2015,5,30), "Les Républicains")

union_pour_un_mouvement_populaire.set_results_presidential_election(Date(2007), 31.18, True)
union_pour_un_mouvement_populaire.set_results_presidential_election(Date(2012), 27.18)
les_republicains                 .set_results_presidential_election(Date(2017), 20.01)
les_republicains                 .set_results_presidential_election(Date(2022),  4.78)

union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2002), 33.30, 358, True)
union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2007), 39.54, 313, True)
union_pour_un_mouvement_populaire.set_results_legislative_election(Date(2012), 27.12, 194)
les_republicains                 .set_results_legislative_election(Date(2017), 15.77, 112)
les_republicains                 .set_results_legislative_election(Date(2022), 10.55,  61)
les_republicains                 .set_results_legislative_election(Date(2024),  7.55,  48)

union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2004), 156, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2008), 151, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2011), 132, True)
union_pour_un_mouvement_populaire.set_results_senatorial_election(Date(2014), 143, True)
les_republicains                 .set_results_senatorial_election(Date(2017), 146, True)
les_republicains                 .set_results_senatorial_election(Date(2020), 148, True)
les_republicains                 .set_results_senatorial_election(Date(2023), 139, True)

union_pour_un_mouvement_populaire.set_results_european_election(Date(2004), 16.64, 17)
union_pour_un_mouvement_populaire.set_results_european_election(Date(2009), 27.88, 24) # Liste commune avec le NC (trois sièges) et la GM (deux sièges).
union_pour_un_mouvement_populaire.set_results_european_election(Date(2014), 20.80, 20)
les_republicains                 .set_results_european_election(Date(2019),  8.48,  7)
les_republicains                 .set_results_european_election(Date(2024),  7.25,  6)

# union_pour_un_mouvement_populaire                        Date(2002,4,23)                     -1.45+droite_offset  # Creation UMP
union_pour_un_mouvement_populaire.shift_political_position(Date(2006),       Date(2009),       -1.80+droite_offset) # Sarkozisme
les_republicains                 .shift_political_position(Date(2017, 6,18), Date(2022, 6,19), -1.95+droite_offset) # Macronisme

parti_radical.join (Date(2002,4,23), union_pour_un_mouvement_populaire)
parti_radical.leave(Date(2011,5,14), union_pour_un_mouvement_populaire)


#endregion
