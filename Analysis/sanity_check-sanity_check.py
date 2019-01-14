#%%
import datetime
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/')
import pandas as pd
import numpy as np
import tqdm
from bee_helpers import get_alive_bees_for_day
from file_helpers import cache_detections_from_database, detections_to_presence, detections_to_presence_locations_front, detections_to_presence_locations_back, detections_to_presence_locations
from bee_cache import CacheType, CacheFormat, Cache;
#%%

# Goal: investigate why some bees have presence higher than 3FPS should allow



# 1. Download and save a detections file for a given hour of a given day (or all hours of a given day)
# cache = Cache()
# det = cache.load("DETECTIONS-2016-07-25_15:00:00_conf_099", type = CacheType.detections, format = CacheFormat.csv)
# df = pd.read_csv("/home/mi/rrszynka/mnt/janek/caches/Detections/DETECTIONS-2016-07-25_15:00:00_conf_099.csv", parse_dates=['timestamp'])
# df = df.drop(columns=['Unnamed: 0'])




# Side note: fixing detections_to_presence_functions:
# 1. Save one of each for future reference

datetime_start = datetime.datetime(2016,8,9,15)
num_hours = 1
num_intervals_per_hour = 120
bee_ids = get_alive_bees_for_day(datetime_start.date()).bee_id.tolist()



df = detections_to_presence(num_hours, datetime_start, num_intervals_per_hour, bee_ids)


# dloc = detections_to_presence_locations(num_hours, datetime_start, num_intervals_per_hour, bee_ids)
# dfront = detections_to_presence_locations_front(num_hours, datetime_start, num_intervals_per_hour, bee_ids)
# dback = detections_to_presence_locations_back(num_hours, datetime_start, num_intervals_per_hour, bee_ids)
