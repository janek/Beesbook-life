#%%
import datetime
import random
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/')
import pandas as pd
import numpy as np
from tqdm import tqdm
from bee_helpers import get_alive_bees_for_day
from file_helpers import cache_detections_from_database, detections_to_presence
from bee_cache import CacheType, CacheFormat, Cache;
from functools import reduce
import matplotlib.pyplot as plt
#%%

# Goal: investigate why some bees have presence higher than 3FPS should allow


# Load presence files for the same day, by different cams

cam0 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_0', type=CacheType.presence, format=CacheFormat.csv)

cam1 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_1', type=CacheType.presence, format=CacheFormat.csv)
cam2 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_2', type=CacheType.presence, format=CacheFormat.csv)
cam3 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_3', type=CacheType.presence, format=CacheFormat.csv)
cam01 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_01', type=CacheType.presence, format=CacheFormat.csv)
cam23 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_23', type=CacheType.presence, format=CacheFormat.csv)
quadcam = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheFormat.csv)
# NOTE: these all might (and do) have different shapes (as different subsets of bees were detected by different cams that day)






cams = [cam0, cam1, cam2, cam3]
doublecams = [cam01, cam23]
quadcams = [quadcam]
all_cams = cams+doublecams+quadcams


bee_ids = list(get_alive_bees_for_day(datetime.datetime(2016,8,9)).bee_id)

for cam_df in all_cams:
    cam_df.index = bee_ids

# Check sums and nans:
cam0.sum().sum() + cam1.sum().sum() == cam01.sum().sum()
cam2.sum().sum() + cam3.sum().sum() == cam23.sum().sum()
cam01.sum().sum() + cam23.sum().sum() == quadcam.sum().sum()
quadcam.isna().sum().sum() == 0

quadcam.head()
# 1. Copy code from pres_from_interval and plot quadcam for [a) rand bee b) rand forager c) rand problematic]
#%%
# bee_offenders = [2477, 1755, 1128, 2381]
bee_id = random.choice(list(bee_offenders))
# bee_id = 1755
plt.figure(figsize=(24,7))
axes = plt.gca()
axes.set_ylim([-5,370])
plt.scatter(np.arange(0,quadcam.shape[1]), quadcam.loc[bee_id], s=0.5)
plt.title("Bee " + str(bee_id))
#%%

# 4 cams 1 plot
# bee_id = random.choice(list(bee_ids)) # WARN: choosing new bee, remove later to rely on previous choice in cell above
bee_id = random.choice(list(bee_ids))
plt.figure(figsize=(33,7))
axes = plt.gca()
axes.set_ylim([-5,370])
plt.scatter(np.arange(0,quadcam.shape[1]), cam0.loc[bee_id], s=0.5)
plt.scatter(np.arange(0,quadcam.shape[1]), cam1.loc[bee_id], s=0.5)
plt.scatter(np.arange(0,quadcam.shape[1]), cam2.loc[bee_id], s=0.5)
plt.scatter(np.arange(0,quadcam.shape[1]), cam3.loc[bee_id], s=0.5)

plt.title("Bee " + str(bee_id));

#%%

# 4 cams 1 plot
plt.figure(figsize=(33,7))
axes = plt.gca()
axes.set_ylim([-5,370])
plt.scatter(np.arange(0,quadcam.shape[1]), cam0.loc[bee_id], s=0.5)
plt.scatter(np.arange(0,quadcam.shape[1]), cam1.loc[bee_id], s=0.5)
# plt.scatter(np.arange(0,quadcam.shape[1]), cam2.loc[bee_id], s=0.5)
# plt.scatter(np.arange(0,quadcam.shape[1]), cam3.loc[bee_id], s=0.5)

plt.title("Bee " + str(bee_id));
#%%


# 4 cams 1 plot
plt.figure(figsize=(33,7))
axes = plt.gca()
axes.set_ylim([-5,370])
# plt.scatter(np.arange(0,quadcam.shape[1]), cam0.loc[bee_id], s=0.5)
plt.scatter(np.arange(0,quadcam.shape[1]), cam1.loc[bee_id], s=0.5)
# plt.scatter(np.arange(0,quadcam.shape[1]), cam2.loc[bee_id], s=0.5)
# plt.scatter(np.arange(0,quadcam.shape[1]), cam3.loc[bee_id], s=0.5)

plt.title("Bee " + str(bee_id));

#%%


# 2. Plot them on the same plot, with different colors per cam and black fot the sum of all cams





# Filter 1 is Ben's 'alive_bees_2016. Should we filter out bees with very low presence aswell?



# Archived:
# Q: why is there a ton of NaNs in cam0?

# it seems like every time there were no detections for a given bee, instead of filling zeros, we had NaNs
# as consequence, somehow, the ID is a NaN (?)

# try filling zeroes before



# Q: which bee do we want to plot?
# how many bees are there that were detected by all cams? maybe just take the AND of all
