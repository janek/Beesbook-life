#%%
from datetime import timedelta, datetime
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/')
import pandas as pd
import numpy as np
import tqdm
from bee_helpers import get_alive_bees_for_day
from file_helpers import cache_detections_from_database, detections_to_presence
from bee_cache import CacheType, CacheFormat, Cache; cache = Cache()
#%%

# Goal: investigate why some bees have presence higher than 3FPS should allow



# 1. Download and save a detections file for a given hour of a given day (or all hours of a given day)

det = cache.load("DETECTIONS-2016-07-25_15:00:00_conf_099", type = CacheType.detections, format = CacheFormat.csv)
det = det.drop(columns=['Unnamed: 0'])
detections_df = det


# Args that would go into the detections_to_presence function call

num_intervals_per_hour = 120
num_hours = 1

datetime(2016,7,25).date()

bee_ids = get_alive_bees_for_day(datetime(2016,7,25).date())


# interval length is the total observation period divided by total number of intervals
total_num_intervals = (num_intervals_per_hour*num_hours)
interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)



# prepare dataframe with zeros in the shape [bees x total_num_intervals]
# append bee_ids from the left
intervals = pd.DataFrame(data=np.zeros([len(bee_ids),total_num_intervals]))
bee_ids = pd.DataFrame(data={'id': bee_ids['bee_id']})
presence_df = pd.concat([bee_ids, intervals], axis=1)


type(detections_df.timestamp[0])

after_start = detections_df['timestamp'] >= interval_starttime

interval_starttime = datetime_start
# print("Processing intervals: ")
for interval in range(total_num_intervals):
    #choose detections for interval
    interval_endtime = interval_starttime + interval_length
    after_start = detections_df['timestamp'] >= interval_starttime
    before_end = detections_df['timestamp'] < interval_endtime
    interval_detections = detections_df[after_start & before_end]
    bee_row_number = 0



    counts = interval_detections['bee_id'].value_counts()
    keys = counts.keys().tolist()
    counts = counts.tolist()

    for i in np.arange(0,len(counts)):
        bee = keys[i]
        presence_df.loc[bee, interval] = counts[i]

    interval_starttime = interval_endtime
