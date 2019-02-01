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


# For all days that we have cached, tally offending values (anything above 180) and report what % of all nonzero values it represents.
#%%
presences = c.load_all_presence_caches()
#%%


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
alive_sorted;






#%%
def binarize_presence(presence_for_day_series):
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
#%%




#%%


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




xpresent_by_24hs = pd.DataFrame(bees, index=df.index[:10])/2880
# %%



# plot several bees
# #%%
# for bee in present_by_24hs.index:
#     plt.figure(figsize=(24,7))
#     plt.title("bee #"+str(bee)+" % present by day")
#     axes = plt.gca()
#     # axes.set_ylim([-0.2,1.2])
#     plt.plot(np.arange(0,62), present_by_24hs.loc[bee])



#%% single ex

presence = presences[2][1]
bee_id = 1901

bee_pres = presence.loc[bee_id].copy()
type(bee_pres[2])

bee_pres_binarized = binarize_presence(bee_pres)

type(bee_pres_binarized[2])
print(bee_pres_binarized[:100])

short = bee_pres_binarized[:100]

print(short)

print(np.diff(short))


#%%



trips = np.diff(bee_pres_binarized)


d = np.diff(bee_pres_binarized)
np.abs(d).sum()

#%%


d_orig = [1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1]
len(d_orig)

d = np.diff(d_orig)
print(d)
len(d)
#%%
gaps = np.where(np.abs(d) == 1)[0] + 1
idx = gaps[0]
for i in range(1, gaps.shape[0]):
    chunk = d_orig[idx:gaps[i]]
    idx = gaps[i]
    print(chunk)
display(d_orig[idx:])
gaps



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








# %%
def plot_presence(a):
    plt.figure(figsize=(24,7))
    plt.title("Presence")
    axes = plt.gca()
    axes.set_ylim([-0.2,1.2])
    plt.scatter(np.arange(0,2880), a)

#%%

# %%
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
plt.scatter(np.arange(0,2880), a)















































#%% ARCHIVE





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







for (date, _) in presences:
    print("alive: " + str(get_alive_bees_for_day(date).shape[0]))
