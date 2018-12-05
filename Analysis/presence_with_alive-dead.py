# %%
import os
if "rrszynka" not in os.getcwd():
    raise Exception("Working locally - is this desired?")
import psycopg2
import pandas as pd
import seaborn as sns; sns.set_style("whitegrid", {"axes.facecolor": ".9"})
import datetime
import sys
import matplotlib.pyplot as plt
sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
from bee_helpers import calc_trip_lengths, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids#, get_alive_bees_for_day
import bb_utils
# %%


day = datetime.date(2016,8,9)

alive_for_day = get_alive_bees_for_day(day)
hatchdates = c.load('hatchdates')
presence = c.load('PRESENCE-counts-2016-08-09_00_num_hours_24_int_size_120_conf_07', type=CacheType.presence, format=CacheFormat.csv)
# Necessary until corrections are made to loading csvs
presence.index.rename('bee_id', inplace = True)
presence.drop(columns=['bee_id'], inplace = True)




pres_sum = sum_presence_per_day(presence, alive_for_day)

pres_sum['hatchdate'] = hatchdates['hatchdate']
pres_sum['age'] = day - hatchdates['hatchdate']


pres_sum['age'].min()
pres_sum.fillna(0, inplace = True)
pres_sum.age[pres_sum.age < datetime.timedelta(days=0)] = datetime.timedelta(days=0)
pres_sum['age_int'] = pres_sum.age.dt.days


foragers = c.load('foragers_from_groups')
foragers['date'] = foragers['date'].dt.date

foragers_for_day = foragers[foragers['date'] == day].index


pres_sum['was_not_foraging'] = True
pres_sum['was_not_foraging'][foragers_for_day] = False

pres_sum_alive = pres_sum.loc[alive_for_day['bee_id'].values]

plot_by_conf(pres_sum_alive, 0.7)

def plot_by_conf(presence_summed, confidence):
    presence_summed['bee_id'] = presence_summed.index
    sns.set(rc={'figure.figsize':(25,10)})
    title = 'Sum of presence points in a day for all 4096 ids, with det. confidence ' + str(confidence)
    ax = sns.scatterplot(x="bee_id", y='pres_score', style='determined_alive',  hue="age_int", size="was_not_foraging", data=presence_summed).set_title(title)
    # ax.axes.set_ylim(0,100000)
    # ax.axes.set_xlim(0,4100)
    presence_summed.drop(columns=['bee_id'], inplace=True)


def sum_presence_per_day(presence_df, alive_df):
    pres_pts_summed = pd.DataFrame(presence_df.sum(axis=1))
    pres_pts_summed.rename(columns={0:'pres_score'}, inplace = True)
    pres_pts_summed['determined_alive'] = False
    pd.options.mode.chained_assignment = None
    pres_pts_summed.determined_alive[alive_df.bee_id.values] = True
    return pres_pts_summed
