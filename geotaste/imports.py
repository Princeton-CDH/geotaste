from typing import *
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
from functools import cached_property, lru_cache
cache = lru_cache(maxsize=None)


#########
# SETUP #
#########

PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_REPO = os.path.dirname(PATH_HERE)
# PATH_DATA = os.path.join(PATH_REPO,'data')
PATH_DATA = os.path.expanduser('~/geotaste_data')

# Urls
URLS=dict(
    books='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/books.csv',
    members='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/members.csv',
    events='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/events.csv',
    dwellings='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.3-beta/dwellings.csv',
    creators='https://raw.githubusercontent.com/Princeton-CDH/geotaste/main/data/1.2/creators.csv',
    geojson_arrond='https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/arrondissements/exports/geojson?lang=en&timezone=Europe%2FParis'
)

# Paths
PATHS=dict(
    here=PATH_HERE,
    data=PATH_DATA,
    
    members = os.path.join(PATH_DATA,'members.csv'),
    books = os.path.join(PATH_DATA,'books.csv'),
    events = os.path.join(PATH_DATA,'events.csv'),
    dwellings = os.path.join(PATH_DATA,'dwellings.csv'),
    creators = os.path.join(PATH_DATA,'creators.csv'),
    
    # members = os.path.join(PATH_DATA,'1.3-beta','members.csv'),
    # books = os.path.join(PATH_DATA,'1.3-beta','books.csv'),
    # events = os.path.join(PATH_DATA,'1.3-beta','events.csv'),
    # dwellings = os.path.join(PATH_DATA,'1.3-beta','dwellings.csv'),
    # creators = os.path.join(PATH_DATA,'1.2','creators.csv'),
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


from .datasets import *