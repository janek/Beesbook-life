import numpy as np
import pandas as pd


from datetime import timedelta, datetime
import time
import random

import bb_utils
import bb_utils.meta
import bb_utils.ids

def create_presence_cache_filename(num_hours, datetime_start, num_intervals_per_hour):
    location_prefix = "/mnt/storage/janek/caches/" # or ""
    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    csv_name = 'PRESENCE-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'.csv'
    csv_name_and_location = location_prefix+csv_name
    return (location_prefix, csv_name, csv_name_and_location)

def detections_to_presence(num_hours, datetime_start, num_intervals_per_hour, bee_ids_from_group):
    (location_prefix, csv_name, csv_name_and_location) = create_presence_cache_filename(num_hours, datetime_start, num_intervals_per_hour)

    #Loading first element before the loop, to have a table formatted nicely for appending
    start_csv_name = (datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(location_prefix+start_csv_name, parse_dates=['timestamp'], usecols=['timestamp', 'bee_id'])

    #read and concat a number of hour-long csvs (note: this is because thekla memory crashes if attempting >16h at a time)
    for i in range(1, num_hours):
        csv_name = (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
        print('Processing '+csv_name)
        new_data = pd.read_csv(location_prefix+csv_name, parse_dates=['timestamp'], usecols=['timestamp', 'bee_id'])
        detections_df = pd.concat([detections_df, new_data])
        print('Num. rows after appending: '+str(detections_df.shape[0])) #TODO: tqdm progress bar 

    #interval length is the total observation period divided by total number of intervals
    total_num_intervals = (num_intervals_per_hour*num_hours)
    interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)

    # prepare dataframe with zeros in the shape [bees x total_num_intervals]
    # append bee_ids from the left
    intervals = pd.DataFrame(data=np.zeros([len(bee_ids_from_group),total_num_intervals])) 
    bee_ids = pd.DataFrame(data={'id': bee_ids_from_group})
    presence_df = pd.concat([bee_ids, intervals], axis=1)
    
    #Iterate over intervals and over detections
    #If a bee from bee_ids is detected within a given interval, mark the cell for that bee and interval with a '1'

    interval_starttime = datetime_start
    # print("Processing intervals: ")
    for interval in range(total_num_intervals): 
        #choose detections for interval
        interval_endtime = interval_starttime + interval_length
        before = detections_df['timestamp'] >= interval_starttime 
        after = detections_df['timestamp'] < interval_endtime
        interval_detections = detections_df[before & after]
        bee_row_number = 0
        for bee in presence_df['id']: 
            if bee in interval_detections['bee_id'].unique():
                presence_df.set_value(bee_row_number, interval, 1)
            bee_row_number += 1 
        interval_starttime = interval_endtime
        if interval%100 == 0:
            print(interval,", ", end='') #TODO: tqdm progress bar https://www.youtube.com/watch?v=T0gmQDgPtzY&feature=youtu.be
            
    
    
    #Saving intermediate result: the presence dataframe, with 1's and 0's for bees present
    presence_df.to_csv(csv_name_and_location)
    
    print("SAVED", csv_name_and_location)
    
    return csv_name_and_location


def calc_trip_lengths(presence_df, total_num_intervals):
    #Takes Presence dataframe and total number of intervals
    #Returns and array of arrays containing lengths of individual trips of each consecutive bee
    trip_lengths = []

    for bee in range(0, presence_df.shape[0]):
        curr_trip_length = 0
        curr_bee_trip_lenghts = []
        #fill with trip lengths
        for interval in range(total_num_intervals): #t: 2880
            #get the 0/1 value from presence_df at the given (bee, interval)
            bool_is_present = presence_df.iat[bee, interval]
            if bool_is_present == 0.0: #bee not present in this interval
                if curr_trip_length != 0: #if we had a value for a trip length -> means trip ends here -> add it to trips and reset the counter
                    curr_bee_trip_lenghts.append(curr_trip_length)
                    curr_trip_length = 0
            if bool_is_present == 1.0: #bee present in this interval, means trip is underway -> increment the length counter 
                curr_trip_length += 1
        trip_lengths.append(curr_bee_trip_lenghts)
    return trip_lengths



def get_forager_bee_ids():
    #Getting a known forager group from manual labeling experiments
    meta = bb_utils.meta.BeeMetaInfo()
    group_id = 20
    bee_ids_as_beesbookid_format = list(map(bb_utils.ids.BeesbookID.from_dec_12, meta.get_foragergroup(group_id).dec12))
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)

def get_random_bee_ids(amount):
    meta = bb_utils.meta.BeeMetaInfo()
    bees = set()
    while len(bees) < amount:
        bee_id_dec = random.randint(0, 4097)
        bee_id = bb_utils.ids.BeesbookID.from_dec_9(bee_id_dec)
        if meta.get_hatchdate(bee_id) != np.datetime64('NaT'): 
            bees.add(bee_id)
    bee_ids_as_beesbookid_format = list(bees)
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)


def get_all_bee_ids():
    meta = bb_utils.meta.BeeMetaInfo()
    bees = []
    for id in range(0,4096):
        bee_id = bb_utils.ids.BeesbookID.from_dec_9(id)
        if meta.get_hatchdate(bee_id) != np.datetime64('NaT'): 
            bees.append(bee_id)
    bee_ids_as_beesbookid_format = list(bees)
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)

#also write a function to get bees alive at a certain day 