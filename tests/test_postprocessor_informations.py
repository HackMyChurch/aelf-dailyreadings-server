'''
Information cleanup is tedious. These tests run over a full year.

Input data were collected using:

```
cd test_fixtures/informations
for i in {0..365}
do
    day=$(date +%Y-%m-%d -d "2023-09-01 + $i day")
    wget "https://api.aelf.org/v1/informations/$day/france" -qO $day.json
done
```
'''

import os
import json

FIXTURES_BASE_PATH="./test_fixtures/informations"

EXPECTED_DAY = {
    "2023-09-01": {"year": "impaire", "psalter": 1,    "day": "vendredi"},
    "2023-09-02": {"year": "impaire", "psalter": 1,    "day": "samedi"  },
    "2023-09-03": {"year": "a",       "psalter": 2,    "day": "dimanche"},
    "2023-09-04": {"year": "impaire", "psalter": 2,    "day": "lundi"   },
    "2023-09-05": {"year": "impaire", "psalter": 2,    "day": "mardi"   },
    "2023-09-06": {"year": "impaire", "psalter": 2,    "day": "mercredi"},
    "2023-09-07": {"year": "impaire", "psalter": 2,    "day": "jeudi"   },
    "2023-09-08": {"year": "impaire", "psalter": None, "day": "Nativité de\u00a0Marie"},
    "2023-09-09": {"year": "impaire", "psalter": 2,    "day": "samedi"  },
    "2023-09-10": {"year": "a",       "psalter": 3,    "day": "dimanche"},
    "2023-09-11": {"year": "impaire", "psalter": 3,    "day": "lundi"   },
    "2023-09-12": {"year": "impaire", "psalter": 3,    "day": "mardi"   },
    "2023-09-13": {"year": "impaire", "psalter": 3,    "day": "mercredi"},
    "2023-09-14": {"year": "impaire", "psalter": None, "day": "Croix\u00a0Glorieuse"},
    "2023-09-15": {"year": "impaire", "psalter": 3,    "day": "vendredi"},
    "2023-09-16": {"year": "impaire", "psalter": 3,    "day": "samedi"  },
    "2023-09-17": {"year": "a",       "psalter": 4,    "day": "dimanche"},
    "2023-09-18": {"year": "impaire", "psalter": 4,    "day": "lundi"   },
    "2023-09-19": {"year": "impaire", "psalter": 4,    "day": "mardi"   },
    "2023-09-20": {"year": "impaire", "psalter": 4,    "day": "mercredi"},
    "2023-09-21": {"year": "impaire", "psalter": None, "day": "Saint\u00a0Matthieu"},
    "2023-09-22": {"year": "impaire", "psalter": 4,    "day": "vendredi"},
    "2023-09-23": {"year": "impaire", "psalter": 4,    "day": "samedi"  },
    "2023-09-24": {"year": "a",       "psalter": 1,    "day": "dimanche"},
    "2023-09-25": {"year": "impaire", "psalter": 1,    "day": "lundi"   },
    "2023-09-26": {"year": "impaire", "psalter": 1,    "day": "mardi"   },
    "2023-09-27": {"year": "impaire", "psalter": 1,    "day": "mercredi"},
    "2023-09-28": {"year": "impaire", "psalter": 1,    "day": "jeudi"   },
    "2023-09-29": {"year": "impaire", "psalter": None, "day": "vendredi"},
    "2023-09-30": {"year": "impaire", "psalter": 1,    "day": "samedi"  },
    "2023-10-01": {"year": "a",       "psalter": 2,    "day": "dimanche"},
    "2023-10-02": {"year": "impaire", "psalter": 2,    "day": "lundi"   },
    "2023-10-03": {"year": "impaire", "psalter": 2,    "day": "mardi"   },
    "2023-10-04": {"year": "impaire", "psalter": 2,    "day": "mercredi"},
    "2023-10-05": {"year": "impaire", "psalter": 2,    "day": "jeudi"   },
    "2023-10-06": {"year": "impaire", "psalter": 2,    "day": "vendredi"},
    "2023-10-07": {"year": "impaire", "psalter": 2,    "day": "samedi"  },
    "2023-10-08": {"year": "a",       "psalter": 3,    "day": "dimanche"},
    "2023-10-09": {"year": "impaire", "psalter": 3,    "day": "lundi"   },
    "2023-10-10": {"year": "impaire", "psalter": 3,    "day": "mardi"   },
    "2023-10-11": {"year": "impaire", "psalter": 3,    "day": "mercredi"},
    "2023-10-12": {"year": "impaire", "psalter": 3,    "day": "jeudi"   },
    "2023-10-13": {"year": "impaire", "psalter": 3,    "day": "vendredi"},
    "2023-10-14": {"year": "impaire", "psalter": 3,    "day": "samedi"  },
    "2023-10-15": {"year": "a",       "psalter": 4,    "day": "dimanche"},
    "2023-10-16": {"year": "impaire", "psalter": 4,    "day": "lundi"   },
    "2023-10-17": {"year": "impaire", "psalter": 4,    "day": "mardi"   },
    "2023-10-18": {"year": "impaire", "psalter": None, "day": "Saint\u00a0Luc"},
    "2023-10-19": {"year": "impaire", "psalter": 4,    "day": "jeudi"   },
    "2023-10-20": {"year": "impaire", "psalter": 4,    "day": "vendredi"},
    "2023-10-21": {"year": "impaire", "psalter": 4,    "day": "samedi"  },
    "2023-10-22": {"year": "a",       "psalter": 1,    "day": "dimanche"},
    "2023-10-23": {"year": "impaire", "psalter": 1,    "day": "lundi"   },
    "2023-10-24": {"year": "impaire", "psalter": 1,    "day": "mardi"   },
    "2023-10-25": {"year": "impaire", "psalter": 1,    "day": "mercredi"},
    "2023-10-26": {"year": "impaire", "psalter": 1,    "day": "jeudi"   },
    "2023-10-27": {"year": "impaire", "psalter": 1,    "day": "vendredi"},
    "2023-10-28": {"year": "impaire", "psalter": None, "day": "samedi"  },
    "2023-10-29": {"year": "a",       "psalter": None, "day": "dimanche"},
    "2023-10-30": {"year": "impaire", "psalter": 2,    "day": "lundi"   },
    "2023-10-31": {"year": "impaire", "psalter": 2,    "day": "mardi"   },
    "2023-11-01": {"year": "a",       "psalter": None, "day": "Toussaint"},
    "2023-11-02": {"year": "impaire", "psalter": None, "day": "Fidèles\u00a0défunts"},
    "2023-11-03": {"year": "impaire", "psalter": 2,    "day": "vendredi"},
    "2023-11-04": {"year": "impaire", "psalter": 2,    "day": "samedi"  },
    "2023-11-05": {"year": "a",       "psalter": 3,    "day": "dimanche"},
    "2023-11-06": {"year": "impaire", "psalter": 3,    "day": "lundi"   },
    "2023-11-07": {"year": "impaire", "psalter": 3,    "day": "mardi"   },
    "2023-11-08": {"year": "impaire", "psalter": 3,    "day": "mercredi"},
    "2023-11-09": {"year": "impaire", "psalter": None, "day": "jeudi"   },
    "2023-11-10": {"year": "impaire", "psalter": 3,    "day": "vendredi"},
    "2023-11-11": {"year": "impaire", "psalter": 3,    "day": "samedi"  },
    "2023-11-12": {"year": "a",       "psalter": 4,    "day": "dimanche"},
    "2023-11-13": {"year": "impaire", "psalter": 4,    "day": "lundi"   },
    "2023-11-14": {"year": "impaire", "psalter": 4,    "day": "mardi"   },
    "2023-11-15": {"year": "impaire", "psalter": 4,    "day": "mercredi"},
    "2023-11-16": {"year": "impaire", "psalter": 4,    "day": "jeudi"   },
    "2023-11-17": {"year": "impaire", "psalter": 4,    "day": "vendredi"},
    "2023-11-18": {"year": "impaire", "psalter": 4,    "day": "samedi"  },
    "2023-11-19": {"year": "a",       "psalter": 1,    "day": "dimanche"},
    "2023-11-20": {"year": "impaire", "psalter": 1,    "day": "lundi"   },
    "2023-11-21": {"year": "impaire", "psalter": 1,    "day": "mardi"   },
    "2023-11-22": {"year": "impaire", "psalter": 1,    "day": "mercredi"},
    "2023-11-23": {"year": "impaire", "psalter": 1,    "day": "jeudi"   },
    "2023-11-24": {"year": "impaire", "psalter": 1,    "day": "vendredi"},
    "2023-11-25": {"year": "impaire", "psalter": 1,    "day": "samedi"  },
    "2023-11-26": {"year": "a",       "psalter": None, "day": "Christ-Roi"},
    "2023-11-27": {"year": "impaire", "psalter": 2,    "day": "lundi"   },
    "2023-11-28": {"year": "impaire", "psalter": 2,    "day": "mardi"   },
    "2023-11-29": {"year": "impaire", "psalter": 2,    "day": "mercredi"},
    "2023-11-30": {"year": "impaire", "psalter": None, "day": "jeudi"   },
    "2023-12-01": {"year": "impaire", "psalter": 2,    "day": "vendredi"},
    "2023-12-02": {"year": "impaire", "psalter": 2,    "day": "samedi"  },
    "2023-12-03": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2023-12-04": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2023-12-05": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2023-12-06": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2023-12-07": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2023-12-08": {"year": "b",       "psalter": None, "day": "Immaculée\u00a0Conception"},
    "2023-12-09": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2023-12-10": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2023-12-11": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2023-12-12": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2023-12-13": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2023-12-14": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2023-12-15": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2023-12-16": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2023-12-17": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2023-12-18": {"year": "paire",   "psalter": None, "day": "lundi"   }, # This should be 3
    "2023-12-19": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2023-12-20": {"year": "paire",   "psalter": None, "day": "mercredi"},
    "2023-12-21": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2023-12-22": {"year": "paire",   "psalter": None, "day": "vendredi"},
    "2023-12-23": {"year": "paire",   "psalter": None, "day": "samedi"  },
    "2023-12-24": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2023-12-25": {"year": "b",       "psalter": None, "day": "Noël"},
    "2023-12-26": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2023-12-27": {"year": "paire",   "psalter": None, "day": "Saint\u00a0Jean"},
    "2023-12-28": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2023-12-29": {"year": "b",       "psalter": None, "day": "vendredi"}, # This is wrong, but the upstream data is wrong
    "2023-12-30": {"year": "b",       "psalter": None, "day": "samedi"  }, # Same
    "2023-12-31": {"year": "b",       "psalter": None, "day": "dimanche"},
    "2024-01-01": {"year": "b",       "psalter": None, "day": "Sainte\u00a0Marie, Mère\u00a0de\u00a0Dieu"},
    "2024-01-02": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2024-01-03": {"year": "paire",   "psalter": None, "day": "mercredi"},
    "2024-01-04": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2024-01-05": {"year": "paire",   "psalter": None, "day": "vendredi"},
    "2024-01-06": {"year": "paire",   "psalter": None, "day": "samedi"  },
    "2024-01-07": {"year": "b",       "psalter": None, "day": "Épiphanie"},
    "2024-01-08": {"year": "b",       "psalter": None, "day": "lundi"   },
    "2024-01-09": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-01-10": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-01-11": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-01-12": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-01-13": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-01-14": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-01-15": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-01-16": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-01-17": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-01-18": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2024-01-19": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-01-20": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-01-21": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-01-22": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-01-23": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-01-24": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-01-25": {"year": "paire",   "psalter": None, "day": "jeudi"},
    "2024-01-26": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-01-27": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-01-28": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-01-29": {"year": "paire",   "psalter": 4,    "day": "lundi"   },
    "2024-01-30": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-01-31": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-02-01": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-02-02": {"year": "paire",   "psalter": None, "day": "Présentation au\u00a0Temple"},
    "2024-02-03": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-02-04": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-02-05": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-02-06": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-02-07": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-02-08": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-02-09": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-02-10": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-02-11": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-02-12": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-02-13": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-02-14": {"year": "paire",   "psalter": 4,    "day": "Cendres"},
    "2024-02-15": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-02-16": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-02-17": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-02-18": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-02-19": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-02-20": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-02-21": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-02-22": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2024-02-23": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-02-24": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-02-25": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-02-26": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-02-27": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-02-28": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-02-29": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2024-03-01": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-03-02": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-03-03": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-03-04": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-03-05": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-03-06": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-03-07": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-03-08": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-03-09": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-03-10": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-03-11": {"year": "paire",   "psalter": 4,    "day": "lundi"   },
    "2024-03-12": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-03-13": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-03-14": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-03-15": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-03-16": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-03-17": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-03-18": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-03-19": {"year": "b",       "psalter": None, "day": "Saint\u00a0Joseph"},
    "2024-03-20": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-03-21": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-03-22": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-03-23": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-03-24": {"year": "b",       "psalter": None, "day": "Rameaux"},
    "2024-03-25": {"year": "paire",   "psalter": None, "day": "lundi"   },
    "2024-03-26": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2024-03-27": {"year": "paire",   "psalter": None, "day": "mercredi"},
    "2024-03-28": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2024-03-29": {"year": "paire",   "psalter": None, "day": "vendredi"},
    "2024-03-30": {"year": "b",       "psalter": None, "day": "samedi"  },
    "2024-03-31": {"year": "b",       "psalter": None, "day": "Pâques"},
    "2024-04-01": {"year": "b",       "psalter": None, "day": "lundi"},
    "2024-04-02": {"year": "b",       "psalter": None, "day": "mardi"   },
    "2024-04-03": {"year": "b",       "psalter": None, "day": "mercredi"},
    "2024-04-04": {"year": "b",       "psalter": None, "day": "jeudi"   },
    "2024-04-05": {"year": "b",       "psalter": None, "day": "vendredi"},
    "2024-04-06": {"year": "b",       "psalter": None, "day": "samedi"  },
    "2024-04-07": {"year": "b",       "psalter": 2,    "day": "Miséricorde"},
    "2024-04-08": {"year": "b",       "psalter": None, "day": "Annonciation"},
    "2024-04-09": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-04-10": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-04-11": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2024-04-12": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-04-13": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-04-14": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-04-15": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-04-16": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-04-17": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-04-18": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-04-19": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-04-20": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-04-21": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-04-22": {"year": "paire",   "psalter": 4,    "day": "lundi"   },
    "2024-04-23": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-04-24": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-04-25": {"year": "paire",   "psalter": None, "day": "Saint\u00a0Marc"},
    "2024-04-26": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-04-27": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-04-28": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-04-29": {"year": "paire",   "psalter": None, "day": "lundi"   },
    "2024-04-30": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-05-01": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-05-02": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-05-03": {"year": "paire",   "psalter": None, "day": "vendredi"},
    "2024-05-04": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-05-05": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-05-06": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-05-07": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-05-08": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-05-09": {"year": "b",       "psalter": None, "day": "Ascension"},
    "2024-05-10": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-05-11": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-05-12": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-05-13": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-05-14": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2024-05-15": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-05-16": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-05-17": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-05-18": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-05-19": {"year": "b",       "psalter": None, "day": "Pentecôte"},
    "2024-05-20": {"year": "paire",   "psalter": None, "day": "lundi"   },
    "2024-05-21": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-05-22": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-05-23": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-05-24": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-05-25": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-05-26": {"year": "b",       "psalter": None, "day": "Sainte\u00a0Trinité"},
    "2024-05-27": {"year": "paire",   "psalter": 4,    "day": "lundi"   },
    "2024-05-28": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-05-29": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-05-30": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-05-31": {"year": "paire",   "psalter": None, "day": "Visitation"},
    "2024-06-01": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-06-02": {"year": "b",       "psalter": None, "day": "Saint\u00a0Sacrement"},
    "2024-06-03": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-06-04": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-06-05": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-06-06": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-06-07": {"year": "b",       "psalter": None, "day": "Sacré-Cœur"},
    "2024-06-08": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-06-09": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-06-10": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-06-11": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-06-12": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-06-13": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2024-06-14": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-06-15": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-06-16": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-06-17": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-06-18": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-06-19": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-06-20": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-06-21": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-06-22": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-06-23": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-06-24": {"year": "b",       "psalter": None, "day": "Saint\u00a0Jean\u00a0Baptiste"},
    "2024-06-25": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-06-26": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-06-27": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-06-28": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-06-29": {"year": "b",       "psalter": None, "day": "Saint\u00a0Pierre et Saint\u00a0Paul"},
    "2024-06-30": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-07-01": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-07-02": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-07-03": {"year": "paire",   "psalter": None, "day": "mercredi"},
    "2024-07-04": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-07-05": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-07-06": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-07-07": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-07-08": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-07-09": {"year": "paire",   "psalter": 2,    "day": "mardi"   },
    "2024-07-10": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-07-11": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2024-07-12": {"year": "paire",   "psalter": 2,    "day": "vendredi"},
    "2024-07-13": {"year": "paire",   "psalter": 2,    "day": "samedi"  },
    "2024-07-14": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-07-15": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-07-16": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-07-17": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-07-18": {"year": "paire",   "psalter": 3,    "day": "jeudi"   },
    "2024-07-19": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-07-20": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-07-21": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-07-22": {"year": "paire",   "psalter": None, "day": "lundi"   },
    "2024-07-23": {"year": "paire",   "psalter": None, "day": "mardi"   },
    "2024-07-24": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-07-25": {"year": "paire",   "psalter": None, "day": "jeudi"   },
    "2024-07-26": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-07-27": {"year": "paire",   "psalter": 4,    "day": "samedi"  },
    "2024-07-28": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-07-29": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-07-30": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-07-31": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-08-01": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-08-02": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-08-03": {"year": "paire",   "psalter": 1,    "day": "samedi"  },
    "2024-08-04": {"year": "b",       "psalter": 2,    "day": "dimanche"},
    "2024-08-05": {"year": "paire",   "psalter": 2,    "day": "lundi"   },
    "2024-08-06": {"year": "b",       "psalter": None, "day": "Transfiguration"},
    "2024-08-07": {"year": "paire",   "psalter": 2,    "day": "mercredi"},
    "2024-08-08": {"year": "paire",   "psalter": 2,    "day": "jeudi"   },
    "2024-08-09": {"year": "paire",   "psalter": None, "day": "vendredi"},
    "2024-08-10": {"year": "paire",   "psalter": None, "day": "samedi"  },
    "2024-08-11": {"year": "b",       "psalter": 3,    "day": "dimanche"},
    "2024-08-12": {"year": "paire",   "psalter": 3,    "day": "lundi"   },
    "2024-08-13": {"year": "paire",   "psalter": 3,    "day": "mardi"   },
    "2024-08-14": {"year": "paire",   "psalter": 3,    "day": "mercredi"},
    "2024-08-15": {"year": "b",       "psalter": None, "day": "Assomption"},
    "2024-08-16": {"year": "paire",   "psalter": 3,    "day": "vendredi"},
    "2024-08-17": {"year": "paire",   "psalter": 3,    "day": "samedi"  },
    "2024-08-18": {"year": "b",       "psalter": 4,    "day": "dimanche"},
    "2024-08-19": {"year": "paire",   "psalter": 4,    "day": "lundi"   },
    "2024-08-20": {"year": "paire",   "psalter": 4,    "day": "mardi"   },
    "2024-08-21": {"year": "paire",   "psalter": 4,    "day": "mercredi"},
    "2024-08-22": {"year": "paire",   "psalter": 4,    "day": "jeudi"   },
    "2024-08-23": {"year": "paire",   "psalter": 4,    "day": "vendredi"},
    "2024-08-24": {"year": "paire",   "psalter": None, "day": "samedi"  },
    "2024-08-25": {"year": "b",       "psalter": 1,    "day": "dimanche"},
    "2024-08-26": {"year": "paire",   "psalter": 1,    "day": "lundi"   },
    "2024-08-27": {"year": "paire",   "psalter": 1,    "day": "mardi"   },
    "2024-08-28": {"year": "paire",   "psalter": 1,    "day": "mercredi"},
    "2024-08-29": {"year": "paire",   "psalter": 1,    "day": "jeudi"   },
    "2024-08-30": {"year": "paire",   "psalter": 1,    "day": "vendredi"},
    "2024-08-31": {"year": "paire",   "psalter": 1,    "day": "samedi"},
}

