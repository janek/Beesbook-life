#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys 
sys.path.append('../Python-modules/') #For bee_helpers and file_helpers 
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids
from file_helpers import delete_detection_caches_for_date, detections_to_presence, detections_to_presence_locations, create_presence_cache_filename, create_presence_cache_filename, cache_location_prefix, cache_detections_from_database, detections_to_presence_locations_front, detections_to_presence_locations_back, cache_death_dates, last_days_caches
from datetime import timedelta, datetime
from pathlib import Path
from bee_cache import Cache, CacheType, CacheFormat
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')


# In[3]:


experiment_start_day = datetime(2016, 7, 20) # TODO: those are dates of first and last detections
experiment_end_day = datetime(2016, 9, 19)   # consider making the period smaller

datetime_start = datetime(2016, 7, 25)
# datetime_start = datetime(2016, 7, 25)
num_days_to_process = 1

observ_period = timedelta(hours=1)
num_observ_periods = 24 #hours in day
detection_confidence_requirement = 0.99 # atm switching between: 0, 0.7, 0.99
num_intervals_per_hour = 120

(csv_name, csv_path) = create_presence_cache_filename(num_observ_periods, datetime(2016, 7, 20), num_intervals_per_hour, locations=True, cam_orientation='back')


# In[4]:


num_hours = 1
interval_starttime = datetime_start
start_day = datetime_start


# In[5]:


# cache_detections_from_database(datetime_start, observ_period, num_observ_periods, detection_confidence_requirement


# In[6]:


#(bee_ids_as_ferwar_format, bee_ids_as_beesbookid_format) = get_all_bee_ids()


# In[7]:


#detections_to_presence(num_observ_periods, start_day, num_intervals_per_hour, bee_ids_as_ferwar_format, method='counts', detection_confidence_requirement=0)


# In[8]:


def plot_k_hists(pres, k=3):
    pres = pres[pres.sum(axis=1) > 0]
    rands = np.random.randint(pres.shape[0], size=k)
    fig, ax = plt.subplots(k)

    for i, axi in enumerate(ax):
        axi.set_ylim([0,125])
        axi.set_xlim([-5,200])
        axi.set_ylabel('Amount of intervals with given presence detected')
        axi.set_xlabel('Presence (max should be 90)  [bee #'+str(rands[i])+']')
        pres.iloc[rands[i]].hist(bins=100, figsize=(27,15), ax=ax[i])


# In[9]:


# plot_k_hists(presence_conf_099_midnight_sample)


# In[10]:


c = Cache()


# In[11]:


df = c.load('PRESENCE-counts-2016-07-25_00_num_hours_24_int_size_120_conf_099', type=CacheType.presence, format=CacheFormat.csv)


# In[12]:


df.head()


# In[13]:


df.index.rename('id', inplace=True)
df = df.drop(columns=['Unnamed: 0','id'])


# In[16]:


sums = df.sum(axis=1)
sums


# In[ ]:


ax = presence_conf_0_midday_sample[presence_conf_0_midday_sample.sum(axis=1)>=100].sum(axis=1).hist(bins=200, figsize=[27,10])
ax.set_ylim([0,300])
ax.set_title("Distribution of values for sums of presence over 1 hour. max should be 120*90=10800");


# In[ ]:





# In[ ]:





# In[ ]:


ax = df[df.sum(axis=1)>=100].sum(axis=1).hist(bins=200, figsize=[27,10])
# ax = df.sum(axis=1).hist(bins=200, figsize=[27,10])
ax.set_ylim([0,2500])
ax.set_title("Distribution of values for sums of presence over 24 hours");


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


presence_conf_099_midday_sample 


# In[ ]:


presence_conf_099_midnight_sample


# In[ ]:


presence_conf_0_midnight_sample


# In[ ]:


presence_conf_0_midday_sample


# In[ ]:




