#%%
import datetime
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/')
import pandas as pd
import numpy as np
import tqdm
from bee_helpers import get_alive_bees_for_day
from file_helpers import cache_detections_from_database, detections_to_presence
from bee_cache import CacheType, CacheFormat, Cache;
from functools import reduce
#%%

# Goal: investigate why some bees have presence higher than 3FPS should allow


# 1. Load presence files for the same day, from different cams
c = Cache()
cam0 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_0', type=CacheType.presence, format=CacheFormat.csv)
cam1 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_1', type=CacheType.presence, format=CacheFormat.csv)
cam2 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_2', type=CacheType.presence, format=CacheFormat.csv)
cam3 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_3', type=CacheType.presence, format=CacheFormat.csv)
cam01 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_01', type=CacheType.presence, format=CacheFormat.csv)
cam23 = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_cams_23', type=CacheType.presence, format=CacheFormat.csv)
quadcam = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_099_untrusted', type=CacheType.presence, format=CacheFormat.csv)
# NOTE: these all might (and do) have different shapes (as different subsets of bees were detected by different cams that day)


cams = [cam0, cam1, cam2, cam3]
doublecams = [cam01, cam23]
quadcams = [quadcam]

all_cams = cams+doublecams+quadcams

ids = []


# TODO: make sure this is done in cache loading
for cam_df in all_cams:
    cam_df.index = cam_df.id
    cam_df.drop(columns=['Unnamed: 0', 'id'], inplace=True)
    ids.append(cam_df.index)

list(cam0.index.astype(int))

cam0.index.notnull().shape
cam0.index.shape

cam0.iloc[-900:]

cam0.index.isna().sum()

cam1.index.isna().sum()

quadcam.index.isna().sum()
# 2. Plot them on the same plot, with different colors per cam and black fot the sum of all cams


# Q: why is there a ton of NaNs in cam0?

# it seems like every time there were no detections for a given bee, instead of filling zeros, we had NaNs
# as consequence, somehow, the ID is a NaN (?)

# try filling zeroes before



# Q: which bee do we want to plot?
# how many bees are there that were detected by all cams? maybe just take the AND of all

xd = detections_to_presence(1, datetime_start, num_intervals_per_hour, bee_ids)



cam0.head()
cam3.head()
