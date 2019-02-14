import pandas as pd
import h5py
import matplotlib.pyplot as plt


filename = '/home/mi/rrszynka/mnt/janek/caches/Other/with_coordinates.hdf5'
f = h5py.File(filename, 'r')

a_group_key = list(f.keys())[0]
trip_locations = pd.read_hdf(filename,a_group_key)

trip_locations.head()
trips_side_a = trip_locations[trip_locations.hive_side == 0]
trips_side_b = trip_locations[trip_locations.hive_side == 1]


trips_side_a


plt.figure(figsize=(30,20))
plt.scatter(trips_side_a.x, trips_side_a.y)
