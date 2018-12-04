# %%
import os
print(os.getcwd())
import psycopg2
import pandas as pd
import seaborn as sns; sns.set()
import datetime
import sys
import matplotlib.pyplot as plt
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat
# %%

connect_str = """dbname='beesbook' user='reader' host='tonic.imp.fu-berlin.de' password='' application_name='mehmed'"""

with psycopg2.connect(connect_str) as conn:
    query = """SET geqo_effort to 10;
                SET max_parallel_workers_per_gather TO 8;
                SET temp_buffers to "32GB";
                SET work_mem to "1GB";
                SET temp_tablespaces to "ssdspace";
            SELECT * FROM alive_bees_2016
           ;"""
alive_bees_2016 = pd.read_sql_query(
    query, conn,
    coerce_float=False)

c = Cache()

c.save(alive_bees_2016, 'alive_bees_2016')
alive_bees_2016.head()

alive_7_25_2016 = df[df.timestamp == datetime.date(2016,7,25)]

alive_7_25_2016

c = Cache()
df = c.load('PRESENCE-counts-2016-07-25_00_num_hours_24_int_size_120_conf_099', type=CacheType.presence, format=CacheFormat.csv)
df.index.rename('bee_id', inplace=True)
df = df.drop(columns=['id', 'Unnamed: 0'])




pres_pts_per_day = pd.DataFrame(df.sum(axis=1))

pres_pts_per_day.rename(columns={0:'pres_score'}, inplace = True)

pres_pts_per_day['bee_id'] = pres_pts_per_day.index

pres_pts_per_day['determined_alive'] = False

pd.options.mode.chained_assignment = None

pres_pts_per_day.determined_alive[alive_7_25_2016.bee_id.values] = True

pres_pts_per_day.head()

# fig = plt.figure(figsize=(30,15));
sns.set(rc={'figure.figsize':(25,10)});
sns.scatterplot(x="bee_id", y='pres_score', hue='determined_alive', data=pres_pts_per_day)
