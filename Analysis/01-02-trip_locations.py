import pandas as pd
import h5py
import matplotlib.pyplot as plt
import bb_utils
import datetime
import os
import sys
import seaborn as sns
import tqdm
import pytz
from pytz import timezone
sys.path.append(os.getcwd()+'/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
meta = bb_utils.meta.BeeMetaInfo()

#%%
# Locations based on the file from David

trips_locations = c.load('trips_with_coordinates_and_ages', format = CacheFormat.hdf)
trips_side_a = trips_locations[trips_locations.hive_side == 0]
trips_side_b = trips_locations[trips_locations.hive_side == 1]
trips_side_a.sample(10)



#%%
ts = trips_side_a
ts = ts[ts.age_group > 8]
#%%
plt.figure(figsize=(20,15))
sns.scatterplot(ts.x, ts.y, hue=ts.age_group)



tsb = trips_side_b
tsb = tsb[tsb.age_group > 7]
#%%
plt.figure(figsize=(20,15))
sns.scatterplot(tsb.x, tsb.y, hue=tsb.age_group)





























#%% ARCHIVE
# Code used to add age and age_group to trips_with_coordinates

#%%
def process_row(row):
    id = bb_utils.ids.BeesbookID.from_ferwar(int(row['bee_id']))
    date = row['timestamp'].replace(tzinfo=None)
    return (meta.get_age(id, date))
#%%

ages = trip_locations.apply(process_row, axis=1)
age_groups = abs(ages.dt.days // 5)

trip_loc_ages = trip_locations.assign(age=ages, age_group=age_groups)
trip_loc_ages.to_hdf('/home/mi/rrszynka/mnt/janek/caches/Other/trips_with_coordinates_and_ages.hdf5', key='df', mode='w')


trip_loc_ages
#%%
# To see format of bee_exits_timestamps (step before trips_locations, passed to David's notebook)
exits = c.load('bee_exits_timestamps')
# len: ~2966
# format:    bee_id: t1, t2, t3 (..)


#%%
# matplotlib plots
plt.figure(figsize=(30,20))
plt.scatter(trips_side_a.x, trips_side_a.y, s = 3)