EXPECTED_LITURGICAL_OPTIONS = {
    "2023-09-01": [
        ("vert", "Férie", "vendredi, 21ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-02": [
        ("vert", "Férie", "samedi, 21ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-03": [
        ("vert", "Férie", "dimanche, 22ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-04": [
        ("vert", "Férie", "lundi, 22ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-05": [
        ("vert", "Férie", "mardi, 22ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-06": [
        ("vert", "Férie", "mercredi, 22ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-07": [
        ("vert", "Férie", "jeudi, 22ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-08": [
        ("blanc", "Fête", "La Nativité de la Bienheureuse Vierge Marie"),
    ],
    "2023-09-09": [
        ("vert", "Férie", "samedi, 22ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Pierre Claver, prêtre"),
    ],
    "2023-09-10": [
        ("vert", "Férie", "23ème dimanche du Temps Ordinaire"),
    ],
    "2023-09-11": [
        ("vert", "Férie", "lundi, 23ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-12": [
        ("vert", "Férie", "mardi, 23ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Le Saint Nom de Marie"),
    ],
    "2023-09-13": [
        ("blanc", "Mémoire", "saint Jean Chrysostome, évêque, docteur de l'Église"),
    ],
    "2023-09-14": [
        ("rouge", "Fête du Seigneur", "La Croix Glorieuse"),
    ],
    "2023-09-15": [
        ("blanc", "Mémoire", "Bienheureuse Vierge Marie des Douleurs"),
    ],
    "2023-09-16": [
        ("rouge", "Mémoire", "saint Corneille, pape, et saint Cyprien, évêque, martyrs"),
    ],
    "2023-09-17": [
        ("vert", "Férie", "dimanche, 24ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-18": [
        ("vert", "Férie", "lundi, 24ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-19": [
        ("vert", "Férie", "mardi 24ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Bienheureuse Vierge Marie de La Salette"),
    ],
    "2023-09-20": [
        ("rouge", "Mémoire", "saint André Kim Tae-gon, prêtre, saint Paul Chong Ha-sang, et leurs compagnons, martyrs"),
    ],
    "2023-09-21": [
        ("rouge", "Fête", "Saint Matthieu, apôtre et évangéliste"),
    ],
    "2023-09-22": [
        ("vert", "Férie", "vendredi, 24ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-23": [
        ("blanc", "Mémoire", "saint Pio de Pietrelcina , prêtre"),
    ],
    "2023-09-24": [
        ("vert", "Férie", "25ème dimanche du Temps Ordinaire"),
    ],
    "2023-09-25": [
        ("blanc", "Férie", "lundi, 25ème Semaine du Temps Ordinaire"),
    ],
    "2023-09-26": [
        ("vert", "Férie", "mardi, 25ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Côme et saint Damien, martyrs"),
    ],
    "2023-09-27": [
        ("blanc", "Mémoire", "saint Vincent de Paul, prêtre"),
    ],
    "2023-09-28": [
        ("vert", "Férie", "jeudi, 25ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Venceslas, martyr"),
        ("rouge", "Mémoire facultative", "saint Laurent Ruiz et ses compagnons, martyrs"),
    ],
    "2023-09-29": [
        ("blanc", "Fête", "Saint Michel, Saint Gabriel et Saint Raphaël, Archanges"),
    ],
    "2023-09-30": [
        ("blanc", "Mémoire", "saint Jérôme, prêtre et docteur de l'Église"),
    ],
    "2023-10-01": [
        ("vert", "Férie", "dimanche, 26ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-02": [
        ("blanc", "Mémoire", "Ss Anges Gardiens"),
    ],
    "2023-10-03": [
        ("vert", "Férie", "mardi, 26ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-04": [
        ("blanc", "Mémoire", "saint François d'Assise"),
    ],
    "2023-10-05": [
        ("vert", "Férie", "jeudi, 26ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Faustine Kowalska, vierge"),
    ],
    "2023-10-06": [
        ("vert", "Férie", "vendredi, 26ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Bruno, prêtre"),
    ],
    "2023-10-07": [
        ("blanc", "Mémoire", "Notre-Dame du Rosaire"),
    ],
    "2023-10-08": [
        ("vert", "Férie", "27ème dimanche du Temps Ordinaire"),
    ],
    "2023-10-09": [
        ("vert", "Férie", "lundi, 27ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Denis, évêque, et ses compagnons, martyrs"),
        ("blanc", "Mémoire facultative", "saint Jean Léonardi, prêtre"),
    ],
    "2023-10-10": [
        ("vert", "Férie", "mardi, 27ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-11": [
        ("vert", "Férie", "mercredi, 27ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Jean XXIII, pape"),
    ],
    "2023-10-12": [
        ("vert", "Férie", "jeudi, 27ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-13": [
        ("vert", "Férie", "vendredi, 27ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-14": [
        ("vert", "Férie", "samedi, 27ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Callixte Ier, pape et martyr"),
    ],
    "2023-10-15": [
        ("vert", "Férie", "dimanche, 28ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-16": [
        ("vert", "Férie", "lundi, 28ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Edwige, religieuse\u00a0; sainte Marguerite-Marie Alacoque, vierge"),
    ],
    "2023-10-17": [
        ("rouge", "Mémoire", "saint Ignace d'Antioche, évêque et martyr"),
    ],
    "2023-10-18": [
        ("rouge", "Fête", "saint Luc, évangéliste"),
    ],
    "2023-10-19": [
        ("vert", "Férie", "jeudi, 28ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Jean de Brébeuf et saint Isaac Jogues, prêtres, et leurs compagnons, martyrs"),
        ("blanc", "Mémoire facultative", "saint Paul de la Croix, prêtre"),
    ],
    "2023-10-20": [
        ("vert", "Férie", "vendredi, 28ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-21": [
        ("vert", "Férie", "samedi, 28ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-22": [
        ("vert", "Férie", "29ème dimanche du Temps Ordinaire"),
    ],
    "2023-10-23": [
        ("vert", "Férie", "lundi, 29ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Jean de Capistran, prêtre"),
    ],
    "2023-10-24": [
        ("vert", "Férie", "mardi, 29ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Antoine-Marie Claret, évêque"),
    ],
    "2023-10-25": [
        ("vert", "Ou Dédicace des Églises dont on ne connaît pas la date de consécration\u00a0; voir\u00a0: propre de votre pays", "mercredi, 29ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-26": [
        ("vert", "Férie", "jeudi, 29ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-27": [
        ("vert", "Férie", "vendredi, 29ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-28": [
        ("rouge", "Fête", "Saint Simon et Saint Jude, apôtres"),
    ],
    "2023-10-29": [
        ("blanc", "Solennité", "DÉDICACE DES ÉGLISES consacrées dont on ne connaît pas la date de consécration"),
    ],
    "2023-10-30": [
        ("vert", "Férie", "lundi, 30ème Semaine du Temps Ordinaire"),
    ],
    "2023-10-31": [
        ("vert", "Férie", "mardi, 30ème Semaine du Temps Ordinaire"),
    ],
    "2023-11-01": [
        ("blanc", "Solennité", "Tous les Saints"),
    ],
    "2023-11-02": [
        ("violet", "Férie", "Commémoration de tous les fidèles défunts, lectures au choix dans le rituel des funérailles"),
    ],
    "2023-11-03": [
        ("vert", "Férie", "vendredi, 30ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Martin de Porrès, religieux"),
    ],
    "2023-11-04": [
        ("blanc", "Mémoire", "saint Charles Borromée, évêque"),
    ],
    "2023-11-05": [
        ("vert", "Férie", "31ème dimanche du Temps Ordinaire"),
    ],
    "2023-11-06": [
        ("vert", "Férie", "lundi, 31ème Semaine du Temps Ordinaire"),
    ],
    "2023-11-07": [
        ("vert", "Férie", "mardi, 31ème Semaine du Temps Ordinaire"),
    ],
    "2023-11-08": [
        ("vert", "Férie", "mercredi, 31ème Semaine du Temps Ordinaire"),
    ],
    "2023-11-09": [
        ("blanc", "Fête", "Dédicace de la Basilique du Latran"),
    ],
    "2023-11-10": [
        ("blanc", "Mémoire", "saint Léon le Grand, pape et docteur de l'Église"),
    ],
    "2023-11-11": [
        ("blanc", "Mémoire", "saint Martin de Tours, évêque"),
    ],
    "2023-11-12": [
        ("vert", "Férie", "dimanche, 32ème semaine du Temps Ordinaire"),
    ],
    "2023-11-13": [
        ("vert", "Férie", "lundi, 32ème semaine du Temps Ordinaire"),
    ],
    "2023-11-14": [
        ("vert", "Férie", "mardi, 32ème semaine du Temps Ordinaire"),
    ],
    "2023-11-15": [
        ("vert", "Férie", "mercredi, 32ème semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Albert le Grand, évêque et docteur de l'Église"),
    ],
    "2023-11-16": [
        ("vert", "Férie", "jeudi, 32ème semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Marguerite d'Ecosse\u00a0; sainte Gertrude, vierge"),
    ],
    "2023-11-17": [
        ("blanc", "Mémoire", "sainte Elisabeth de Hongrie"),
    ],
    "2023-11-18": [
        ("vert", "Férie", "samedi, 32ème semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Dédicace des basiliques de saint Pierre et de saint Paul, apôtres"),
    ],
    "2023-11-19": [
        ("vert", "Férie", "33ème dimanche du Temps Ordinaire"),
    ],
    "2023-11-20": [
        ("vert", "Férie", "lundi, 33ème semaine du Temps Ordinaire"),
    ],
    "2023-11-21": [
        ("blanc", "Mémoire", "Présentation de la Vierge Marie"),
    ],
    "2023-11-22": [
        ("rouge", "Mémoire", "sainte Cécile, vierge et martyre"),
    ],
    "2023-11-23": [
        ("vert", "Férie", "jeudi, 33ème semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Clément Ier, pape et martyr"),
        ("blanc", "Mémoire facultative", "saint Colomban, abbé"),
    ],
    "2023-11-24": [
        ("rouge", "Mémoire", "saint André Dung-Lac, prêtre, et ses compagnons, martyrs"),
    ],
    "2023-11-25": [
        ("vert", "Férie", "samedi, 33ème semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "sainte Catherine d'Alexandrie, vierge et martyre"),
    ],
    "2023-11-26": [
        ("blanc", "Solennité du Seigneur", "Notre Seigneur Jésus Christ Roi de l'Univers"),
    ],
    "2023-11-27": [
        ("vert", "Férie", "lundi, 34ème semaine du Temps Ordinaire"),
    ],
    "2023-11-28": [
        ("vert", "Férie", "mardi, 34ème semaine du Temps Ordinaire"),
    ],
    "2023-11-29": [
        ("vert", "Férie", "mercredi, 34ème semaine du Temps Ordinaire"),
    ],
    "2023-11-30": [
        ("rouge", "Fête", "saint André, Apôtre"),
    ],
    "2023-12-01": [
        ("vert", "Férie", "vendredi, 34ème semaine du Temps Ordinaire"),
    ],
    "2023-12-02": [
        ("vert", "Férie", "samedi, 34ème semaine du Temps Ordinaire"),
    ],
    "2023-12-03": [
        ("violet", "Férie de l’Avent", "dimanche, 1ère Semaine de l'Avent"),
    ],
    "2023-12-04": [
        ("violet", "Férie de l’Avent", "lundi, 1ère Semaine de l'Avent"),
        ("blanc", "Mémoire facultative", "saint Jean de Damas, prêtre et docteur de l'Église"),
    ],
    "2023-12-05": [
        ("violet", "Férie de l’Avent", "mardi, 1ère Semaine de l'Avent"),
    ],
    "2023-12-06": [
        ("violet", "Férie de l’Avent", "mercredi, 1ère Semaine de l'Avent"),
        ("blanc", "Mémoire facultative", "saint Nicolas, évêque"),
    ],
    "2023-12-07": [
        ("blanc", "Mémoire", "saint Ambroise, évêque, docteur de l'Église"),
    ],
    "2023-12-08": [
        ("blanc", "Solennité de la Vierge Marie", "Immaculée Conception de la Vierge Marie"),
    ],
    "2023-12-09": [
        ("violet", "Férie de l’Avent", "samedi, 1ère Semaine de l'Avent"),
    ],
    "2023-12-10": [
        ("violet", "Férie de l’Avent", "2ème Dimanche de l'Avent"),
    ],
    "2023-12-11": [
        ("violet", "Férie de l’Avent", "lundi, 2ème Semaine de l'Avent"),
        ("blanc", "Mémoire facultative", "saint Damase Ier, pape"),
    ],
    "2023-12-12": [
        ("violet", "Férie de l’Avent", "mardi, 2ème Semaine de l'Avent"),
        ("blanc", "Mémoire facultative", "Bienheureuse Vierge Marie de Guadaloupé"),
    ],
    "2023-12-13": [
        ("rouge", "Mémoire", "Ste. Lucie, vierge et martyre"),
    ],
    "2023-12-14": [
        ("blanc", "Mémoire", "saint Jean de la Croix, prêtre,docteur de l'Église"),
    ],
    "2023-12-15": [
        ("violet", "Férie de l’Avent", "vendredi, 2ème Semaine de l'Avent"),
    ],
    "2023-12-16": [
        ("violet", "Férie de l’Avent", "samedi, 2ème Semaine de l'Avent"),
    ],
    "2023-12-17": [
        ("rose", "Férie de l’Avent", "3ème Dimanche de l'Avent, de Gaudete"),
    ],
    "2023-12-18": [
        ("violet", "Férie de l’Avent", "18 décembre"),
    ],
    "2023-12-19": [
        ("violet", "Férie de l’Avent", "19 décembre"),
    ],
    "2023-12-20": [
        ("violet", "Férie de l’Avent", "20 décembre"),
    ],
    "2023-12-21": [
        ("violet", "Férie de l’Avent", "21 décembre"),
        ("violet", "Mémoire facultative", "saint Pierre Canisius, prêtre, docteur de l'Église"),
    ],
    "2023-12-22": [
        ("violet", "Férie de l’Avent", "22 décembre"),
    ],
    "2023-12-23": [
        ("violet", "Férie de l’Avent", "23 décembre"),
        ("violet", "Mémoire facultative", "saint Jean de Kenty, prêtre."),
    ],
    "2023-12-24": [
        ("violet", "Férie de l’Avent", "4ème Dimanche de l'Avent"),
    ],
    "2023-12-25": [
        ("blanc", "Solennité du Seigneur", "Nativité du Seigneur"),
    ],
    "2023-12-26": [
        ("rouge", "Fête", "Saint Etienne, premier martyr"),
    ],
    "2023-12-27": [
        ("blanc", "Fête", "Saint Jean, apôtre et évangéliste"),
    ],
    "2023-12-28": [
        ("rouge", "Fête", "Les Saints Innocents, martyrs"),
    ],
    "2023-12-29": [
        ("blanc", "Férie de Noël", "5ème jour dans l'octave de Noël"),
        ("rouge", "Mémoire facultative", "saint Thomas Becket, évêque, martyr"),
    ],
    "2023-12-30": [
        ("blanc", "Férie de Noël", "6ème jour dans l'octave de Noël"),
    ],
    "2023-12-31": [
        ("blanc", "Fête du Seigneur", "La Sainte Famille"),
    ],
    "2024-01-01": [
        ("blanc", "Solennité de la Vierge Marie", "Sainte Marie, Mère de Dieu"),
    ],
    #"2024-01-02": [
    #    ("blanc", "Mémoire", "saint Basile le Grand et saint Grégoire de Nazianze, évêques et docteurs de l'Église"),
    #],
    "2024-01-03": [
        ("blanc", "Férie de Noël", "3 janvier"),
        ("blanc", "Mémoire facultative", "sainte Geneviève, vierge"),
    ],
    "2024-01-04": [
        ("blanc", "Férie de Noël", "4 janvier"),
    ],
    "2024-01-05": [
        ("blanc", "Férie de Noël", "5 janvier"),
    ],
    "2024-01-06": [
        ("blanc", "Férie de Noël", "6 janvier"),
    ],
    "2024-01-07": [
        ("blanc", "Solennité du Seigneur", "L'Épiphanie du Seigneur"),
    ],
    "2024-01-08": [
        ("blanc", "Fête du Seigneur", "Le Baptême du Seigneur"),
    ],
    "2024-01-09": [
        ("vert", "Férie", "mardi, 1ère Semaine du Temps Ordinaire"),
    ],
    "2024-01-10": [
        ("vert", "Férie", "mercredi, 1ère Semaine du Temps Ordinaire"),
    ],
    "2024-01-11": [
        ("vert", "Férie", "jeudi, 1ère Semaine du Temps Ordinaire"),
    ],
    "2024-01-12": [
        ("vert", "Férie", "vendredi, 1ère Semaine du Temps Ordinaire"),
    ],
    "2024-01-13": [
        ("vert", "Férie", "samedi, 1ère Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Hilaire, évêque et docteur de l'Église"),
    ],
    "2024-01-14": [
        ("vert", "Férie", "2ème dimanche du Temps Ordinaire"),
    ],
    "2024-01-15": [
        ("vert", "Férie", "lundi 2ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Rémi, évêque"),
    ],
    "2024-01-16": [
        ("vert", "Férie", "mardi, 2ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-17": [
        ("blanc", "Mémoire", "saint Antoine, Abbé"),
    ],
    "2024-01-18": [
        ("vert", "Férie", "jeudi, 2ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-19": [
        ("vert", "Férie", "vendredi, 2ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-20": [
        ("vert", "Férie", "samedi, 2ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Fabien, pape et martyr\u00a0; Saint Sébastien, martyr"),
    ],
    "2024-01-21": [
        ("vert", "Férie", "3ème dimanche du Temps Ordinaire"),
    ],
    "2024-01-22": [
        ("vert", "Férie", "lundi, 3ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Vincent, diacre et martyr"),
    ],
    "2024-01-23": [
        ("vert", "Férie", "mardi, 3ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-24": [
        ("blanc", "Mémoire", "saint François de Sales, évêque et docteur de l'Église"),
    ],
    "2024-01-25": [
        ("blanc", "Fête", "Conversion de st Paul, Apôtre"),
    ],
    "2024-01-26": [
        ("blanc", "Mémoire", "saint Timothée et saint Tite, évêques"),
    ],
    "2024-01-27": [
        ("vert", "Férie", "samedi, 3ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Angèle Merici, vierge"),
    ],
    "2024-01-28": [
        ("vert", "Férie", "4ème dimanche du Temps Ordinaire"),
    ],
    "2024-01-29": [
        ("vert", "Férie", "lundi, 4ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-30": [
        ("vert", "Férie", "mardi, 4ème Semaine du Temps Ordinaire"),
    ],
    "2024-01-31": [
        ("blanc", "Mémoire", "saint Jean Bosco, prêtre"),
    ],
    "2024-02-01": [
        ("vert", "Férie", "jeudi, 4ème Semaine du Temps Ordinaire"),
    ],
    "2024-02-02": [
        ("blanc", "Fête du Seigneur", "Présentation du Seigneur au Temple"),
    ],
    "2024-02-03": [
        ("vert", "Férie", "samedi, 4ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Blaise, évêque et martyr"),
        ("blanc", "Mémoire facultative", "Saint Anschaire, évêque"),
    ],
    "2024-02-04": [
        ("vert", "Férie", "5ème dimanche du Temps Ordinaire"),
    ],
    "2024-02-05": [
        ("rouge", "Mémoire", "sainte Agathe, vierge et martyre"),
    ],
    "2024-02-06": [
        ("rouge", "Mémoire", "saint Paul Miki et ses compagnons, martyrs"),
    ],
    "2024-02-07": [
        ("vert", "Férie", "mercredi, 5ème Semaine du Temps Ordinaire"),
    ],
    "2024-02-08": [
        ("vert", "Férie", "jeudi, 5ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Jérôme Émilien"),
        ("blanc", "Mémoire facultative", "sainte Joséphine Bakhita, vierge"),
    ],
    "2024-02-09": [
        ("vert", "Férie", "vendredi, 5ème Semaine du Temps Ordinaire"),
    ],
    "2024-02-10": [
        ("blanc", "Mémoire", "sainte Scholastique, vierge"),
    ],
    "2024-02-11": [
        ("vert", "Férie", "6ème dimanche du Temps Ordinaire"),
    ],
    "2024-02-12": [
        ("vert", "Férie", "lundi, 6ème Semaine du Temps Ordinaire"),
    ],
    "2024-02-13": [
        ("vert", "Férie", "mardi, 6ème Semaine du Temps Ordinaire"),
    ],
    "2024-02-14": [
        ("violet", "Férie du Carême", "Mercredi des Cendres"),
    ],
    "2024-02-15": [
        ("violet", "Férie du Carême", "Jeudi après les cendres"),
    ],
    "2024-02-16": [
        ("violet", "Férie du Carême", "Vendredi après les cendres"),
    ],
    "2024-02-17": [
        ("violet", "Férie du Carême", "Samedi après les cendres"),
        ("violet", "Mémoire facultative", "Les sept saints fondateurs des Servîtes de Marie"),
    ],
    "2024-02-18": [
        ("violet", "Férie du Carême", "1er Dimanche de Carême"),
    ],
    "2024-02-19": [
        ("violet", "Férie du Carême", "lundi, 1ère Semaine de Carême"),
    ],
    "2024-02-20": [
        ("violet", "Férie du Carême", "mardi, 1ère Semaine de Carême"),
    ],
    "2024-02-21": [
        ("violet", "Férie du Carême", "mercredi, 1ère Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Pierre Damien, docteur de l'Église"),
    ],
    "2024-02-22": [
        ("blanc", "Fête", "La Chaire de Saint Pierre"),
    ],
    "2024-02-23": [
        ("violet", "Férie du Carême", "vendredi, 1ère Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Polycarpe, évêque et martyr"),
    ],
    "2024-02-24": [
        ("violet", "Férie du Carême", "samedi, 1ère Semaine de Carême"),
    ],
    "2024-02-25": [
        ("violet", "Férie du Carême", "2ème Dimanche de Carême"),
    ],
    "2024-02-26": [
        ("violet", "Férie du Carême", "lundi, 2ème Semaine de Carême"),
    ],
    "2024-02-27": [
        ("violet", "Férie du Carême", "mardi, 2ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Grégoire de Narek, abbé et docteur de l'Église"),
    ],
    "2024-02-28": [
        ("violet", "Férie du Carême", "mercredi, 2ème Semaine de Carême"),
    ],
    "2024-02-29": [
        ("violet", "Férie du Carême", "jeudi, 2ème Semaine de Carême"),
    ],
    "2024-03-01": [
        ("violet", "Férie du Carême", "vendredi, 2ème Semaine de Carême"),
    ],
    "2024-03-02": [
        ("violet", "Férie du Carême", "samedi, 2ème Semaine de Carême"),
    ],
    "2024-03-03": [
        ("violet", "Férie du Carême", "3ème Dimanche de Carême"),
    ],
    "2024-03-04": [
        ("violet", "Férie du Carême", "lundi, 3ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Casimir"),
    ],
    "2024-03-05": [
        ("violet", "Férie du Carême", "mardi, 3ème Semaine de Carême"),
    ],
    "2024-03-06": [
        ("violet", "Férie du Carême", "mercredi, 3ème Semaine de Carême"),
    ],
    "2024-03-07": [
        ("violet", "Férie du Carême", "jeudi, 3ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "sainte Perpétue et sainte Félicité, martyres"),
    ],
    "2024-03-08": [
        ("violet", "Férie du Carême", "vendredi, 3ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Jean de Dieu"),
    ],
    "2024-03-09": [
        ("violet", "Férie du Carême", "samedi, 3ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "sainte Françoise Romaine"),
    ],
    "2024-03-10": [
        ("rose", "Férie du Carême", "4ème Dimanche de Carême, de Lætare"),
    ],
    "2024-03-11": [
        ("violet", "Férie du Carême", "lundi, 4ème Semaine de Carême"),
    ],
    "2024-03-12": [
        ("violet", "Férie du Carême", "mardi, 4ème Semaine de Carême"),
    ],
    "2024-03-13": [
        ("violet", "Férie du Carême", "mercredi, 4ème Semaine de Carême"),
    ],
    "2024-03-14": [
        ("violet", "Férie du Carême", "jeudi, 4ème Semaine de Carême"),
    ],
    "2024-03-15": [
        ("violet", "Férie du Carême", "vendredi, 4ème Semaine de Carême"),
    ],
    "2024-03-16": [
        ("violet", "Férie du Carême", "samedi, 4ème Semaine de Carême"),
    ],
    "2024-03-17": [
        ("violet", "Férie du Carême", "5ème Dimanche de Carême"),
    ],
    "2024-03-18": [
        ("violet", "Férie du Carême", "lundi, 5ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Cyrille de Jérusalem, évêque et docteur de l'Église"),
    ],
    "2024-03-19": [
        ("blanc", "Solennité de la Vierge Marie", "Saint Joseph, époux de la Bienheureuse Vierge Marie"),
    ],
    "2024-03-20": [
        ("violet", "Férie du Carême", "mercredi, 5ème Semaine de Carême"),
    ],
    "2024-03-21": [
        ("violet", "Férie du Carême", "jeudi, 5ème Semaine de Carême"),
    ],
    "2024-03-22": [
        ("violet", "Férie du Carême", "vendredi, 5ème Semaine de Carême"),
    ],
    "2024-03-23": [
        ("violet", "Férie du Carême", "samedi, de la férie, 5ème Semaine de Carême"),
        ("violet", "Mémoire facultative", "saint Turibio de Mogrovejo, évêque"),
    ],
    "2024-03-24": [
        ("rouge", "Solennité", "Dimanche des Rameaux et de la Passion du Seigneur"),
    ],
    "2024-03-25": [
        ("violet", "Férie du Carême", "Lundi Saint"),
    ],
    "2024-03-26": [
        ("violet", "Férie du Carême", "Mardi Saint"),
    ],
    "2024-03-27": [
        ("violet", "Férie du Carême", "Mercredi Saint"),
    ],
    "2024-03-28": [
        ("blanc", "Triduum Pascal", "Jeudi Saint"),
    ],
    "2024-03-29": [
        ("rouge", "Triduum Pascal", "Vendredi Saint"),
    ],
    "2024-03-30": [
        ("violet", "Triduum Pascal", "Samedi Saint"),
    ],
    "2024-03-31": [
        ("blanc", "Solennité du Seigneur", "Résurrection du Seigneur"),
    ],
    "2024-04-01": [
        ("blanc", "Solennité du Seigneur", "Lundi dans l'Octave de Pâques"),
    ],
    "2024-04-02": [
        ("blanc", "Solennité du Seigneur", "Mardi  dans l'Octave de Pâques"),
    ],
    "2024-04-03": [
        ("blanc", "Solennité du Seigneur", "Mercredi dans l'Octave de Pâques"),
    ],
    "2024-04-04": [
        ("blanc", "Solennité du Seigneur", "Jeudi dans l'Octave de Pâques"),
    ],
    "2024-04-05": [
        ("blanc", "Solennité du Seigneur", "Vendredi dans l'Octave de Pâques"),
    ],
    "2024-04-06": [
        ("blanc", "Solennité du Seigneur", "Samedi dans l'Octave de Pâques"),
    ],
    "2024-04-07": [
        ("blanc", "Solennité du Seigneur", "2ème Dimanche de Pâques ou de la Divine Miséricorde"),
    ],
    "2024-04-08": [
        ("blanc", "Solennité du Seigneur", "Annonciation du Seigneur"),
    ],
    "2024-04-09": [
        ("blanc", "Férie du temps Pascal", "mardi, 2ème Semaine du Temps Pascal"),
    ],
    "2024-04-10": [
        ("blanc", "Férie du temps Pascal", "mercredi, 2ème Semaine du Temps Pascal"),
    ],
    "2024-04-11": [
        ("rouge", "Mémoire", "saint Stanislas, évêque"),
    ],
    "2024-04-12": [
        ("blanc", "Férie du temps Pascal", "vendredi, 2ème Semaine du Temps Pascal"),
    ],
    "2024-04-13": [
        ("blanc", "Férie du temps Pascal", "samedi, 2ème Semaine du Temps Pascal"),
        ("rouge", "Mémoire facultative", "saint Martin Ier, pape, martyr"),
    ],
    "2024-04-14": [
        ("blanc", "Férie du temps Pascal", "3ème Dimanche de Pâques"),
    ],
    "2024-04-15": [
        ("blanc", "Férie du temps Pascal", "lundi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-16": [
        ("blanc", "Férie du temps Pascal", "mardi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-17": [
        ("blanc", "Férie du temps Pascal", "mercredi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-18": [
        ("blanc", "Férie du temps Pascal", "jeudi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-19": [
        ("blanc", "Férie du temps Pascal", "vendredi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-20": [
        ("blanc", "Férie du temps Pascal", "samedi, 3ème Semaine du Temps Pascal"),
    ],
    "2024-04-21": [
        ("blanc", "Férie du temps Pascal", "4ème Dimanche de Pâques"),
    ],
    "2024-04-22": [
        ("blanc", "Férie du temps Pascal", "lundi, 4ème Semaine du Temps Pascal"),
    ],
    "2024-04-23": [
        ("blanc", "Férie du temps Pascal", "mardi, 4ème Semaine du Temps Pascal"),
        ("rouge", "Mémoire facultative", "saint Georges, martyr\u00a0; saint Adalbert, évêque et martyr"),
    ],
    "2024-04-24": [
        ("blanc", "Férie du temps Pascal", "mercredi, 4ème Semaine du Temps Pascal"),
        ("rouge", "Mémoire facultative", "saint Fidèle de Sigmaringen, prêtre et martyr"),
    ],
    "2024-04-25": [
        ("rouge", "Fête", "saint Marc, évangéliste"),
    ],
    "2024-04-26": [
        ("blanc", "Férie du temps Pascal", "vendredi, 4ème Semaine du Temps Pascal"),
    ],
    "2024-04-27": [
        ("blanc", "Férie du temps Pascal", "samedi, 4ème Semaine du Temps Pascal"),
    ],
    "2024-04-28": [
        ("blanc", "Férie du temps Pascal", "5ème Dimanche de Pâques"),
    ],
    "2024-04-29": [
        ("blanc", "Mémoire", "sainte Catherine de Sienne, vierge et docteur de l'Église"),
    ],
    "2024-04-30": [
        ("blanc", "Férie du temps Pascal", "mardi, 5ème Semaine du Temps Pascal"),
        ("blanc", "Mémoire facultative", "saint Pie V, pape"),
    ],
    "2024-05-01": [
        ("blanc", "Férie du temps Pascal", "mercredi, 5ème Semaine du Temps Pascal"),
        ("blanc", "Mémoire facultative", "saint Joseph, travailleur"),
    ],
    "2024-05-02": [
        ("blanc", "Mémoire", "saint Athanase, évêque et docteur de l'Église"),
    ],
    "2024-05-03": [
        ("rouge", "Fête", "saint Philippe et saint Jacques, Apôtres"),
    ],
    "2024-05-04": [
        ("blanc", "Férie du temps Pascal", "samedi, 5ème Semaine du Temps Pascal"),
    ],
    "2024-05-05": [
        ("blanc", "Férie du temps Pascal", "6ème Dimanche de Pâques"),
    ],
    "2024-05-06": [
        ("blanc", "Férie du temps Pascal", "lundi, 6ème Semaine du Temps Pascal"),
    ],
    "2024-05-07": [
        ("blanc", "Férie du temps Pascal", "mardi, 6ème Semaine du Temps Pascal"),
    ],
    "2024-05-08": [
        ("blanc", "Férie du temps Pascal", "mercredi, 6ème Semaine du Temps Pascal"),
    ],
    "2024-05-09": [
        ("blanc", "Solennité du Seigneur", "Ascension-Année B"),
    ],
    "2024-05-10": [
        ("blanc", "Férie du temps Pascal", "vendredi, 6ème Semaine du Temps Pascal"),
        ("blanc", "Mémoire facultative", "saint Jean de Avila, prêtre et docteur de l’Église"),
    ],
    "2024-05-11": [
        ("blanc", "Férie du temps Pascal", "samedi, 6ème Semaine du Temps Pascal"),
    ],
    "2024-05-12": [
        ("blanc", "Férie du temps Pascal", "7ème Dimanche de Pâques"),
    ],
    "2024-05-13": [
        ("blanc", "Férie du temps Pascal", "lundi, 7ème Semaine du Temps Pascal"),
        ("blanc", "Mémoire facultative", "Bienheureuse Vierge Marie de Fatima"),
    ],
    "2024-05-14": [
        ("rouge", "Fête", "saint Matthias, apôtre"),
    ],
    "2024-05-15": [
        ("blanc", "Férie du temps Pascal", "mercredi, 7ème Semaine du Temps Pascal"),
    ],
    "2024-05-16": [
        ("blanc", "Férie du temps Pascal", "jeudi, 7ème Semaine du Temps Pascal"),
    ],
    "2024-05-17": [
        ("blanc", "Férie du temps Pascal", "vendredi, 7ème Semaine du Temps Pascal"),
    ],
    "2024-05-18": [
        ("blanc", "Férie du temps Pascal", "samedi, 7ème Semaine du Temps Pascal"),
        ("rouge", "Mémoire facultative", "saint Jean Ier, pape et martyr"),
    ],
    "2024-05-19": [
        ("rouge", "Solennité du Seigneur", "Pentecôte"),
    ],
    "2024-05-20": [
        ("blanc", "Mémoire", "Bienheureuse Vierge Marie, Mère de l'Église"),
    ],
    "2024-05-21": [
        ("vert", "Férie", "mardi, 7ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Christophe Magallanès, prêtre, et ses compagnons, martyrs"),
    ],
    "2024-05-22": [
        ("vert", "Férie", "mercredi, 7ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Rita de Cascia, religieuse"),
    ],
    "2024-05-23": [
        ("vert", "Férie", "jeudi, 7ème Semaine du Temps Ordinaire"),
    ],
    "2024-05-24": [
        ("vert", "Férie", "vendredi, 7ème Semaine du Temps Ordinaire"),
    ],
    "2024-05-25": [
        ("vert", "Férie", "samedi, 7ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoires facultatives", "saint Bède le Vénérable, prêtre et docteur de l'Église\u00a0; saint Grégoire VII, pape\u00a0: sainte Marie-Madeleine de Pazzi, vierge"),
    ],
    "2024-05-26": [
        ("blanc", "Solennité du Seigneur", "Sainte Trinité"),
    ],
    "2024-05-27": [
        ("vert", "Férie", "lundi, 8ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Augustin de Cantorbéry, prêtre"),
    ],
    "2024-05-28": [
        ("vert", "Férie", "mardi, 8ème Semaine du Temps Ordinaire"),
    ],
    "2024-05-29": [
        ("vert", "Férie", "mercredi, 8ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Paul VI, pape"),
    ],
    "2024-05-30": [
        ("blanc", "Mémoire", "sainte Jeanne d’Arc, vierge, patronne secondaire de la Fran"),
    ],
    "2024-05-31": [
        ("blanc", "Fête de la Vierge Marie", "La Visitation de la Bienheureuse Vierge Marie"),
    ],
    "2024-06-01": [
        ("rouge", "Mémoire", "saint Justin, martyr"),
    ],
    "2024-06-02": [
        ("blanc", "Solennité du Seigneur", "Le Saint Sacrement"),
    ],
    "2024-06-03": [
        ("rouge", "Mémoire", "saint Charles Lwanga et ses compagnons, martyrs"),
    ],
    "2024-06-04": [
        ("vert", "Férie", "mardi 9ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Clotilde"),
    ],
    "2024-06-05": [
        ("rouge", "Mémoire", "saint Boniface, évêque et martyr"),
    ],
    "2024-06-06": [
        ("vert", "Férie", "jeudi, 9ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Norbert, évêque"),
    ],
    "2024-06-07": [
        ("blanc", "Solennité du Seigneur", "Sacré-Cœur de Jésus"),
    ],
    "2024-06-08": [
        ("blanc", "Mémoire", "Le Cœur immaculé de la bienheureuse Vierge Marie"),
    ],
    "2024-06-09": [
        ("vert", "Férie", "10ème dimanche du Temps Ordinaire"),
    ],
    "2024-06-10": [
        ("vert", "Férie", "lundi, 10ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-11": [
        ("rouge", "Mémoire", "saint Barnabé"),
    ],
    "2024-06-12": [
        ("vert", "Férie", "mercredi, 10ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-13": [
        ("blanc", "Mémoire", "saint Antoine de Padoue, prêtre et docteur de l'Église"),
    ],
    "2024-06-14": [
        ("vert", "Férie", "vendredi, 10ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-15": [
        ("vert", "Férie", "samedi, 10ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-16": [
        ("vert", "Férie", "11ème dimanche du Temps Ordinaire"),
    ],
    "2024-06-17": [
        ("vert", "Férie", "lundi, 11ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-18": [
        ("vert", "Férie", "mardi, 11ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-19": [
        ("vert", "Férie", "mercredi, 11ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Romuald"),
    ],
    "2024-06-20": [
        ("vert", "Férie", "jeudi, 11ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-21": [
        ("blanc", "Mémoire", "saint Louis de Gonzague"),
    ],
    "2024-06-22": [
        ("vert", "Férie", "samedi, 11ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Paulin de Nole, évêque"),
        ("rouge", "Mémoire facultative", "saint Jean Fisher, évêque et saint Thomas More, martyrs"),
    ],
    "2024-06-23": [
        ("vert", "Férie", "12ème dimanche du Temps Ordinaire"),
    ],
    "2024-06-24": [
        ("blanc", "Solennité", "Nativité de Saint Jean Baptiste"),
    ],
    "2024-06-25": [
        ("vert", "Férie", "mardi, 12ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-26": [
        ("vert", "Férie", "mercredi, 12ème Semaine du Temps Ordinaire"),
    ],
    "2024-06-27": [
        ("vert", "Férie", "jeudi, 12ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Cyrille d'Alexandrie, évêque et docteur de l'Église"),
    ],
    "2024-06-28": [
        ("rouge", "Mémoire", "saint Irénée, évêque et martyr"),
    ],
    "2024-06-29": [
        ("rouge", "Solennité", "Saint Pierre et Saint Paul"),
    ],
    "2024-06-30": [
        ("vert", "Férie", "13ème dimanche du Temps Ordinaire"),
    ],
    "2024-07-01": [
        ("vert", "Férie", "lundi, 13ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-02": [
        ("vert", "Férie", "mardi, 13ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-03": [
        ("rouge", "Fête", "Saint Thomas, apôtre"),
    ],
    "2024-07-04": [
        ("vert", "Férie", "jeudi, 13ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Elisabeth du Portugal"),
    ],
    "2024-07-05": [
        ("vert", "Férie", "vendredi, 13ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Antoine-Marie Zaccaria, prêtre"),
    ],
    "2024-07-06": [
        ("vert", "Férie", "samedi, 13ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "sainte Marie Goretti, vierge et martyre"),
    ],
    "2024-07-07": [
        ("vert", "Férie", "14ème dimanche du Temps Ordinaire"),
    ],
    "2024-07-08": [
        ("vert", "Férie", "lundi, 14ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-09": [
        ("vert", "Férie", "mardi, 14ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Augustin Zhao Rong, prêtre, et ses compagnons, martyrs"),
    ],
    "2024-07-10": [
        ("vert", "Férie", "mercredi, 14ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-11": [
        ("blanc", "Mémoire", "saint Benoît, abbé"),
    ],
    "2024-07-12": [
        ("vert", "Férie", "vendredi, 14ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-13": [
        ("vert", "Férie", "samedi, 14ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Henri"),
    ],
    "2024-07-14": [
        ("vert", "Férie", "15ème dimanche du Temps Ordinaire"),
    ],
    "2024-07-15": [
        ("blanc", "Mémoire", "saint Bonaventure, évêque et docteur de l'Église"),
    ],
    "2024-07-16": [
        ("vert", "Férie", "mardi, 15ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Bienheureuse Vierge Marie du Mont Carmel"),
    ],
    "2024-07-17": [
        ("vert", "Férie", "mercredi, 15ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-18": [
        ("vert", "Férie", "jeudi, 15ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-19": [
        ("vert", "Férie", "vendredi, 15ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-20": [
        ("vert", "Férie", "samedi, 15ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Apollinaire, évêque et martyr"),
    ],
    "2024-07-21": [
        ("vert", "Férie", "16ème dimanche du Temps Ordinaire"),
    ],
    "2024-07-22": [
        ("blanc", "Fête", "sainte Marie-Madeleine"),
    ],
    "2024-07-23": [
        ("blanc", "Mémoire facultative", "sainte Brigitte, religieuse"),
    ],
    "2024-07-24": [
        ("vert", "Férie", "mercredi, 16ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Charbel Maklouf, prêtre"),
    ],
    "2024-07-25": [
        ("rouge", "Fête", "Saint Jacques, apôtre"),
    ],
    "2024-07-26": [
        ("blanc", "Mémoire", "sainte Anne et saint Joachim, parents de la Bienheureuse Vierge Marie"),
    ],
    "2024-07-27": [
        ("vert", "Férie", "samedi, 16ème Semaine du Temps Ordinaire"),
    ],
    "2024-07-28": [
        ("vert", "Férie", "17ème dimanche du Temps Ordinaire , année B"),
    ],
    "2024-07-29": [
        ("blanc", "Mémoire", "sainte Marthe, Marie et saint Lazare"),
    ],
    "2024-07-30": [
        ("vert", "Férie", "mardi, 17ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Pierre Chrysologue, évêque et docteur de l'Église"),
    ],
    "2024-07-31": [
        ("blanc", "Mémoire", "saint Ignace de Loyola, prêtre"),
    ],
    "2024-08-01": [
        ("blanc", "Mémoire", "saint Alphonse de Liguori, évêque et docteur de l'Église"),
    ],
    "2024-08-02": [
        ("vert", "Férie", "vendredi, 17ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Eusèbe, évêque"),
        ("blanc", "Mémoire facultative", "saint Pierre-Julien Eymard, prêtre"),
    ],
    "2024-08-03": [
        ("vert", "Férie", "samedi, 17ème Semaine du Temps Ordinaire"),
    ],
    "2024-08-04": [
        ("vert", "Férie", "18ème dimanche du Temps Ordinaire"),
    ],
    "2024-08-05": [
        ("vert", "Férie", "lundi, 18ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "Dédicace de la Basilique Sainte-Marie Majeure"),
    ],
    "2024-08-06": [
        ("blanc", "Fête du Seigneur", "Transfiguration du Seigneur"),
    ],
    "2024-08-07": [
        ("vert", "Férie", "mercredi, 18ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Sixte II, pape, et ses compagnons, martyrs"),
        ("blanc", "Mémoire facultative", "saint Gaëtan, prêtre"),
    ],
    "2024-08-08": [
        ("blanc", "Mémoire", "saint Dominique, prêtre"),
    ],
    "2024-08-09": [
        ("rouge", "Fête", "sainte Thérèse-Bénédicte de la Croix, vierge et martyre"),
    ],
    "2024-08-10": [
        ("rouge", "Fête", "Saint Laurent, diacre et martyr"),
    ],
    "2024-08-11": [
        ("vert", "Férie", "19ème dimanche du Temps Ordinaire"),
    ],
    "2024-08-12": [
        ("vert", "Férie", "lundi, 19ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Jeanne-Françoise de Chantal, religieuse"),
    ],
    "2024-08-13": [
        ("vert", "Férie", "mardi, 19ème Semaine du Temps Ordinaire"),
        ("rouge", "Mémoire facultative", "saint Pontien, pape, et saint Hippolyte, prêtre, martyrs."),
    ],
    "2024-08-14": [
        ("rouge", "Mémoire", "saint Maximilien Kolbe, prêtre et martyr"),
    ],
    "2024-08-15": [
        ("blanc", "Solennité de la Vierge Marie", "Assomption de la Vierge Marie"),
    ],
    "2024-08-16": [
        ("vert", "Férie", "vendredi, 19ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Étienne de Hongrie"),
    ],
    "2024-08-17": [
        ("vert", "Férie", "samedi, 19ème Semaine du Temps Ordinaire"),
    ],
    "2024-08-18": [
        ("vert", "Férie", "20ème dimanche du Temps Ordinaire"),
    ],
    "2024-08-19": [
        ("vert", "Férie", "lundi, 20ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Jean Eudes, prêtre"),
    ],
    "2024-08-20": [
        ("blanc", "Mémoire", "saint Bernard, abbé et docteur de l'Église"),
    ],
    "2024-08-21": [
        ("blanc", "Mémoire", "saint Pie X, pape"),
    ],
    "2024-08-22": [
        ("blanc", "Mémoire", "Bienheureuse Vierge Marie Reine"),
    ],
    "2024-08-23": [
        ("vert", "Férie", "vendredi, 20ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "sainte Rose de Lima, vierge"),
    ],
    "2024-08-24": [
        ("rouge", "Fête", "Saint Barthélémy, apôtre"),
    ],
    "2024-08-25": [
        ("vert", "Férie", "21ème dimanche du Temps Ordinaire"),
    ],
    "2024-08-26": [
        ("vert", "Férie", "lundi 21ème Semaine du Temps Ordinaire"),
        ("blanc", "Mémoire facultative", "saint Césaire, évêque d’Arles"),
    ],
    "2024-08-27": [
        ("blanc", "Mémoire", "sainte Monique"),
    ],
    "2024-08-28": [
        ("blanc", "Mémoire", "saint Augustin, évêque et docteur de l'Église"),
    ],
    "2024-08-29": [
        ("rouge", "Mémoire", "Martyre de saint Jean Baptiste"),
    ],
    "2024-08-30": [
        ("vert", "Férie", "vendredi, 21ème Semaine du Temps Ordinaire"),
    ],
    "2024-08-31": [
        ("vert", "Férie", "samedi, 21ème Semaine du Temps Ordinaire"),
    ]
}


def test_informations_day():
    from lib.postprocessor import postprocess_informations

    # Load inputs
    input: dict[str, dict] = {}
    for date in EXPECTED_DAY.keys():
        with open(os.path.join(FIXTURES_BASE_PATH, f'{date}.json')) as f:
            input[date] = json.loads(f.read())

    # Validate outputs
    for date, expected in EXPECTED_DAY.items():
        result = postprocess_informations(input[date]['informations'].copy())
        assert result['liturgical_day'] == expected['day'], f"Unexpected day for {date}\n{result}"
        assert result['liturgical_year'] == expected['year'], f"Unexpected year for {date}\n{result}"
        assert result['psalter_week'] == expected['psalter'], f"Unexpected psalter week for {date}\n{result}"

def test_informations_liturgical_options():
    from lib.postprocessor import postprocess_informations

    # Load inputs
    input: dict[str, dict] = {}
    for date in EXPECTED_LITURGICAL_OPTIONS.keys():
        with open(os.path.join(FIXTURES_BASE_PATH, f'{date}.json')) as f:
            input[date] = json.loads(f.read())

    # Validate outputs
    for date, expected in EXPECTED_LITURGICAL_OPTIONS.items():
        result = postprocess_informations(input[date]['informations'].copy())
        options = result['liturgy_options']

        assert len(expected) == len(options), f"Unexpected number of options for {date}\n{result}"

        for i in range(len(expected)):
            assert options[i]['liturgical_color'] == expected[i][0], f"Unexpected color for {date}, option {i+1}\n{result}"
            assert options[i]['liturgical_degree'] == expected[i][1], f"Unexpected degree for {date}, option {i+1}\n{result}"
            assert options[i]['liturgical_name'] == expected[i][2], f"Unexpected name for {date}, option {i+1}\n{result}"
