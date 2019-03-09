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
from bee_helpers import get_alive_bees_for_day
import bb_utils
import random
from skimage.morphology import rectangle, closing
from tqdm import tqdm
import pickle

# Get all days that we have cached (confidence 0.99) and binarize them
#%%
presences = c.load_all_presence_caches()
#%%
presences_bin = []
for (date, presence) in tqdm(presences):
    presence_bin = binarize_presence(presence)
    presences_bin.append((date, presence_bin))


#%%
bee_exits = {}
for presence_bin in tqdm(presences_bin):
    put_entries_exits_to_dict(presence_bin, bee_exits, mode='exits')

#%%



d = c.load('DETECTIONS-2016-08-22_14:00:00', format=CacheFormat.csv, type=CacheType.detections)

d.head()
b = d[d.bee_id == 885]

b[3670:].head(20)




# 14:08, 14:17, 14:54:30


vvnbee_exits_dict[885]


c.load('real_forager_lives')


plot_presence(pp.loc[251])



os.getcwd()


# Function sketch: binarized presence -> exits, entries or both
#%%
def put_entries_exits_to_dict(binarized_presence, dict, mode='both'):
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
    return
#%%
print()
#%%











#FUNCTIONS - BINARIZATION
#TODO: merge into one (currently they are separate for single bey and all bees )
#DONE: tested if outputs are the same whether ([] -> bin -> select_row) or ([] -> select_row -> bin)
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
def binarize_presence_row(presence_for_day_series):
    # TODO: running this on an already-binarized series will return all zeros,
    # (and that's not what we want) - changing the threshold solves it, but try sth else
    ys = presence_for_day_series.copy()
    if ys[ys>1].sum() == 0:
        #Consider this already binarized, make no changes
        return ys

    ys[ys>90] = 90
    ys[ys>45] = 90
    ys[ys<=45] = 0 #TODO: consult: what should the threshold be
    ys[ys==90] = 1
    ys = np.reshape(np.array(ys, dtype=np.int32),[1,ys.shape[0]])
    ys = closing(ys, rectangle(1,15))
    ys = ys.flatten()
    return ys


# PLOTTING
#%%
def plot_presence(a):
    plt.figure(figsize=(26,7))
    plt.title("Presence")
    axes = plt.gca()
    axes.set_ylim([-0.2,1.2])
    plt.scatter(np.arange(0,2880), a, s=3)

#%%

def plot_diff(a):
    plt.figure(figsize=(24,7))
    plt.title("diff")
    axes = plt.gca()
    axes.set_ylim([-1.2,1.2])
    plt.scatter(np.arange(0,2879), a)

# %%


plt.figure(figsize=(24,7))
plt.title("Means of presence scores over time for 24h, starting midnight, on "+str(date))
axes = plt.gca()
axes.set_ylim([-0.2,1.2])
plt.scatter(np.arange(0,2880), pp)























# Take basic presence metrics for each alive bee
#%%
df = pd.DataFrame(np.zeros([len(alive_sorted), len(presences)], dtype=np.int32))
df.index = alive_sorted.index


SAMPLE_SIZE = 60

bee_trips = []
for bee_id in df.index[:SAMPLE_SIZE]:
    daily_trips = []
    for (i, (date, presence)) in tqdm(enumerate(presences)):
        if bee_id not in presence.index:
            daily_trips.append(-1)
        else:
            bee_pres = presence.loc[bee_id].copy()
            bee_pres_binarized = binarize_presence(bee_pres)
            diff = np.diff(bee_pres_binarized)
            num_trips = np.abs(diff).sum()/2
            daily_trips.append(num_trips)

    bee_trips.append(daily_trips)

#%%
trips_df = pd.DataFrame(bee_trips, index=df.index[:SAMPLE_SIZE])


for row in np.arange(SAMPLE_SIZE):
    data = trips_df.iloc[row]
    plt.figure(figsize=(24,7))
    plt.title("Number of trips per hiveday for bee " + str(data.name))
    axes = plt.gca()
    # axes.set_ylim([-1.2,1.2])
    plt.plot(np.arange(0,62), data)


present_by_24hs = pd.DataFrame(bees, index=df.index[:10])/2880


#%%



trips = np.diff(bee_pres_binarized)
d = np.diff(bee_pres_binarized)
np.abs(d).sum()


