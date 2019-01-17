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
# %%


df = c.load('alive_bees_2016')



datetime_start = datetime.datetime(2016,8,9)
num_hours = 24
num_intervals_per_hour = 120
bee_ids = get_alive_bees_for_day(datetime_start).bee_id.tolist()


# Currently, when loading a Presence cache, rename and drop need to be executed to keep the dataframe tidy.
# This should be alleviated by improving saving and/or doing the cleanup in the Cache class

#TODO: broken because of the load/indexing issue, fix in a) detections_to_presence b) cache load
presence = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheFormat.csv)


# Load up known foragers for this day so we can see how their presence looked like
# Note: for most days there will be 0 foragers
foragers = c.load('foragers_from_groups')
foragers['date'] = foragers['date'].dt.date
foragers_for_day = foragers[foragers['date'] == datetime_start].index

presence['was_foraging'] = False
presence['was_foraging'][foragers_for_day] = True

# Get alive bees for the chosen day and filter other (dead) bees out of the presence table
bees_alive_for_day = get_alive_bees_for_day(datetime_start)['bee_id'].values
#presence = presence.loc[bees_alive_for_day] # what was the intention behind this line?
presence.index = bees_alive_for_day
presence.shape # 1064 alivee bees x 2880 30sec intervals

presence.head()
#%%
# For a random bee, a plot of time vs presence score (i.e. for all intervals, how many detections per interval she has)
# ids for good examples of anomalous detection: [2, 607, 894, 912, 926, 933, 943, 994, 1003, 1016] (on 2016-08-09)

# bee_id = random.randint(0,presence.shape[0])
# problematic_bees_old = [2, 607, 894, 912, 926, 933, 943, 994, 1003, 1016] # collected before bugfixes in presence


bee_id = random.choice(bees_alive_for_day)
plt.figure(figsize=(33,7))
axes = plt.gca()
axes.set_ylim([-5,370])
plt.scatter(np.arange(0,presence.shape[1]), presence.loc[bee_id], s=0.5)
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



# TIP: focus on pushing forward, not the anomaly #medianfilter
# Ben and David are looking up the cam1 video, wait for the result


# TODO: get all days, allcam and maybe cam1
# DONE: presence to det should warn you if there are detection files missing for the day you're trying to convert
# TODO: we should always cache detections with a super low confidence threshold and save the confidence in DETECTIONS cache, then do filtering at the presence conversion level
# TODO: when is stuff removed?

# dist: x is time, for every interval, the mean of all presence scores for all bees - this is part of the anomaly investigation, don't do it for now
# dist of gap length
# dist of pres durations


# 2d histogram: y is time, then gap lenght

#%%
# ---- Aggregate info about the entire day for all bees ----
df = presence.drop(columns=['was_foraging'])
# Distribution of values of presence over all bees over all 2880 intervals of a single day
plt.figure(figsize=(24,7))
axes.set_ylim([0,70])
plt.plot(np.arange(0,presence.shape[1]), presence.mean())



#%%
# Distribution of sums of presence over entire day
plt.figure(figsize=(32,7)); df.sum(axis=1).hist(bins=100)
