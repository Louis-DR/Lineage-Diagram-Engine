from ..base import PoliticalParty, Date
from ..constants import *
from .socialisme import generations

#region[ecosocialiste]

mouvement_decologie_politique = PoliticalParty(
  symbol        = "CIMÉ MÉP VPÉ",
  color         = "#66C52C",
  creation_date = Date(1974,11,9),
  initial_name  = "Mouvement Écologique",
  initial_prominence_tier    = "micro",
  initial_political_position = +0.03+gauche_offset,
)

mouvement_decologie_politique.name_change(Date(1978, 7, 1), "Coordination Interrégionale des Mouvements Écologistes")
mouvement_decologie_politique.name_change(Date(1980, 1,16), "Mouvement d'Écologie Politique")
mouvement_decologie_politique.name_change(Date(1982,11, 1), "Verts, Parti Écologiste")

confederation_ecologiste = PoliticalParty(
  symbol        = "RAT CÉ LVCÉ",
  color         = "#66C52C",
  creation_date = Date(1977,5,22),
  initial_name  = "Réseau des Amis de la Terre",
  initial_prominence_tier    = "micro",
  initial_political_position = -0.03+gauche_offset,
)

confederation_ecologiste.name_change(Date(1981,12,13), "Confédération Écologiste")
confederation_ecologiste.name_change(Date(1983, 5,23), "Les Verts - Confédération Écologiste")

les_ecologistes = PoliticalParty(
  symbol        = "LV EELV LÉ",
  color         = "#66C52C",
  creation_date = Date(1984,1,29),
  initial_name  = "Les Verts - Confédération Écologiste, Parti Écologiste",
  initial_prominence_tier    = "major",
  initial_political_position = +0.00+gauche_offset,
  merge_from = [
    mouvement_decologie_politique,
    confederation_ecologiste,
  ]
)

les_ecologistes.name_change(Date(2010,11,13), "Europe Écologistes Les Verts")
les_ecologistes.name_change(Date(2024, 6,30), "Les Écologistes")

les_ecologistes.shift_political_position(Date(1994), Date(1995), +0.60+gauche_offset) # Fin du "ni-ni"

generations.join(Date(2020,8), les_ecologistes)

#endregion