# %present during the 6-18 window
#%%

df = pd.DataFrame(np.zeros([len(alive_sorted), len(presences)], dtype=np.int32))
df.index = alive_sorted.index

intervals_per_hour = 120
bees = []
for bee_id in df.index[:10]:
    daily_sums = []
    for (i, (date, presence)) in tqdm(enumerate(presences)):
        if bee_id not in presence.index:
            daily_sums.append(0)
        else:
            bee_pres = presence.loc[bee_id].copy()
            bee_pres_binarized = binarize_presence(bee_pres)
            daily_pres_sum = bee_pres_binarized[6*intervals_per_hour:18*intervals_per_hour].sum()
            daily_sums.append(daily_pres_sum)
    bees.append(daily_sums)





#%%
present_by_24hs = pd.DataFrame(bees, index=df.index[:10])/1440
# %%



#%%
for bee in present_by_24hs.index:
    plt.figure(figsize=(24,7))
    # plt.title("bee "+str(bee)+" % present by day")
    axes = plt.gca()
    # axes.set_ylim([-0.2,1.2])
    plt.plot(np.arange(0,62), present_by_24hs.loc[bee])













#%% ARCHIVE
# Summarize which bees were alive on which days (0/1)
alive_matrix = np.zeros([len(presences), 4096], dtype=np.int32)
for bee_id in range(0,4096):
    for (i, (date, presence)) in enumerate(presences):
        if bee_id in presence.index:
            alive_matrix[i, bee_id] = 1

alive_df = pd.DataFrame(alive_matrix.T)
alive_df.index.name = 'bee_id'
alive_df.sum().sum()
#%%

alive_sorted = pd.Series(alive_matrix.sum(axis=0))
alive_sorted.sort_values(ascending=False, inplace=True)
alive_sorted = alive_sorted[alive_sorted>0]
alive_sorted[alive_sorted>20]
alive_sorted




# For all days that we have cached, tally offending values (anything above 180) and report what % of all nonzero values it represents.
# Count up the problematic days and print basic info
#%%
 offenders = []
for (date, presence_df) in presences:
    presence_df.index.name = "bee_id"
    total = presence_df.shape[0] * presence_df.shape[1]
    total_nonzero = presence_df[presence_df>0].count().sum()
    offending = presence_df[presence_df>180].count().sum()

    sum = presence_df.sum(axis=1)
    sum = sum[sum>0]
    mean = int(sum.mean()/presence_df.shape[1])

    print("Date: " + str(date) + ", offending values: " + str(offending) + " ({0:.3f}% of all nonzero values)".format((offending/total_nonzero)*100))
    print("There were " + str(presence_df.shape[0]) + " bees alive on that day, with and average number of detections of " + str(mean) + " per 30s interval\n")

    if (((offending/total_nonzero)*100) > 2):
        offenders.append((date, presence_df))


#%%


# Plot means of presence scores for all days
#%%
for (date, presence_df) in res:
    plt.figure(figsize=(24,7))
    plt.title("Means of presence scores over time for 24h, starting midnight, on "+str(date))
    axes = plt.gca()
    axes.set_ylim([0,70])
    plt.plot(np.arange(0,presence_df.shape[1]), presence_df.mean())
    plt.savefig('means_of_presence_'+str(date)+'.png')
#%%



# Draft used for making put_entries_exits_to_dict, probably removable
exits_dict = {}
for i, row in presence.iterrows():
    # For each bee, make a list of exits
    diff = np.diff(row)
    exits = np.where(diff == -1)[0]
    exit_timestamps = [npdate + np.timedelta64(int(exit)*30, 's') for exit in exits]
    exits_dict[row.name] = exit_timestamps





# SNIPPET FROM DAVID regarding (binarized_presence -> Trips)
#%%

d_orig = [1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1]
len(d_orig)

d = np.diff(d_orig)
print(d)
len(d)
#%%
gaps = np.where(np.abs(d) == 1)[0]
gaps
idx = gaps[0]
for i in range(1, gaps.shape[0]):
    chunk = d_orig[idx:gaps[i]]
    idx = gaps[i]
    print(chunk)
display(d_orig[idx:])
gaps
#%%

d_orig = [[1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1],[1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1]]

np.diff(d_orig, axis=1)
