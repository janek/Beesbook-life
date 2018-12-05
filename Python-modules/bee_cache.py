import pandas as pd
from enum import Enum

class CacheType(Enum):
    other = "Other"
    detections = "Detections"
    presence = "Presence"
    trips = "Trips"

class CacheFormat(Enum):
    csv = "csv"
    pickle = "pkl"
    hdf = "h5"


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
        path = self.make_path(filename, type=type, format=format)

        if format == CacheFormat.pickle:
            df = pd.read_pickle(path)
        elif format == CacheFormat.csv:
            df = pd.read_csv(path)
        elif format == CacheFormat.hdf:
            df = pd.read_hdf(path)

        # TODO: why isn't this executed in new_presence?
        print('loading with type ' + str(type))
        if type == CacheType.presence:
            print("dropping")
            df.index.rename('bee_id', inplace = True)
            df.drop(columns=['Unnamed: 0', 'id'], inplace = True)

        return df
