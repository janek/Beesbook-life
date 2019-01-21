#%%
import datetime
from datetime import timedelta
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/')
import pandas as pd
import numpy as np
import tqdm
from bee_helpers import get_alive_bees_for_day, get_all_bee_ids
from file_helpers import cache_detections_from_database, detections_to_presence
from bee_cache import CacheType, CacheFormat, Cache; c = Cache()
import matplotlib.pyplot as plt
import random
#%%

# Goal: get to a binary function form. First method: median filter.



# 1. Load up a presence file
df = c.load('PRESENCE-counts-2016-07-20_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheFormat.csv)
df.index = df['Unnamed: 0']
df.index.name = 'bee_id'
presence = df.drop(columns=['Unnamed: 0'])
day = datetime.datetime(2016,7,20)
bees_alive_for_day = get_alive_bees_for_day(day)['bee_id'].values




# 2. Recreate the median presence plot
#%%
# For a random bee, a plot of time vs presence score (i.e. for all intervals, how many detections per interval she has)
# ids for good examples of anomalous detection: [2, 607, 894, 912, 926, 933, 943, 994, 1003, 1016] (on 2016-08-09)

# bee_id = random.randint(0,presence.shape[0])
# problematic_bees_old = [2, 607, 894, 912, 926, 933, 943, 994, 1003, 1016] # collected before bugfixes in presence


bee_id = random.choice(bees_alive_for_day)
axes = plt.gca()
axes.set_ylim([-5,370])
bee_presence = presence.loc[bee_id]



#%%
bee_presence = presence.loc[bee_id]
plt.figure(figsize=(33,7))
plt.scatter(np.arange(0,presence.shape[1]), bee_presence, s=0.5)
plt.title("Bee " + str(bee_id))





































# Distribution of medians of presence over all bees over all 2880 intervals of a single day
plt.figure(figsize=(24,7))
axes = plt.gca()
axes.set_ylim([0,70])
plt.plot(np.arange(0,presence.shape[1]), presence.median())
