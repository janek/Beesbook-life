import os
print(os.getcwd())
import os, shutil
import bb_utils
import bb_utils.meta
import bb_utils.ids
import bb_backend
# from datetime import timedelta
import datetime
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
cache_location_prefix = "/home/mi/rrszynka/mnt/janek/"+"caches/"
detections_cache_path = cache_location_prefix + "Detections/"


def cache_detections_from_database(datetime_start, observ_period, num_observ_periods, detection_confidence_requirement):
    """Pulls detections from the Beesbook database
    and saves them to disk as (e.g.) "DETECTIONS-2016-08-25_conf_07.csv" file.

    Args:
        datetime_start (datetime): the starting point for observations we want to pull
        observ_period (timedelta):  size of the window we're going to save to disk
        num_observ_periods (int):  how many periods we want to save
        detection_confidence_requirement (float): how high the database value for detection confidence needs to be
    """


    print('Beginning at ' + datetime_start.strftime("%Y-%m-%d %H:%M:%S"))
    print('Saving to ' + detections_cache_path)

    for i in tqdm(range(0,num_observ_periods)):
        datetime_end = datetime_start + observ_period
        datetime_str = datetime_start.strftime("%Y-%m-%d_%H:%M:%S")
        #If this file has already been saved, we're good, just drop it

        conf_string = str(detection_confidence_requirement).replace('.','')
        filename = 'DETECTIONS-'+datetime_str+'_conf_'+conf_string+'.csv'
        filepath = detections_cache_path+filename
        file = Path(filepath)
        if file.exists():
            print("File " + filename + " already exists, dropping")
            datetime_start = datetime_end
            continue
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

        df.to_csv(filepath)
        datetime_start = datetime_end

def create_presence_cache_filename(num_hours,
                                   datetime_start,
                                   num_intervals_per_hour,
                                   cams=[1,2,3,4],
                                   method='binary',
                                   detection_confidence_requirement=0):

    presence_cache_location_prefix = cache_location_prefix + "Presence/"

    date_string = (datetime_start).strftime("%Y-%m-%d_%H")
    conf_string = str(detection_confidence_requirement).replace('.','')
    cams_string = ''.join(str(x) for x in cams)
    csv_name = 'PRESENCE-'+method+'-'+str(date_string)+"_num_hours_"+str(num_hours)+"_int_size_"+str(num_intervals_per_hour)+'_conf_'+conf_string+'_cams_'+cams_string+'.csv'
    csv_path = presence_cache_location_prefix+csv_name
    return (csv_name, csv_path)

