# In: []
import os
print(os.getcwd())

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
from datetime import timedelta, datetime
import sys

sys.path.append(os.getcwd()+'/Beesbook-life/Python-modules/') #For bee_helpers and file_helpers
# sys.path.append('/home/mi/rrszynka/mnt/janek/Beesbook-life/Python-modules/')
from bee_helpers import calc_trip_lengths, calc_trip_starts, get_forager_bee_ids, get_random_bee_ids, get_all_bee_ids
from file_helpers import cache_location_prefix, detections_to_presence, detections_to_presence_locations, create_presence_cache_filename, create_presence_locations_cache_filename, create_presence_cache_filename, cache_location_prefix, create_presence_locations_cam_cache_filename


from pathlib import Path
from tqdm import tqdm

#%

datetime_start = datetime(2016, 7, 20) #TODO: set beginning date as default param in file helpers
num_days_to_process = 60
num_intervals_per_hour = 60 #TODO: if considered
num_hours = 24 #TODO: set as default param in file helpers


presence_dfs = []


for i in tqdm(range(0, num_days_to_process)):
    start_day = datetime_start+timedelta(days=i)
    (csv_name, csv_path) = create_presence_cache_filename(num_hours, start_day, num_intervals_per_hour)
    file = Path(csv_path)
    if file.exists() == False:
        print(csv_path+ " doesn't exist")
    else:
        new_presence_df = pd.read_csv(csv_path).iloc[:,1:]
        new_presence_df = new_presence_df.drop(columns='id')
        presence_dfs.append(new_presence_df)
        # print("Adding df #"+str(i)+", "+csv_name)


presence_df = pd.concat(presence_dfs, axis=1)
presence_df.index.rename('bee_id', inplace=True)

# Saving and loading cache (should not normally be needed, as it seems to work faster to use the code above)
# presence_df.to_csv('../../caches/Presence/COMBINED_PRESENCE_59d_24h_from_07-19.csv')
# presence_df = pd.read_csv('../../caches/Presence/COMBINED_PRESENCE_59d_24h_from_07-19.csv', index_col='bee_id')



presence_df.head()
sum_pres_by_bee = presence_df.sum(axis=1)
sum_pres_by_bee = sum_pres_by_bee.to_frame()
sum_pres_by_bee.columns = ['presence_score_total']

lives_from_detections_df = pd.read_csv(os.getcwd()+'/caches/Other/lives_from_detections_df.csv', index_col='bee_id', parse_dates=['min', 'max'])


sum_pres_by_bee.head()


lives_from_detections_df.head()



presence_with_lifespan = sum_pres_by_bee.join(lives_from_detections_df, how='outer')
presence_with_lifespan['presence_coefficient'] = presence_with_lifespan.presence_score_total/(presence_with_lifespan.lifespan*1440)
presence_with_lifespan_fil = presence_with_lifespan.dropna()
presence_with_lifespan_work = presence_with_lifespan_fil[presence_with_lifespan_fil.lifespan > 0]

%matplotlib inline

preshist = (presence_with_lifespan_work[presence_with_lifespan_work.presence_coefficient > 0.03]).presence_coefficient
title = 'Distribution of presence_coefficient values among ' + str(len(preshist)) + ' bees. \n(a value of 1.0 would mean 100% presence in the hive)'
plt.subplots(figsize=(20,8))
ax = sns.distplot(preshist, bins=100, kde=False)
ax.set(title=title)




presence_with_lifespan_work.head()


pres_by_minute = presence_df.sum(axis='rows')


# In[62]:

#convert from intervals (minutes) to hours

pres_by_hour = []
for i in np.arange(0, 24*59): #24hours * 59 days
    newHour = pres_by_minute[i*60:(i+1)*60].sum()
    pres_by_hour.append(newHour)

pres_by_hour = pd.DataFrame(pres_by_hour, columns=['presence'])


#%

