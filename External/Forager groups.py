import os
print(os.getcwd())


import bb_utils
import bb_backend
import numpy as np
import pandas as pd


connect_str = """dbname='beesbook'
                 user='reader'
                 host='tonic.imp.fu-berlin.de'
                 password=''
                 application_name='sammelgruppen'"""


meta = bb_utils.meta.BeeMetaInfo()


# This file collects known (ground truth) forager bee IDs, together with the date they were foraging on.
# The source for the data are forager groups (defined in the database).


all_groups_indices = np.arange(1,26)

all_groups_dataframes = []

for i in all_groups_indices:
    group = meta.get_foragergroup(i)
    group_df = pd.DataFrame(group.dec12, columns=['bee_id_dec12'])
    group_df['group_id'] = group.group_id
    group_df['date'] = group.date
    group_df['location'] = group.location
    all_groups_dataframes.append(group_df)

all_groups_df = pd.concat(all_groups_dataframes)

all_groups_df.bee_id_dec12 = all_groups_df.bee_id_dec12.apply(lambda ID: bb_utils.ids.BeesbookID.from_dec_12(ID).as_ferwar())
all_groups_df.rename(columns={'bee_id_dec12' : 'bee_id'}, inplace=True)
all_groups_df.index = all_groups_df.bee_id
all_groups_df.drop(columns='bee_id')
all_groups_df.to_pickle(os.getcwd()+'/caches/Other/foragers_from_groups.pkl')
