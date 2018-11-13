import os
print(os.getcwd())

import os, shutil
import bb_utils
import bb_utils.meta
import bb_utils.ids
import bb_backend
from datetime import timedelta, datetime
import time
import psycopg2
import psycopg2.extras
import numpy as np
import pandas as pd
from tqdm import tqdm
from pathlib import Path



# bb_backend.api.server_adress = 'localhost:8000'
connect_str = """dbname='beesbook' user='reader' host='tonic.imp.fu-berlin.de' password='' application_name='mehmed'"""
#removed storage from filepath

#TODO: defined here, main notebook and file_helpers - how to extract it to be just in one place?
cache_location_prefix = os.getcwd()+"/caches"
detections_cache_path = cache_location_prefix + "/Detections/"


def delete_detection_caches_for_date(date_string, directory=detections_cache_path):
    ### date_string must be in MM-DD_hh:mm:ss format
    name_prefix = "DETECTIONS-"
    removed_count = 0
    for the_file in os.listdir(detections_cache_path):
        if the_file.startswith(name_prefix+date_string):
            file_path = os.path.join(detections_cache_path, the_file)
            try:
                if os.path.isfile(file_path):
                    print("Removing " + the_file)
                    os.unlink(file_path)
            except Exception as e:
                print(e)

def create_presence_cache_filename(num_hours, datetime_start, num_intervals_per_hour):
    presence_cache_location_prefix = cache_location_prefix + "/Presence/"
    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    csv_name = 'PRESENCE-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'.csv'
    csv_path = presence_cache_location_prefix+csv_name
    print("HALO")
    return (csv_name, csv_path)

def create_presence_locations_cam_cache_filename(num_hours, datetime_start, num_intervals_per_hour, orientation):
    presence_cache_location_prefix = cache_location_prefix + "Presence/locations/cam/"+orientation
    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    csv_name = 'PRESENCE-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'.csv'
    csv_path = presence_cache_location_prefix+csv_name
    return (csv_name, csv_path)

def create_presence_locations_cache_filename(num_hours, datetime_start, num_intervals_per_hour):
    presence_cache_location_prefix = cache_location_prefix + "Presence/locations/"
    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    csv_name = 'PRESENCE-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'.csv'
    csv_path = presence_cache_location_prefix+csv_name
    return (csv_name, csv_path)

