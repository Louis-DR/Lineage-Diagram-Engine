from .constants import *
from .date import Date
from .base import (
    PoliticalSystem,
    PoliticalParty,
    PoliticalFederation,
    PoliticalAlliance,
)

# Import all france regions to register them in the system
from .france import (
    political_system,
    anarchisme,
    trotskisme,
    communisme,
    socialisme,
    insoumission,
    ecosocialiste,
    radicalisme,
    centralisme,
    gaullisme,
    agrarisme,
    nationalisme,
)
