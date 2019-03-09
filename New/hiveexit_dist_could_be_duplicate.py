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
import numpy as np
from pytz import timezone
sys.path.append(os.getcwd()+'/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
meta = bb_utils.meta.BeeMetaInfo()
#%%






gaps_sample.head(3)


#%%
# Real gaps 100% gaps
detection_confidence_requirement = 0.99
gaps = c.load_multiple_day_caches(type=CacheType.gaps, detection_confidence_requirement=detection_confidence_requirement)
gaps_df = pd.concat(gaps)
gaps_sample = gaps_df.sample(1000)
# %%


# %% Add origins
gaps_df['origin_for_exit'] = gaps_df.apply(origin_for_exit, axis=1)
gaps_df['origin_for_entry'] = gaps_df.apply(origin_for_entry, axis=1)


# %% Add distance for exit
df = gaps_df
o_x_ex = [x for (x,y) in df.origin_for_exit]
o_y_ex = [y for (x,y) in df.origin_for_exit]

diff_x = df.exit_x - o_x_ex
diff_y = df.exit_y - o_y_ex

d = pd.Series(np.linalg.norm([diff_x, diff_y], axis=0))

gaps_df['hiveexit_distance_for_exit'] = d


# %% Add distance for entry
df = gaps_df
o_x_en = [x for (x,y) in df.origin_for_entry]
o_y_en = [y for (x,y) in df.origin_for_entry]

diff_x = df.entry_x - o_x_en
diff_y = df.entry_y - o_y_en

d = pd.Series(np.linalg.norm([diff_x, diff_y], axis=0))

gaps_df['hiveexit_distance_for_entry'] = d




























# %% FUNCTIONS

def origin_for_exit(row):
    origin = np.array([0, 250]) if row.hive_side_exit == 1 else np.array([350, 250])
    return origin

def origin_for_entry(row):
    origin = np.array([0, 250]) if row.hive_side_entry == 1 else np.array([350, 250])
    return origin









# %% ARCHIVE
# Some decently nice plots of gaps starts per age group

tsb = trips_side_b
tsb = tsb[tsb.age_group > 7]


tl = trips_locations.apply(add_exit_distance, axis=1)


#%%
plt.figure(figsize=(20,15))
sns.scatterplot(tsb.x, tsb.y, hue=tsb.age_group)


#%%
ts = trips_side_a
ts = ts[ts.age_group > 8]
#%%
plt.figure(figsize=(20,15))
sns.scatterplot(ts.x, ts.y, hue=ts.age_group)



xy = xy[~np.any(np.isnan(xy), axis=1), :]




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
