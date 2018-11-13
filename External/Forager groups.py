#!/usr/bin/env python
# coding: utf-8

# In[3]:


import bb_utils
import bb_utils.meta
from bb_utils.ids import BeesbookID
import bb_backend
import numpy as np
import pandas as pd 


# In[4]:


connect_str = """dbname='beesbook' 
                 user='reader' 
                 host='tonic.imp.fu-berlin.de' 
                 password='' 
                 application_name='sammelgruppen'"""


# In[5]:


meta = bb_utils.meta.BeeMetaInfo()


# In[6]:


all_groups_indices = np.arange(1,26)


# In[54]:


all_groups_dataframes = []

for i in all_groups_indices:
    group = meta.get_foragergroup(i)
    group_df = pd.DataFrame(group.dec12, columns=['bee_id_dec12'])
    group_df['group_id'] = group.group_id
    group_df['date'] = group.date
    group_df['location'] = group.location
    all_groups_dataframes.append(group_df)

all_groups_df = pd.concat(all_groups_dataframes)
all_groups_df


# In[55]:


all_groups_df.bee_id_dec12 = all_groups_df.bee_id_dec12.apply(lambda ID: bb_utils.ids.BeesbookID.from_dec_12(ID).as_ferwar())
all_groups_df.rename(columns={'bee_id_dec12' : 'bee_id'}, inplace=True)
all_groups_df.index = all_groups_df.bee_id
all_groups_df.drop(columns='bee_id')


# In[ ]:




