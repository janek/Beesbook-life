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




# For all days that we have cached, tally offending values (anything above 180) and report what % of all nonzero values it represents.
#%%
presences = c.load_all_presence_caches()
#%%
for (date, presence_df) in presences:
    total = presence_df.shape[0] * presence_df.shape[1]
    total_nonzero = presence_df[presence_df>0].count().sum()
    offending = presence_df[presence_df>180].count().sum()
    print("Date: " + str(date) + ", offending values: " + str(offending) + " ({0:.3f}% of all nonzero values)".format((offending/total_nonzero)*100))



# Plot means of presence scores for all days
#%%
for (date, presence_df) in presences:
    plt.figure(figsize=(24,7))
    plt.title("Means of presence scores over time for 24h, starting midnight, on "+str(date))
    axes = plt.gca()
    axes.set_ylim([0,70])
    plt.plot(np.arange(0,presence_df.shape[1]), presence_df.mean())
    plt.savefig('means_of_presence_'+str(date)+'.png')
