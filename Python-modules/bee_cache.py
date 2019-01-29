import pandas as pd
from enum import Enum
import os; import sys; sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules')
from file_helpers import create_presence_cache_filename
import datetime
from pathlib import Path

#%%
class CacheType(Enum):
    other = "Other"
    detections = "Detections"
    presence = "Presence"
    trips = "Trips"

class CacheFormat(Enum):
    csv = "csv"
    pickle = "pkl"
    hdf = "h5"

class PresenceCacheType(Enum):
    binary = "binary"
    counts = "counts"
    last_location = "last_location"


class Cache:
    def __init__(self, location = "/home/mi/rrszynka/mnt/janek/caches/"):
        self.cache_location_prefix = location

    def make_path(self, filename, type=CacheType.other, format=CacheFormat.pickle):
        return self.cache_location_prefix + type.value + "/" + filename + '.' + format.value

    def save(self, dataframe, filename, type=CacheType.other, format=CacheFormat.pickle):
        path = self.make_path(filename, type=type, format=format)

        if format == CacheFormat.pickle:
            dataframe.to_pickle(path)
        elif format == CacheFormat.csv:
            dataframe.to_csv(path)
        elif format == CacheFormat.hdf:
            dataframe.to_hdf(path, filename)

    def load(self, filename, type=CacheType.other, format=CacheFormat.pickle):
        # Clean format suffixes if they were contained in the string
        filename = filename.split('.', 1)[0]
        path = self.make_path(filename, type=type, format=format)


        df = pd.DataFrame()

        if format == CacheFormat.pickle:
            df = pd.read_pickle(path)
        elif format == CacheFormat.csv:
            if type == CacheType.detections:
                df = pd.read_csv(path, parse_dates=['timestamp'])
            else:
                df = pd.read_csv(path)
            if 'Unnamed: 0' in df.columns: #TODO: test and make sure this runs
                df.index = df['Unnamed: 0']
                df.drop(columns=['Unnamed: 0'], inplace=True)
            if 'id' in df.columns:
                print('reindexing to id, droppping id as a col')
                df.index = df.id
                df.drop(columns=['id'])
        elif format == CacheFormat.hdf:
            df = pd.read_hdf(path)

        return df

    def load_presence_for_date(self, date, detection_confidence_requirement=0.99):
        (csv_name, csv_path) = create_presence_cache_filename(date, method='counts', detection_confidence_requirement=0.99, cams=[0,1,2,3])
        presence_df = self.load(csv_name, type=CacheType.presence, format=CacheFormat.csv)
        return presence_df

    def load_all_presence_caches(self, detection_confidence_requirement=0.99):
        experiment_start_date = datetime.date(2016,7,20)
        experiment_end_date = datetime.date(2016,9,19)
        experiment_length = (experiment_end_date - experiment_start_date).days

        presences = []
        for i in range(experiment_length):
            date = experiment_start_date + datetime.timedelta(days=i)
            # Go through all days, note down which are missing, report that. Combine the rest into a list of presences.
            (csv_name, csv_path) = create_presence_cache_filename(date, method='counts', detection_confidence_requirement=detection_confidence_requirement, cams=[0,1,2,3])

            file = Path(csv_path)
            if file.exists():
                presences.append((date, self.load_presence_for_date(date)))

        print("Collected " + str(len(presences)) + "/" + str(experiment_length)+ " presence caches (all that are currently downloaded)." )
        return presences

#%%




c = Cache()
a = c.load_all_presence_caches()

#%%
for x in a:
    print(x[0], x[1].sum().sum())

#%%
experiment_start_date = datetime.date(2016,7,20)
experiment_end_date = datetime.date(2016,9,19)
experiment_length = (experiment_end_date - experiment_start_date).days
experiment_length

### SCRATCHPAD for testing this class etc
# c = Cache()
# a = c.load_all_presence_caches()
# c.load_presence_for_date(datetime.date(2016,7,20))

# /home/mi/rrszynka/mnt/janek/caches/Presence/PRESENCE-counts-2016-07-20_00_num_hours_24_int_size_120_conf_099_cams_1234.csv' does not exist

# /home/mi/rrszynka/mnt/janek/caches/Presence/PRESENCE-counts-2016-07-20_00_num_hours_24_int_size_120_conf_099_cams_0123.csv



# c.load('PRESENCE-counts-2016-07-20_00_num_hours_24_int_size_120_conf_099_cams_0123', type=CacheType.presence, format=CacheType.csv)
