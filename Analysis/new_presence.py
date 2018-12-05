#!/usr/bin/env python
# coding: utf-8
import os; os.getcwd()
import sys
from datetime import timedelta, datetime
from pathlib import Path
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

import datetime

os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers and file_helpers
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids
from file_helpers import delete_detection_caches_for_date, detections_to_presence, detections_to_presence_locations, create_presence_cache_filename, create_presence_cache_filename, cache_location_prefix, cache_detections_from_database, detections_to_presence_locations_front, detections_to_presence_locations_back, cache_death_dates, last_days_caches
from bee_cache import Cache, CacheFormat, CacheType





c = Cache()
presence_conf_099_1h = c.load('PRESENCE-counts-2016-07-25_00_num_hours_1_int_size_120_conf_099', type=CacheType.presence, format=CacheFormat.csv)
presence_conf_099_1h.index.rename('bee_id', inplace = True)
presence_conf_099_1h.drop(columns=['Unnamed: 0', 'id'], inplace = True)
presence_conf_099_1h.shape

presence_conf_099_24h = c.load('PRESENCE-counts-2016-07-25_00_num_hours_24_int_size_120_conf_099', type=CacheType.presence, format=CacheFormat.csv)
presence_conf_099_24h.index.rename('bee_id', inplace = True)
presence_conf_099_24h.drop(columns=['Unnamed: 0', 'id'], inplace = True)
presence_conf_099_24h.shape


alive_bees_2016 = c.load('alive_bees_2016')
alive_bees_07_25_2016 = alive_bees_2016[alive_bees_2016['timestamp'] == datetime(2016, 7, 25).date()]



presence_conf_099_1h_alive = presence_conf_099_1h.iloc[alive_bees_07_25_2016.bee_id]
presence_conf_099_24h_alive = presence_conf_099_24h.iloc[alive_bees_07_25_2016.bee_id]

plot_k_hists(presence_conf_099_1h_alive)



# In[ ]:



type(datetime.datetime(2016,7,20).date()) == datetime.date

ax = presence_conf_099_24h.sum(axis=1).hist(bins=200, figsize=[27,10])
ax = presence_conf_099_24h_alive.6543 sum(axis=1).hist(bins=200, figsize=[27,10])
ax.set_ylim([0,800])
ax.set_title("Distribution of values for sums of presence over 1 hour. max should be 120*90=10800");



# In[ ]:


ax = df[df.sum(axis=1)>=100].sum(axis=1).hist(bins=200, figsize=[27,10])
# ax = df.sum(axis=1).hist(bins=200, figsize=[27,10])
ax.set_ylim([0,2500])
ax.set_title("Distribution of values for sums of presence over 24 hours");


# In[ ]:




# In[ ]:
# plotting func

def plot_k_hists(pres, k=3):
    pres = pres[pres.sum(axis=1) > 0]
    rands = np.random.randint(pres.shape[0], size=k)
    fig, ax = plt.subplots(k)

    for i, axi in enumerate(ax):
        axi.set_ylim([0,125])
        axi.set_xlim([-5,200])
        axi.set_ylabel('Amount of intervals with given presence detected')
        axi.set_xlabel('Presence (max should be 90)  [bee #'+str(rands[i])+']')
        pres.iloc[rands[i]].hist(bins=100, figsize=(18,14), ax=ax[i])



# In[ ]:




# archive: getting other variants of data# In[3]:
observ_period = timedelta(hours=1)
experiment_start_day = datetime(2016, 7, 20) # TODO: those are dates of first and last detections
experiment_end_day = datetime(2016, 9, 19)   # consider making the period smaller



datetime_start = datetime(2016, 7, 25)
num_observ_periods = 1 # hours
num_intervals_per_hour = 120

(csv_name, csv_path) = create_presence_cache_filename(num_observ_periods, datetime(2016, 7, 20), num_intervals_per_hour, locations=True, cam_orientation='back')

(bee_ids_as_ferwar_format, bee_ids_as_beesbookid_format) = get_all_bee_ids()

d = detections_to_presence(num_observ_periods, datetime_start, num_intervals_per_hour, bee_ids_as_ferwar_format, method='counts', detection_confidence_requirement=0.99)
