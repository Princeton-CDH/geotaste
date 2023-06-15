from typing import *
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from functools import cached_property, lru_cache
# cache = lru_cache(maxsize=None)
# from diskcache import Cache
from joblib import Memory


#########
# SETUP #
#########

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
PATH_DATA = os.path.join(PATH_REPO,'data')
PATH_CACHE = os.path.join(PATH_DATA,'cache')
# cache = Cache(PATH_CACHE)
cache = Memory(PATH_CACHE, verbose=1).cache

# Paths
PATHS=dict(
    here=PATH_HERE,
    data=PATH_DATA,
    members = os.path.join(PATH_DATA,'1.3-beta','members.csv'),
    books = os.path.join(PATH_DATA,'1.3-beta','books.csv'),
    events = os.path.join(PATH_DATA,'1.3-beta','events.csv'),
    dwellings = os.path.join(PATH_DATA,'1.3-beta','dwellings.csv'),
    creators = os.path.join(PATH_DATA,'1.2','creators.csv'),
)

### other vars
LATLON_SCO = (48.85107555543428, 2.3385039932538567)
DISPREFERRED_ADDRESSES = {
    '11 rue Scribe': 'American Express',
    'Berkeley Street': 'Thomas Cook', # @CHECK
    '': 'Empty street address'
}
DWELLING_ID_SEP='; '
####


from .utils import *
from .datasets import *
# from .arronds import *
# from .authors import *
# from .books import *
# from .choices import *
# from .combined import *
# from .dwellings import *
# from .events import *
# from .maps import *
# from .people import *