#!/usr/bin/env python
# coding: utf-8

# In[143]:


import pandas as pd
import numpy as np


# In[150]:


import bb_utils
import bb_utils.meta
from bb_utils.ids import BeesbookID


# In[164]:


dance_events = pd.read_csv("../../datasets/foragergroups/full_data_marie23.csv", index_col=0) #751 x 28/29
dance_events = dance_events[dance_events.following == True]
print(list(dance_events.columns))


# ### Get a list of dancers and recruits along with the date of the dance

# In[165]:


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


# In[ ]:


# Future work: (nullified if we only get 13 bees from this anyway)
# compare dancers and followers agains each other,
# maybe see if the length of the dance makes a difference?
# what other features of this could be meaningful?

