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

# bb_backend.api.server_adress = 'localhost:8000'
connect_str = """dbname='beesbook' user='reader' host='tonic.imp.fu-berlin.de' 
                 password='' application_name='mehmed'"""
detection_confidence_requirement = 0.99 #note: 0.99 is pretty high

cache_location_prefix = "/mnt/storage/janek/caches/"
detections_cache_path = cache_location_prefix + "Detections/"

def delete_detection_caches_for_date(date_string, directory=detections_cache_path):
    ### date_string must be in MM-DD_hh:mm:ss format
    name_prefix = "DETECTIONS-2016-"
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


def get_detections_from_database(datetime_start, observ_period, num_observ_periods):
    print('Beginning at '+datetime_start.strftime("%Y-%m-%d %H:%M:%S"))

    for i in tqdm(range(0,num_observ_periods)):
        datetime_end = datetime_start + observ_period
        datetime_str = datetime_start.strftime("%Y-%m-%d_%H:%M:%S")

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