def detections_to_presence(num_hours, datetime_start, num_intervals_per_hour, bee_ids):
    #TODO: add documentation-style comments


    (csv_name, csv_path) = create_presence_cache_filename(num_hours, datetime_start, num_intervals_per_hour)
    detections_cache_location_prefix = cache_location_prefix + "Detections/"
    #Loading first element before the loop, to have a table formatted nicely for appending
    start_csv_name = "DETECTIONS-"+(datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+detections_cache_location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(detections_cache_location_prefix+start_csv_name, parse_dates=['timestamp'], usecols=['timestamp', 'bee_id'])

    #read and concat a number of hour-long csvs (note: this is because thekla memory crashes if attempting >16h at a time)
    for i in tqdm(range(1, num_hours)):
        csv_name = "DETECTIONS-" + (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
        print('Processing '+csv_name)
        new_data = pd.read_csv(detections_cache_location_prefix+csv_name, parse_dates=['timestamp'], usecols=['timestamp', 'bee_id'])
        detections_df = pd.concat([detections_df, new_data])
        print('Num. rows after appending: '+str(detections_df.shape[0]))

    #interval length is the total observation period divided by total number of intervals
    total_num_intervals = (num_intervals_per_hour*num_hours)
    interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)

    # prepare dataframe with zeros in the shape [bees x total_num_intervals]
    # append bee_ids from the left
    intervals = pd.DataFrame(data=np.zeros([len(bee_ids),total_num_intervals]))
    bee_ids = pd.DataFrame(data={'id': bee_ids})
    presence_df = pd.concat([bee_ids, intervals], axis=1)

    #Iterate over intervals and over detections
    #If a bee from bee_ids is detected within a given interval, mark the cell for that bee and interval with a '1'

    interval_starttime = datetime_start
    # print("Processing intervals: ")
    for interval in tqdm(range(total_num_intervals)):
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

    #Saving the ENCE dataframe, with 1's and 0's for bees present in a given interval
    presence_df.to_csv(csv_path)

    print("SAVED", csv_path)
    return csv_path




def cache_detections_from_database(datetime_start, observ_period, num_observ_periods, detection_confidence_requirement):
    """Pulls detections from the Beesbook database
    and saves them to disk as (e.g.) "DETECTIONS-2016-08-25.csv" file.

    Args:
        datetime_start (datetime): the starting point for observations we want to pull
        observ_period (timedelta):  size of the window we're going to save to disk
        num_observ_periods (int):  how many periods we want to save
    """


    print('Beginning at '+datetime_start.strftime("%Y-%m-%d %H:%M:%S"))

    for i in tqdm(range(0,num_observ_periods)):
        datetime_end = datetime_start + observ_period
        datetime_str = datetime_start.strftime("%Y-%m-%d_%H:%M:%S")
        #If this file has already been saved, we're good, just drop it

        filepath = detections_cache_path+'DETECTIONS-'+datetime_str+'.csv'
        file = Path(filepath)
        if file.exists():
            print("File "+ datetime_str+".csv already exists, dropping")
            datetime_start = datetime_end
            continue

        print('Getting hour #'+str(i)+', beginning at '+datetime_str)
        start = time.time()
        with psycopg2.connect(connect_str) as conn:
            query = """SET geqo_effort to 10;
                        SET max_parallel_workers_per_gather TO 8;
                        SET temp_buffers to "32GB";
                        SET work_mem to "1GB";
                        SET temp_tablespaces to "ssdspace";
                    SELECT * FROM bb_detections_2016_stitched
                   WHERE timestamp >= %s AND
                         timestamp < %s AND
                         bee_id_confidence >= %s
                   ;"""
        df = pd.read_sql_query(
            query, conn,
            params=(datetime_start, datetime_end, detection_confidence_requirement),
            coerce_float=False)

        end = time.time()
        secs_elapsed = end - start

        m, s = divmod(secs_elapsed, 60)
        h, m = divmod(m, 60)
        print('Getting the data took: %d:%02d:%02d'% (h, m, s))

        start = time.time()
        df.to_csv(detections_cache_path+'DETECTIONS-'+datetime_str+'.csv')
        datetime_start = datetime_end

        end = time.time()
        secs_elapsed = end - start

        m, s = divmod(secs_elapsed, 60)
        h, m = divmod(m, 60)
        print('Saving the csv took: %d:%02d:%02d'% (h, m, s))

def cache_death_dates():
    """Pulls alive_bees_2016 from the Beesbook database
    and saves a dataframe with the last date alive for each bee to disk as "Last_day_alive.csv" file.
    """

    print('Loading bee alive states')

    with psycopg2.connect(connect_str) as conn:
        query = """SET geqo_effort to 10;
                    SET max_parallel_workers_per_gather TO 8;
                    SET temp_buffers to "32GB";
                    SET work_mem to "1GB";
                    SET temp_tablespaces to "ssdspace";
                SELECT * FROM alive_bees_2016
               ;"""
    df = pd.read_sql_query(
        query, conn, coerce_float=False)

    df = df.groupby('bee_id')['timestamp'].agg(['max'])
    df.to_csv(detections_cache_path+'Last_day_alive.csv')
    print('Saved last day alive for all bees')

def cache_hatch_dates():
    """Pulls alive_bees_2016 from the Beesbook database
    and saves a dataframe with the first detection date for each bee to disk as "First_day_alive.csv" file.
    """

    print('Loading bee alive states')

    with psycopg2.connect(connect_str) as conn:
        query = """SET geqo_effort to 10;
                    SET max_parallel_workers_per_gather TO 8;
                    SET temp_buffers to "32GB";
                    SET work_mem to "1GB";
                    SET temp_tablespaces to "ssdspace";
                SELECT * FROM alive_bees_2016
               ;"""
    df = pd.read_sql_query(
        query, conn, coerce_float=False)

    df = df.groupby('bee_id')['timestamp'].agg(['min'])
    df.to_csv(detections_cache_path+'First_day_alive.csv')
    print('Saved first day alive for all bees')



def detections_to_presence_locations(num_hours, datetime_start, num_intervals_per_hour, bee_ids):
    #TODO: add documentation-style comments


    (csv_name, csv_path) = create_presence_locations_cache_filename(num_hours, datetime_start, num_intervals_per_hour)
    detections_cache_location_prefix = cache_location_prefix + "Detections/"
    # Load first element before the loop, to have a table formatted nicely for appending
    start_csv_name = "DETECTIONS-"+(datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+detections_cache_location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(detections_cache_location_prefix+start_csv_name,
                                parse_dates=['timestamp'],
                                usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation'])

    # Read and concat a number of hour-long csvs (note: this is because thekla memory crashes if attempting >16h at a time)
    for i in tqdm(range(1, num_hours)):
        csv_name = "DETECTIONS-" + (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
        print('Processing '+csv_name)
        new_data = pd.read_csv(detections_cache_location_prefix+csv_name,
                               parse_dates=['timestamp'],
                               usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation'])

        detections_df = pd.concat([detections_df, new_data])
        print('Num. rows after appending: '+str(detections_df.shape[0]))

    #interval length is the total observation period divided by total number of intervals
    total_num_intervals = (num_intervals_per_hour*num_hours)
    interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)

    # prepare dataframe with zeros in the shape [bees x total_num_intervals]
    # append bee_ids from the left
    intervals = pd.DataFrame(data=np.zeros([len(bee_ids),total_num_intervals]))
    bee_ids = pd.DataFrame(data={'id': bee_ids})
    presence_df = pd.concat([bee_ids, intervals], axis=1)

    #Iterate over intervals and over detections
    #If a bee from bee_ids is detected within a given interval, mark the cell for that bee and interval with a '1'

    interval_starttime = datetime_start
    # print("Processing intervals: ")
    for interval in tqdm(range(total_num_intervals)):
        #choose detections for interval
        interval_endtime = interval_starttime + interval_length
        after_start = detections_df['timestamp'] >= interval_starttime
        before_end = detections_df['timestamp'] < interval_endtime
        interval_detections = detections_df[after_start & before_end].fillna(0)
        bee_row_number = 0
        for bee in presence_df['id']:
            if bee in interval_detections['bee_id'].unique():
                #TODO: currently just taking the coordinate of the last detection in the interval, maybe change to the average of the interval later?
                x_c = interval_detections['x_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                y_c = interval_detections['y_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                #y_c = detections_df.at[bee_row_number, 'y_pos_hive']
                #orientation = detections_df.at[bee_row_number, 'orientation']
                #loc = str(x_c[0])+":"+str(y_c[0])+":"+str(orientation[0])
                #locx = (x_c[0], y_c[0])
                coordinates = (round(x_c), round(y_c))
                presence_df[interval] = presence_df[interval].astype(object)
                presence_df.set_value(bee_row_number, interval, coordinates) #deprecation: change to presence_df.iat[x,y] = z
            bee_row_number += 1
        interval_starttime = interval_endtime

    #Saving the PRESENCE dataframe, with 1's and 0's for bees present in a given interval
    presence_df.to_csv(csv_path)
    print("SAVED", csv_path)
    return csv_path

def detections_to_presence_locations_front(num_hours, datetime_start, num_intervals_per_hour, bee_ids):
    #TODO: add documentation-style comments


    (csv_name, csv_path) = create_presence_locations_cam_cache_filename(num_hours, datetime_start, num_intervals_per_hour, "front/")
    detections_cache_location_prefix = cache_location_prefix + "Detections/"
    # Load first element before the loop, to have a table formatted nicely for appending
    start_csv_name = "DETECTIONS-"+(datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+detections_cache_location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(detections_cache_location_prefix+start_csv_name,
                                parse_dates=['timestamp'],
                                usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation', 'cam_id'])

    # Read and concat a number of hour-long csvs (note: this is because thekla memory crashes if attempting >16h at a time)
    for i in tqdm(range(1, num_hours)):
        csv_name = "DETECTIONS-" + (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
        print('Processing '+csv_name)
        new_data = pd.read_csv(detections_cache_location_prefix+csv_name,
                               parse_dates=['timestamp'],
                               usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation', 'cam_id'])

        detections_df = pd.concat([detections_df, new_data])
        print('Num. rows after appending: '+str(detections_df.shape[0]))

    #interval length is the total observation period divided by total number of intervals
    total_num_intervals = (num_intervals_per_hour*num_hours)
    interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)

    # prepare dataframe with zeros in the shape [bees x total_num_intervals]
    # append bee_ids from the left
    intervals = pd.DataFrame(data=np.zeros([len(bee_ids),total_num_intervals]))
    bee_ids = pd.DataFrame(data={'id': bee_ids})
    presence_df = pd.concat([bee_ids, intervals], axis=1)
    detections_df = detections_df[(detections_df['cam_id']<2)]

    #Iterate over intervals and over detections
    #If a bee from bee_ids is detected within a given interval, mark the cell for that bee and interval with a '1'

    interval_starttime = datetime_start
    # print("Processing intervals: ")
    for interval in tqdm(range(total_num_intervals)):
        #choose detections for interval
        interval_endtime = interval_starttime + interval_length
        after_start = detections_df['timestamp'] >= interval_starttime
        before_end = detections_df['timestamp'] < interval_endtime
        interval_detections = detections_df[after_start & before_end].fillna(0)
        bee_row_number = 0
        for bee in presence_df['id']:
            if bee in interval_detections['bee_id'].unique():
                #TODO: currently just taking the coordinate of the last detection in the interval, maybe change to the average of the interval later?
                x_c = interval_detections['x_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                y_c = interval_detections['y_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                #y_c = detections_df.at[bee_row_number, 'y_pos_hive']
                #orientation = detections_df.at[bee_row_number, 'orientation']
                #loc = str(x_c[0])+":"+str(y_c[0])+":"+str(orientation[0])
                #locx = (x_c[0], y_c[0])
                coordinates = (round(x_c), round(y_c))
                presence_df[interval] = presence_df[interval].astype(object)
                presence_df.set_value(bee_row_number, interval, coordinates)
            bee_row_number += 1
        interval_starttime = interval_endtime

    #Saving the ENCE dataframe, with 1's and 0's for bees present in a given interval
    presence_df.to_csv(csv_path)
    print("SAVED", csv_path)
    return csv_path

def detections_to_presence_locations_back(num_hours, datetime_start, num_intervals_per_hour, bee_ids):
    #TODO: add documentation-style comments

    (csv_name, csv_path) = create_presence_locations_cam_cache_filename(num_hours, datetime_start, num_intervals_per_hour, "back/")
    detections_cache_location_prefix = cache_location_prefix + "Detections/"
    # Load first element before the loop, to have a table formatted nicely for appending
    start_csv_name = "DETECTIONS-"+(datetime_start).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
    print('Processing '+detections_cache_location_prefix+start_csv_name+' before the loop')

    detections_df = pd.read_csv(detections_cache_location_prefix+start_csv_name,
                                parse_dates=['timestamp'],
                                usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation', 'cam_id'])

    # Read and concat a number of hour-long csvs (note: this is because thekla memory crashes if attempting >16h at a time)
    for i in tqdm(range(1, num_hours)):
        csv_name = "DETECTIONS-" + (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+".csv"
        print('Processing '+csv_name)
        new_data = pd.read_csv(detections_cache_location_prefix+csv_name,
                               parse_dates=['timestamp'],
                               usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation', 'cam_id'])

        detections_df = pd.concat([detections_df, new_data])
        print('Num. rows after appending: '+str(detections_df.shape[0]))

    #interval length is the total observation period divided by total number of intervals
    total_num_intervals = (num_intervals_per_hour*num_hours)
    interval_length = timedelta(hours=num_hours) // (num_intervals_per_hour*num_hours)

    # prepare dataframe with zeros in the shape [bees x total_num_intervals]
    # append bee_ids from the left
    intervals = pd.DataFrame(data=np.zeros([len(bee_ids),total_num_intervals]))
    bee_ids = pd.DataFrame(data={'id': bee_ids})
    presence_df = pd.concat([bee_ids, intervals], axis=1)
    detections_df = detections_df[(detections_df['cam_id']>1)]

    #Iterate over intervals and over detections
    #If a bee from bee_ids is detected within a given interval, mark the cell for that bee and interval with a '1'

    interval_starttime = datetime_start
    # print("Processing intervals: ")
    for interval in tqdm(range(total_num_intervals)):
        #choose detections for interval
        interval_endtime = interval_starttime + interval_length
        after_start = detections_df['timestamp'] >= interval_starttime
        before_end = detections_df['timestamp'] < interval_endtime
        interval_detections = detections_df[after_start & before_end].fillna(0)
        bee_row_number = 0
        for bee in presence_df['id']:
            if bee in interval_detections['bee_id'].unique():
                #TODO: currently just taking the coordinate of the last detection in the interval, maybe change to the average of the interval later?
                x_c = interval_detections['x_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                y_c = interval_detections['y_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                #y_c = detections_df.at[bee_row_number, 'y_pos_hive']
                #orientation = detections_df.at[bee_row_number, 'orientation']
                #loc = str(x_c[0])+":"+str(y_c[0])+":"+str(orientation[0])
                #locx = (x_c[0], y_c[0])
                coordinates = (round(x_c), round(y_c))
                presence_df[interval] = presence_df[interval].astype(object)
                presence_df.set_value(bee_row_number, interval, coordinates)
            bee_row_number += 1
        interval_starttime = interval_endtime

    #Saving the ENCE dataframe, with 1's and 0's for bees present in a given interval
    presence_df.to_csv(csv_path)
    print("SAVED", csv_path)
    return csv_path

def last_days_caches(num_hours, num_intervals_per_hour, number_last_days):
    #step 1 loading last alive csv
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    last_day_alive_df = pd.read_csv(last_alive_path,
                               parse_dates=['max'],
                               usecols=['max', 'bee_id'])

    last_day_alive_df = last_day_alive_df.loc[last_day_alive_df['max'] >= datetime(2016, 7, 20+number_last_days)]
    last_day_alive_df.index = last_day_alive_df['bee_id']
    last_days_presence_df = pd.DataFrame()
    last_days_locations_df = pd.DataFrame()
    last_days_locations_front_df = pd.DataFrame()
    last_days_locations_back_df = pd.DataFrame()

    #step 2 traversing through a loop to extract the relevant intervals from each saved cache (traverse over timestamp or bee_id?)
    for ix in tqdm(last_day_alive_df['bee_id']):
        temp_presence_df = pd.DataFrame()
        temp_locations_df = pd.DataFrame()
        temp_locations_front_df = pd.DataFrame()
        temp_locations_back_df = pd.DataFrame()
        for day in range(number_last_days):
            (presence_name, presence_path) = create_presence_cache_filename(num_hours, last_day_alive_df.loc[ix][1].date()-timedelta(days=day+1), num_intervals_per_hour)
            (locations_name, locations_path) = create_presence_locations_cache_filename(num_hours, last_day_alive_df.loc[ix][1].date()-timedelta(days=day+1), num_intervals_per_hour)
            (locations_front_name, locations_front_path) = create_presence_locations_cam_cache_filename(num_hours, last_day_alive_df.loc[ix][1].date()-timedelta(days=day+1), num_intervals_per_hour, "front/")
            (locations_back_name, locations_back_path) = create_presence_locations_cam_cache_filename(num_hours, last_day_alive_df.loc[ix][1].date()-timedelta(days=day+1), num_intervals_per_hour, "back/")

            new_presence_df = pd.read_csv(presence_path)
            new_presence_df = new_presence_df.loc[new_presence_df['id'] == ix]
            new_locations_df = pd.read_csv(locations_path, low_memory=False)
            new_locations_df = new_locations_df.loc[new_locations_df['id'] == ix]
            new_locations_front_df = pd.read_csv(locations_front_path, low_memory=False)
            new_locations_front_df = new_locations_front_df.loc[new_locations_front_df['id'] == ix]
            new_locations_back_df = pd.read_csv(locations_back_path, low_memory=False)
            new_locations_back_df = new_locations_back_df.loc[new_locations_back_df['id'] == ix]

            if temp_presence_df.empty:
                temp_presence_df = new_presence_df.iloc[:,1:]
            else:
                temp_presence_df = temp_presence_df.merge(new_presence_df.iloc[:,1:], on='id', how='left')
                temp_presence_df.columns = range(-1, temp_presence_df.shape[1]-1)
                temp_presence_df.columns = temp_presence_df.columns.map(str)
                temp_presence_df.rename(columns={'-1': 'id'}, inplace=True)

            if temp_locations_df.empty:
                temp_locations_df = new_locations_df.iloc[:,1:]
            else:
                temp_locations_df = temp_locations_df.merge(new_locations_df.iloc[:,1:], on='id', how='left')
                temp_locations_df.columns = range(-1, temp_locations_df.shape[1]-1)
                temp_locations_df.columns = temp_locations_df.columns.map(str)
                temp_locations_df.rename(columns={'-1': 'id'}, inplace=True)

            if temp_locations_front_df.empty:
                temp_locations_front_df = new_locations_front_df.iloc[:,1:]
            else:
                temp_locations_front_df = temp_locations_front_df.merge(new_locations_front_df.iloc[:,1:], on='id', how='left')
                temp_locations_front_df.columns = range(-1, temp_locations_front_df.shape[1]-1)
                temp_locations_front_df.columns = temp_locations_front_df.columns.map(str)
                temp_locations_front_df.rename(columns={'-1': 'id'}, inplace=True)

            if temp_locations_back_df.empty:
                temp_locations_back_df = new_locations_back_df.iloc[:,1:]
            else:
                temp_locations_back_df = temp_locations_back_df.merge(new_locations_back_df.iloc[:,1:], on='id', how='left')
                temp_locations_back_df.columns = range(-1, temp_locations_back_df.shape[1]-1)
                temp_locations_back_df.columns = temp_locations_back_df.columns.map(str)
                temp_locations_back_df.rename(columns={'-1': 'id'}, inplace=True)

        if last_days_presence_df.empty:
            last_days_presence_df = temp_presence_df
        else:
            last_days_presence_df = pd.concat([last_days_presence_df, temp_presence_df])

        if last_days_locations_df.empty:
            last_days_locations_df = temp_locations_df
        else:
            last_days_locations_df = pd.concat([last_days_locations_df, temp_locations_df])

        if last_days_locations_front_df.empty:
            last_days_locations_front_df = temp_locations_front_df
        else:
            last_days_locations_front_df = pd.concat([last_days_locations_front_df, temp_locations_front_df])

        if last_days_locations_back_df.empty:
            last_days_locations_back_df = temp_locations_back_df
        else:
            last_days_locations_back_df = pd.concat([last_days_locations_back_df, temp_locations_back_df])

    print (last_days_presence_df)
    print (last_days_locations_df)
    print (last_days_locations_front_df)
    print (last_days_locations_back_df)

    #step 3 saving the caches
    #NOTE: make sure the paths are correct
    last_days_presence_df.to_csv(cache_location_prefix+'Presence/Janek/last_days_presence.csv')
    last_days_locations_df.to_csv(cache_location_prefix+'Presence/Janek/locations/last_days_locations.csv')
    last_days_locations_front_df.to_csv(cache_location_prefix+'Presence/Janek/locations/cam/front/last_days_locations_front.csv')
    last_days_locations_back_df.to_csv(cache_location_prefix+'Presence/Janek/locations/cam/back/last_days_locations_back.csv')
    print('Saved last day caches for all bees')

def calculate_bee_lifespans_from_hatchdates():
    meta = bb_utils.meta.BeeMetaInfo()
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    last_day_alive_df = pd.read_csv(last_alive_path,
                                    parse_dates=['max'],
                                    usecols=['max', 'bee_id'])

    last_day_alive_df.index = last_day_alive_df['bee_id']
    life_span = pd.DataFrame()
    for ix in last_day_alive_df['bee_id']:
        birthday = meta.get_hatchdate(bb_utils.ids.BeesbookID.from_dec_9(ix)).date()
        temp_life_span = pd.DataFrame([[ix, (last_day_alive_df.loc[ix]['max'].date() - birthday).days]], columns=['id','life_span'])
        life_span = pd.concat([life_span, temp_life_span])
    life_span.index = last_day_alive_df['bee_id']
    life_span = life_span['life_span']
    life_span = filter_out_fake_deaths(life_span)
    return life_span

    #TODO: returns a Series, while other two lifespan functions return a Dateframe
def calculate_bee_lifespans_from_detections():
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    first_alive_path = detections_cache_path+'First_day_alive.csv'

    last_day_alive_df = pd.read_csv(last_alive_path, parse_dates=['max'], usecols=['max', 'bee_id'])
    first_day_alive_df = pd.read_csv(first_alive_path, parse_dates=['min'], usecols=['min'])

    diff = (last_day_alive_df['max'] - first_day_alive_df['min']).dt.days
    diff.index = last_day_alive_df['bee_id']
    diff = filter_out_fake_deaths(diff)
    return diff

def calculate_bee_lifespans_combined():
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    first_alive_path = detections_cache_path+'First_day_alive.csv'

    last_day_alive_df = pd.read_csv(last_alive_path,
                                    parse_dates=['max'],
                                    usecols=['max', 'bee_id'])
    first_day_alive_df = pd.read_csv(first_alive_path,
                                     parse_dates=['min'],
                                     usecols=['min', 'bee_id'])

    last_day_alive_df.index = last_day_alive_df['bee_id']
    first_day_alive_df.index = first_day_alive_df['bee_id']

    meta = bb_utils.meta.BeeMetaInfo()

    lifespan_from_detections = calculate_bee_lifespans_from_detections()

    life_span = pd.DataFrame()
    for ix in last_day_alive_df['bee_id']:
        birthday = meta.get_hatchdate(bb_utils.ids.BeesbookID.from_dec_9(ix)).date()
        if pd.isnull(birthday):
            birthday = first_day_alive_df.loc[ix]['min'].date()
        temp_life_span = pd.DataFrame([[ix, (last_day_alive_df.loc[ix]['max'].date() - birthday).days]], columns=['id','life_span'])
        life_span = pd.concat([life_span, temp_life_span])
    life_span.index = last_day_alive_df['bee_id']
    life_span = life_span['life_span']
    life_span = filter_out_fake_deaths(life_span)
    return life_span




def filter_out_fake_deaths(lifespans):
    '''Filters out bee ids whose last detections landed on the last day of the experiment,
    because they shouldn't be interpreted as deaths.'''
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    last_day_alive_df = pd.read_csv(last_alive_path,
                                    parse_dates=['max'],
                                    usecols=['max', 'bee_id'])

    last_date = last_day_alive_df['max'].max()
    bees_with_fake_deaths = last_day_alive_df['bee_id'].drop(last_day_alive_df[last_day_alive_df['max'] != last_date].index)
    return lifespans.drop(bees_with_fake_deaths)
