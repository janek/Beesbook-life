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
sys.path.append('/home/mi/rrszynka/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import get_alive_bees_for_day
import bb_utils
import random
from skimage.morphology import rectangle, closing
from tqdm import tqdm
import pickle
from bb_behavior import db as bbdb
import bb_utils; meta = bb_utils.meta.BeeMetaInfo()

# Get all days that we have cached (confidence 0.99) and binarize them
#%%
detection_confidence_requirement = 0.99
presences = c.load_multiple_day_caches(detection_confidence_requirement=0.99)
#%%
presences_bin = []
for (date, presence) in tqdm(presences[:10]):
    presence_bin = binarize_presence(presence)
    presences_bin.append((date, presence_bin))

# %%


# for ((date, presence),(date, presence_bin)) in zip(presences[:1], presences_bin[:1]):



#%%

gaps = []
for bee, bin_row in presence_bin.iterrows():
    row = presence.loc[bee]
    diff = np.diff(bin_row)
    exits = np.where(diff == -1)[0]
    entries = np.where(diff == 1)[0]

    if len(exits) == 0 or len(entries) == 0:
        continue

    # if first entry is before firs exit, start with second entry
    if entries[0] < exits[0]:
        entries = entries[1:]
        if len(entries) == 0:
            continue

    for exit, entry in zip(exits, entries):
        duration = (entry - exit)
        gaps.append((bee, exit, entry, duration))

#%%

    # TODO: make age, age group (from existing code)
    # TODO: put interval+date -> timestamp into a helper file
    # TODO: get locations using David's notebook
    # TODO: get frame and cam_id from david's function, measure time for small data, try optimizing

len(gaps)

npdate = np.datetime64(date)

gaps = pd.DataFrame(gaps)
gaps.columns = ['bee', 'exit', 'entry', 'duration']
gaps.exit = gaps.exit.apply(interval_to_timepoint_for_current_date)
gaps.entry = gaps.entry.apply(interval_to_timepoint_for_current_date)
gaps.duration = gaps.duration.apply(lambda intervals: pd.Timedelta(minutes=intervals / 2))
gaps['age'] = gaps.apply(row_to_age, axis=1)
gaps = gaps.dropna() #TODO: some ages are nan, which and why? (or just discard)
gaps['age_group'] = gaps.age.apply(lambda age: int(age) // 5) # Why does this throw warning?


# xd = tqdm(gaps[:1000].exit.apply(get_frame_id_for_timestamp_for_current_bee))
# ^ 1. runs slow, see if that can be helped
#   2. modify to also get cam_id from the same function
#   3. careful about which bee_id is being used! current ver might be wrong



gaps




#%%

binarized_presence = presences_bin[0]

# binarized presence -> exits, entries or both
(date, presence) = binarized_presence
npdate = np.datetime64(date)
for i, row in presence.iterrows():
    # For each bee, make a list of exits
    diff = np.diff(row)
    if mode == 'both':
        timepoints = np.where(np.abs(diff) == 1)[0]
    elif mode == 'exits':
        timepoints = np.where(diff == -1)[0]
    elif mode == 'entries':
        timepoints = np.where(diff == 1)[0]

    timepoint_timestamps = [npdate + np.timedelta64(int(timepoint)*30, 's') for timepoint in timepoints]
    existing_timestamps = dict.get(row.name, [])
    dict[row.name] = existing_timestamps + timepoint_timestamps







#________________________________________________________________________________________________________________________________________________
# FUNCTIONS (6)
#________________________________________________________________________________________________________________________________________________
#%%
def binarize_presence(presence_for_day_df):
    # TODO: running this on an already-binarized series will return all zeros,
    # (and that's not what we want) - changing the threshold solves it, but try sth else

    ys = presence_for_day_df.copy()
    index = ys.index
    if ys[ys>1].sum().sum() == 0:
        #Consider this already binarized, make no changes
        return ys

    ys[ys>90] = 90
    ys[ys>45] = 90
    ys[ys<=45] = 0 #TODO: consult: what should the threshold be
    ys[ys==90] = 1
    ys = closing(ys, rectangle(1,15))
    ys = pd.DataFrame(ys, index=index)
    ys.index.name = 'bee_id'
    return ys

#%%
def plot_presence(a):
    plt.figure(figsize=(26,7))
    plt.title("Presence")
    axes = plt.gca()
    plt.scatter(np.arange(0,len(a)), a, s=3)

import bb_utils

#%%
def get_frame_id_for_timestamp_for_current_bee(dt):
    bee_id = int(bee)
    get_frame_id_for_bee_id_and_timestamp(bee_id, dt)


#%%
#TODO: analyze how this works
def get_frame_id_for_bee_id_and_timestamp(bee_id, dt):
    for cam_id in range(4):
        # If theere are no frames for this cam and time, move on to the next cam
        frames = bbdb.get_frames(cam_id, dt.timestamp(), dt.timestamp() + 5)
        if len(frames) == 0:
            continue

        # If there are frames, get detections and return
        detections = bbdb.get_bee_detections(bee_id, frames=frames)
        for d in detections:
            if d is not None:
                return (d[1])

#%%
def interval_to_timepoint_for_current_date(interval_number):
    # Date must already be np.datetime64, so as not to convert here (executed for every row)
    return npdate + np.timedelta64(int(interval_number)*30, 's')

#%%
def row_to_age(row):
    bb_id = bb_utils.ids.BeesbookID.from_dec_9(row.bee)
    age = meta.get_age(bb_id, row.exit).days
    return age






#________________________________________________________________________________________________________________________________________________
# ARCHIVE (6)
#________________________________________________________________________________________________________________________________________________
#%%
# For pregame/testing, pick one instead of looping over all
# Choose day
date, presence = presences[5]
date, presence_bin = presences_bin[5]

# Choose bee
row = presence.iloc[5]
bin_row = presence_bin.iloc[5]

bee =  presence.index[5]
#%%
# plot_presence(row)
# plot_presence(bin_row)
#%%


diff = np.diff(bin_row)
exits = np.where(diff == -1)[0]
entries = np.where(diff == 1)[0]

#%%

col = []
for exit, entry in zip(exits, entries):
    duration = (entry - exit)
    col.append((bee, exit, entry, duration))



#Outside the loop, once per day (single presence df)
cc = pd.DataFrame(col)
cc.columns = ['bee', 'exit', 'entry', 'duration']

npdate = np.datetime64(date)

cc.exit = cc.exit.apply(interval_to_timepoint_for_current_date)
cc.entry = cc.entry.apply(interval_to_timepoint_for_current_date)
cc.duration = cc.duration.apply(lambda intervals: pd.Timedelta(minutes=intervals / 2))
bee
cc['exit_frame'] = cc.exit.apply(get_frame_id_for_timestamp_for_current_bee)


cc.exit_frame



cc.exit[0]
