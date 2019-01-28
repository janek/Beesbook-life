#%%
import os
if "rrszynka" not in os.getcwd():
   raise Exception("Working locally - is this desired?")
import pandas as pd
import numpy as np
import seaborn as sns; sns.set()
import datetime
import matplotlib.pyplot as plt
import sys
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache

from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids, get_alive_bees_for_day
import bb_utils
import random
import plotly
import cufflinks
plotly.tools.set_credentials_file(username='DemoAccount', api_key='lr1c37zw81')
# %%


datetime_start = datetime.datetime(2016,7,22)
num_hours = 24
num_intervals_per_hour = 120
bee_ids = get_alive_bees_for_day(datetime_start).bee_id.tolist()

#%%

# Get alive bees for the chosen day and filter other (dead) bees out of the presence table
bees_alive_for_day = get_alive_bees_for_day(datetime_start)['bee_id'].values
presence = c.load('PRESENCE-counts-2016-07-22_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheFormat.csv)
presence.index = bees_alive_for_day
presence.shape # 1064 alivee bees x 2880 30sec intervals



presence = c.load('PRESENCE-counts-2016-07-20_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheFormat.csv)
