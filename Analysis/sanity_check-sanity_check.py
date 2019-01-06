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



zdf = pd.read_csv("/home/mi/rrszynka/mnt/janek/caches/Detections/DETECTIONS-2016-07-25_15:00:00_conf_099.csv", parse_dates=['timestamp'])
