import os
os.getcwd()

import pandas as pd
import bb_utils

dance_events = pd.read_csv(os.getcwd()+"/datasets/foragergroups/full_data_marie23.csv", index_col=0) #751 x 28/29
dance_events = dance_events[dance_events.following == True]
print(list(dance_events.columns))


dance_events.shape

# Get a list of dancers and recruits along with the date of the dance


dancers = dance_events[['dancer','video_date']]
dancers = dancers.dropna()
dancers['role'] = 'dancer'
dancers.rename(columns = {'dancer' : 'bee_id'}, inplace=True) 


# In[166]:


recruits = dance_events[['recruit','video_date']]
recruits = recruits.dropna()
recruits['role'] = 'recruit'
recruits.rename(columns = {'recruit' : 'bee_id'}, inplace=True)


# In[151]:


foragers = dancers.append(recruits, sort=True)
foragers = foragers.drop_duplicates()
foragers.bee_id = foragers.bee_id.astype(int)
foragers.bee_id = foragers.bee_id.apply(lambda ID: bb_utils.ids.BeesbookID.from_dec_12(ID).as_ferwar())


# In[167]:


foragers

# Future work: (nullified if we only get 13 bees from this anyway)
# compare dancers and followers against each other,
# maybe see if the length of the dance makes a difference?
# what other features of this could be meaningful?
