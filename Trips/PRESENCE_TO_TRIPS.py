
# coding: utf-8

# In[7]:


get_ipython().run_line_magic('matplotlib', 'inline')

import matplotlib.pyplot as plt
import matplotlib
import math
import seaborn as sns
import numpy as np
import pandas as pd
import psycopg2
import psycopg2.extras
from datetime import timedelta, datetime
import bee_helpers as bh
from bee_helpers import cache_location_prefix, detections_to_presence, calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids, create_presence_cache_filename
import time


import bb_utils
import bb_utils.meta
import bb_utils.ids
import bb_backend
from bb_backend.api import FramePlotter, VideoPlotter
from bb_backend.api import get_plot_coordinates, transform_axis_coordinates, get_image_origin


meta = bb_utils.meta.BeeMetaInfo()
BeesbookID = bb_utils.ids.BeesbookID


# In[8]:


#TODO: Constants cannot be defined twice! (here and DB_TO_DETECTIONS)
#potential solution: google jupyter magic/jupyter constant definition 


#Parameters for loading data, currently using known date of 23th, august 2016)
num_hours = 12

datetime_start = datetime(2016, 8, 24)

#Parameters for presenting data
bin_size_in_hours = 24

#Hyperparameters for the data wrangling process
num_intervals_per_hour = 60
num_intervals_per_minute = num_intervals_per_hour/60
rolling_window_size = 5

total_num_intervals = (num_intervals_per_hour*num_hours)

print("Starting from", datetime_start, "with number of hours:", num_hours)
print("Bin size for the trip lengths plot:", bin_size_in_hours)
print("Number of intervals per hour:", num_intervals_per_hour)
print("Rolling win size:", rolling_window_size)
#(NOTE: First detections are on 20.07.2016, last are 19.09.2016 (3 months duration))


# In[9]:


#Loading the csv of intermediate result (saved from prevoius cell)
#example value: "/mnt/storage/janek/caches/Presence/PRESENCE-2016-08-23_00_num_hours_24_int_size_120.csv"

#NOTE: the presence cache does not yet know what bees it contains! 
(csv_name, csv_path) = create_presence_cache_filename(num_hours, datetime_start, num_intervals_per_hour)


print('Loading '+csv_path)

presence_df = pd.read_csv(csv_path).iloc[:,1:]
#NOTE: save and read csv adds a duplicate index column, which has to be removed with iloc
#TODO: find a cleaner way to to solve that
presence_df.shape


# In[10]:


#TODO: Constants cannot be defined twice! (here and DB_TO_DETECTIONS)
#potential solution: google jupyter magic/jupyter constant definition 


#Parameters for loading data, currently using known date of 23th, august 2016)
num_hours = 12

datetime_start = datetime(2016, 8, 24)

#Parameters for presenting data
bin_size_in_hours = 24

#Hyperparameters for the data wrangling process
num_intervals_per_hour = 60
num_intervals_per_minute = num_intervals_per_hour/60
rolling_window_size = 5

total_num_intervals = (num_intervals_per_hour*num_hours)

print("Starting from", datetime_start, "with number of hours:", num_hours)
print("Bin size for the trip lengths plot:", bin_size_in_hours)
print("Number of intervals per hour:", num_intervals_per_hour)
print("Rolling win size:", rolling_window_size)
#(NOTE: First detections are on 20.07.2016, last are 19.09.2016 (3 months duration))