def detections_to_presence(num_hours, datetime_start, num_intervals_per_hour, bee_ids, cams=[0,1,2,3], method='binary', detection_confidence_requirement=0, return_mode='path'):
    """Reads a number of DETECTION csvs, combines them into one and converts to a measurement of presence guided by the specified method
       and filtered by specified cam numbers. Saves the PRESENCE cache and returns the path to the saved file.

    Output: A PRESENCE dataframe (csv file), of size [bee_ids x total_num_intervals]. Contents depend on method (see below in Args).

    Args:
        num_hours(int): number of hours to be processed, i.e. number of hour-long DETECTION csv files to be loaded and operated on
        datetime_start (datetime): the starting point of the observations we want to pull
        num_intervals_per_hour (int):  number of intervals per hour. e.g. a value 120 means that one interval covers 30secs of real time
        bee_ids ([int]):  list of bee ids to be taken into account
        cams ([int]): list of desired cams; all cams = [0,1,2,3]; front cams = [0,1]; back cams = [2,3]
        method (string): 'binary' will return 0 and 1, 1 if the given bee was detected at least once in the given interal
                         'counts' will return a value from 0 to MAX, representing how many times the bee was detected during the given interval
        detection_confidence_requirement (float): how high the database value for detection confidence needs to be for this function to include that detection
    """

    if method != 'binary' and method != 'counts' and method != 'last-location':
        print('Please specify either binary, counts or last-location as method.')
        return None

    # 1. Prepare paths and filenames
    (csv_name, csv_path) = create_presence_cache_filename(num_hours,
                                        datetime_start,
                                        num_intervals_per_hour,
                                        cams=cams,
                                        method=method,
                                        detection_confidence_requirement=detection_confidence_requirement)

    detections_cache_location_prefix = cache_location_prefix + "Detections/"
    conf_string = str(detection_confidence_requirement).replace('.','')

    # 2.Read and concat a given number of hour-long csvs (note: this is done hour-by-hour because thekla memory crashes if attempting >16h at a time)
    detections_dfs = []
    for i in tqdm(range(0, num_hours)):
        csv_name = "DETECTIONS-" + (datetime_start + timedelta(hours=i)).strftime("%Y-%m-%d_%H:%M:%S")+'_conf_'+conf_string+'.csv'
        detections_1h = pd.read_csv(detections_cache_location_prefix+csv_name,
                                    parse_dates=['timestamp'],
                                    usecols=['timestamp', 'bee_id', 'x_pos_hive', 'y_pos_hive', 'orientation', 'cam_id'])
        # 2a. Filter detections to only come from desired cams
        detections_1h = detections_1h[detections_1h.cam_id.isin(cams)]
        detections_dfs.append(detections_1h)
    detections_df = pd.concat(detections_dfs)
    print('Num. rows after concatenating: '+str(detections_df.shape[0]))

    #3. Prepare a zeroes dataframe with presence intervals, to be filled up by information from detections_df
    # prepare shape [num_bees x num_intervals]
    presence_df = pd.DataFrame(data=np.zeros([len(bee_ids),(num_intervals_per_hour*num_hours)]))
    presence_df.index = bee_ids

    # 4. Iterate over intervals and over detections to fill up infotmation
    # using user's chosen method (binary/counts/last-location)
    total_num_intervals = num_intervals_per_hour*num_hours
    interval_length = timedelta(hours=num_hours) // total_num_intervals
    interval_starttime = datetime_start

    for interval in tqdm(range(total_num_intervals)):
        #choose detections for interval
        interval_endtime = interval_starttime + interval_length
        after_start = detections_df['timestamp'] >= interval_starttime
        before_end = detections_df['timestamp'] < interval_endtime
        interval_detections = detections_df[after_start & before_end].fillna(0)

        if method == 'binary':
            bee_row_number = 0
            for bee in presence_df['id']:
                if bee in interval_detections['bee_id'].unique():
                    presence_df.set_value(bee_row_number, interval, 1)
                bee_row_number += 1

        elif method == 'last-location':
            bee_row_number = 0
            for bee in presence_df['id']:
                if bee in interval_detections['bee_id'].unique():
                    #TODO: currently just taking the coordinate of the last detection in the interval, maybe change to the average of the interval later?
                    x_c = interval_detections['x_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                    y_c = interval_detections['y_pos_hive'][(interval_detections['bee_id'] == bee)].tail(1).values.item()
                    coordinates = (round(x_c), round(y_c))
                    presence_df[interval] = presence_df[interval].astype(object) # Generalize type of the cells to handle (x,y) coordinate tuples
                    presence_df.set_value(bee_row_number, interval, coordinates) # Fill in the cell
                bee_row_number += 1

        elif method == 'counts':
            counts = interval_detections['bee_id'].value_counts()
            keys = counts.keys().tolist()
            counts = counts.tolist()

            for i in np.arange(0,len(counts)):
                bee = keys[i]
                # If the bee id had some detections, but wasn't among the bees marked as alive for that day, we ignore it
                if bee in bee_ids:
                    presence_df.at[bee, interval] = counts[i]

        interval_starttime = interval_endtime

    presence_df.to_csv(csv_path)
    print("SAVED", csv_path)
    if return_mode == 'path':
        return csv_path
    elif return_mode == 'data':
        return presence_df


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

def cache_first_detection_dates():
    """Pulls alive_bees_2016 from the Beesbook database
    and saves a dataframe with the first detection date for each bee to disk as "First_day_alive.csv" file.
    WARNING: these are not the bees' birthdays - they might have hatched before the video recordings started.
    Only meta.get_hatchdate is a reliable way of finding birthdays.
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
    """
    Uses the Last_day_alive.csv cache and the get_hatchdate functions from bb_utils
    to calculate the lifespan (length-of-life) in days for each bee. The lifespan will be NaN if hatchdate is NaT.

    """
    meta = bb_utils.meta.BeeMetaInfo()
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    last_day_alive_df = pd.read_csv(last_alive_path,
                                    parse_dates=['max'],
                                    usecols=['max', 'bee_id'])

    last_day_alive_df.index = last_day_alive_df['bee_id']
    lifespan = pd.DataFrame()
    for ix in last_day_alive_df['bee_id']:
        birthday = meta.get_hatchdate(bb_utils.ids.BeesbookID.from_dec_9(ix)).date()
        temp_lifespan = pd.DataFrame([[ix, (last_day_alive_df.loc[ix]['max'].date() - birthday).days]], columns=['id','lifespan'])
        lifespan = pd.concat([lifespan, temp_lifespan])
    lifespan.index = last_day_alive_df['bee_id']
    lifespan = lifespan['lifespan']
    lifespan = filter_out_fake_deaths(lifespan)
    return lifespan

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

    lifespan = pd.DataFrame()
    for ix in last_day_alive_df['bee_id']:
        birthday = meta.get_hatchdate(bb_utils.ids.BeesbookID.from_dec_9(ix)).date()
        if pd.isnull(birthday):
            birthday = first_day_alive_df.loc[ix]['min'].date()
        temp_lifespan = pd.DataFrame([[ix, (last_day_alive_df.loc[ix]['max'].date() - birthday).days]], columns=['id','lifespan'])
        lifespan = pd.concat([lifespan, temp_lifespan])
    lifespan.index = last_day_alive_df['bee_id']
    lifespan = lifespan['lifespan']
    lifespan = filter_out_fake_deaths(lifespan)
    return lifespan

def filter_out_fake_deaths(lifespans):
    """Takes a lifespans dataframe and filters out bee ids
    whose last detections landed on the last day of the experiment,
    because they shouldn't be interpreted as deaths."""
    last_alive_path = detections_cache_path+'Last_day_alive.csv'
    last_day_alive_df = pd.read_csv(last_alive_path,
                                    parse_dates=['max'],
                                    usecols=['max', 'bee_id'])

    last_date = last_day_alive_df['max'].max()
    bees_with_fake_deaths = last_day_alive_df['bee_id'].drop(last_day_alive_df[last_day_alive_df['max'] != last_date].index)
    return lifespans.drop(bees_with_fake_deaths)