daily_presences = []
presence_from_morning = presence_df.iloc[:,7*60:]

for i in np.arange(0, 59): #59 days
    begin = i*60*24
    end = begin+60*12
    day = presence_from_morning.iloc[:,begin:end]
    daily_presences.append(day.sum(axis=1))



#%
presence_with_lifespan_long_lives = presence_with_lifespan_work[presence_with_lifespan_work['lifespan'] > 15]
presence_with_lifespan_long_lives.shape

daily_presences = pd.concat(daily_presences, axis=1)
daily_presences = daily_presences/(12*60)
daily_presences = daily_presences.loc[presence_with_lifespan_long_lives.index]

#%
pres_by_ages = daily_presences*0 #create a DataFrame with the same shape and labels, but empty
pres_by_ages.shape
day_0 = datetime(2016, 7, 19)

daily_presences

for day in tqdm(pres_by_ages.columns):
    for bee in pres_by_ages.index: #of a bee
        bee_birth_date = presence_with_lifespan_work.loc[bee]['min']
        if presence_with_lifespan_work.loc[bee]['lifespan'] < day:
            pres_by_ages.loc[bee, day] = np.nan
        else:
            bee_life_day = bee_birth_date+timedelta(day)
            experiment_day = (bee_life_day - day_0).days
            if experiment_day > 58:
                continue
            pres_by_ages.loc[bee, day] = daily_presences.loc[bee, experiment_day]


pres_by_ages_per_bee = pres_by_ages.sum()/(pres_by_ages.isnull() == False).sum()
sns.lineplot(data=pres_by_ages_per_bee)



sns.lineplot(data=pres_by_ages.iloc[22])
# In[ ]:



foragers_from_groups = pd.read_pickle(os.getcwd()+'/caches/Other/foragers_from_groups.pkl').drop(columns=['bee_id'])

forager_lives = pd.merge(lives_from_detections_df, foragers_from_groups, how='inner', on='bee_id')


forager_lives.rename(columns={'min':'born', 'max':'died', 'date': 'foraging_min_date'}, inplace=True)
forager_lives_short = forager_lives[~forager_lives.index.duplicated()]


foraging_max_date = forager_lives[~forager_lives.index.duplicated(keep='last')].foraging_min_date.rename('foraging_max_date')
forager_lives_short = pd.merge(forager_lives_short, pd.DataFrame(foraging_max_date), how='inner', on='bee_id')
forager_lives_short = forager_lives_short.drop(columns=["group_id", "location"])

forager_lives_short['foraging_min_age'] = (forager_lives_short.foraging_min_date - forager_lives_short.born)
forager_lives_short['foraging_max_age'] = (forager_lives_short.foraging_max_date - forager_lives_short.born)

forager_lives_short.head()

sns.lineplot(data=pres_by_ages.loc[199])

# bee_life_day = bee_birth_day+timedelta(day)
# bee_birth_day = presence_with_lifespan_work.loc[4]['min']
# bee_birth_day
# # In[85]:
#
# day_0
# (bee_birth_day - day_0).days




(pres_by_ages.isna().sum(axis=0)/pres_by_ages.shape[0]).head()




daily_presences.shape




# In[252]:




# In[ ]:



fig, ax = plt.subplots()
fig.set_size_inches(30,10)
pres_by_hour.index.name = 'hour'
pres_by_hour['hour'] = pres_by_hour.index
sns.barplot(x='hour', y='presence', data=pres_by_hour[:240], ax=ax)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:


sum_pres_by_bee = pd.DataFrame(sum_pres_by_bee, columns=["presence_score_total"])


# In[72]:


sum_pres_by_bee.max()


# In[60]:


spbdf = sum_pres_by_bee.loc[(sum_pres_by_bee!=0).any(1)]


# In[69]:


spbdf[spbdf.presence_score_total<50].hist(bins=50, figsize=(30,15))


# In[37]:





# In[38]:


sum_pres_filtered


# In[ ]:
