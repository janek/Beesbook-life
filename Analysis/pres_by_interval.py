# %%
import os
if "rrszynka" not in os.getcwd():
    raise Exception("Working locally - is this desired?")
import psycopg2
import pandas as pd
import seaborn as sns; sns.set()
import datetime
import matplotlib.pyplot as plt
import sys
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids#, get_alive_bees_for_day
import bb_utils
# %%



day = datetime.date(2016,8,9)
presence = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_07', type=CacheType.presence, format=CacheFormat.csv)
# Necessary until corrections are made to loading csvs in bee_cache
presence.index.rename('bee_id', inplace = True)
presence.drop(columns=['bee_id'], inplace = True)

foragers = c.load('foragers_from_groups')
foragers['date'] = foragers['date'].dt.date

foragers_for_day = foragers[foragers['date'] == day].index


# presence['was_foraging'] = False
# presence['was_foraging'][foragers_for_day] = True

# %%

fmri = sns.load_dataset("fmri")


fmri.head()
# %%


def get_alive_bees_for_day(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    if isinstance(date, datetime.date) == False:
        raise TypeError('Date must be in a datetime or datetime.date format!')
    df = c.load('alive_bees_2016')
    df = df[df.timestamp == date]
    return df

bees_alive_for_day = get_alive_bees_for_day(day)['bee_id'].values
presence_alive = presence.loc[bees_alive_for_day]

presence_alive.head()



timeseries_df = presence_alive.sample(1).T
timeseries_df.head()

type(timeseries_df[1829][0])

timeseries_df['interval'] = timeseries_df.index

timeseries_df
timeseries_df = pd.DataFrame(timeseries_df, dtype=float)


timeseries_df.iloc[:50]
sns.set(rc={'figure.figsize':(25,10)})
sns.lineplot(data=timeseries_df[:2880])
