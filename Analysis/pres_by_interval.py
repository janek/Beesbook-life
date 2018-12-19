 %%
import os
if "rrszynka" not in os.getcwd():
    raise Exception("Working locally - is this desired?")
import pandas as pd
import seaborn as sns; sns.set()
import datetime
import matplotlib.pyplot as plt
import sys
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids, get_alive_bees_for_day
import bb_utils
# %%



day = datetime.date(2016,8,9)

# Currently, when loading a Presence cache, rename and drop need to be executed to keep the dataframe tidy.
# This should be alleviated by improving saving and/or doing the cleanup in the Cache class
presence = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_07', type=CacheType.presence, format=CacheFormat.csv)
presence.index.rename('bee_id', inplace = True)
presence.drop(columns=['bee_id'], inplace = True)



foragers = c.load('foragers_from_groups')
foragers['date'] = foragers['date'].dt.date
foragers_for_day = foragers[foragers['date'] == day].index


# presence['was_foraging'] = False
# presence['was_foraging'][foragers_for_day] = True


day

isinstance(day, datetime.date)
isinstance(datetime.date, day)

bees_alive_for_day = get_alive_bees_for_day(day)['bee_id'].values
presence_alive = presence.loc[bees_alive_for_day]
bees_alive_for_day
presence_alive.head()



timeseries_df = presence_alive.sample(1).T
timeseries_df.head(100)


presence_alive.sum(axis=1).hist(bins=30)

    timeseries_df['interval'] = timeseries_df.index

timeseries_df
timeseries_df = pd.DataFrame(timeseries_df, dtype=float)

timeseries_df.shape
timeseries_df.iloc[:20]
sns.set(rc={'figure.figsize':(25,10)})
sns.lineplot(data=timeseries_df[:20])
sns.scatterplot(data=timeseries_df[:50])
