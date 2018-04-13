import numpy as np
import pandas as pd


from datetime import timedelta, datetime
import time

import bb_utils
import bb_utils.meta
import bb_utils.ids

def detections_to_presence(num_hours, datetime_start, num_intervals_per_hour, bee_ids_from_group):
    location_prefix = "/mnt/storage/janek/" # or ""

    #Loading first element before the loop, to have a table formatted nicely for appending
    start_csv_name = (datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(location_prefix+start_csv_name, parse_dates=['timestamp'], usecols=['timestamp', 'bee_id'])


    #read and concat a number of hour-long csvs (note: thekla memory crashes if >16)
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
            
    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    csv_name = 'PRESENCE-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'.csv'
    
    #Saving intermediate result: the presence dataframe, with 1's and 0's for bees present
    presence_df.to_csv(location_prefix+csv_name)
    
    print("SAVED", location_prefix+csv_name)
    
    return location_prefix+csv_name