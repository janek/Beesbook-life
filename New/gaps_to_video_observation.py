# %%
import sys
sys.path.append('/home/mi/rrszynka/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers and file_helpers
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids
from file_helpers import delete_detection_caches_for_date, detections_to_presence, create_presence_cache_filename, create_presence_cache_filename, cache_location_prefix, cache_detections_from_database, cache_death_dates, last_days_caches
from datetime import timedelta, datetime
from pathlib import Path
from bee_cache import Cache, CacheType, CacheFormat; c=Cache()
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
%matplotlib inline
# %%



exits = c.load('50_random_exits')
# %%
exits.to_csv('/home/mi/rrszynka/mnt/janek/caches/Other/50_random_exits.csv')


#%%

# e.g. name: bee_id_random_exit
