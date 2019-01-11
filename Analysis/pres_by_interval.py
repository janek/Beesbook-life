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
sys.path.append(os.getcwd()+'/Python-modules/') #For bee_helpers, file_helpers and cache

from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids, get_alive_bees_for_day
import bb_utils
import random
# %%



day = datetime.date(2016,8,9)

# Currently, when loading a Presence cache, rename and drop need to be executed to keep the dataframe tidy.
# This should be alleviated by improving saving and/or doing the cleanup in the Cache class
presence = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099', type=CacheType.presence, format=CacheFormat.csv)
presence.index.rename('bee_id', inplace = True)
presence.drop(columns=['Unnamed: 0', 'id'], inplace = True)
presence.head()


# Load up known foragers for this day so we can see how their presence looked like
# Note: for most days there will be 0 foragers
foragers = c.load('foragers_from_groups')
foragers['date'] = foragers['date'].dt.date
foragers_for_day = foragers[foragers['date'] == day].index


presence['was_foraging'] = False
presence['was_foraging'][foragers_for_day] = True # TODO:

foragers_for_day

# Get alive bees for the chosen day and filter other (dead) bees out of the presence table
bees_alive_for_day = get_alive_bees_for_day(day)['bee_id'].values
presence = presence.loc[bees_alive_for_day]
presence.shape # 1064 alivee bees x 2880 30sec intervals



#%%
# For a random bee, a plot of time vs presence score (i.e. for all intervals, how many detections per interval she has)
# ids for good examples of anomalous detection: [607, 894, 912, 1003] (on 2016-08-09)
bee_id = random.randint(0,presence.shape[0])
plt.figure(figsize=(33,7))
plt.scatter(np.arange(0,presence.shape[1]), presence.iloc[bee_id], s=0.5)
plt.title("Bee " + str(bee_id))



#%%
# See the same plot for known foragers
bee_id = random.choice(foragers_for_day)
plt.figure(figsize=(33,7))
plt.scatter(np.arange(0,presence.shape[1]), presence.loc[bee_id], s=0.5)

print(bee_id)




#%%
df = presence.drop(columns=['was_foraging'])
plt.figure(figsize=(33,7))
df.iloc[bee_id].hist(bins=100)





#%%
# ---- General info -----
df = presence.drop(columns=['was_foraging'])
# Distribution of values of presence over all bees over all 2880 intervals of a single day
s = pd.Series()
for row in df.index:
    s = s.append(df.loc[row])

plt.figure(figsize=(32,7)); s.hist(bins=100)


# Distribution of sums of presence over entire day
plt.figure(figsize=(32,7)); df.sum(axis=1).hist(bins=100)
