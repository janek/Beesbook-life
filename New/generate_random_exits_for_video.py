from bb_behavior import plot
from bb_behavior import db as bbdb
import bb_behavior
import pandas as pd
import os
import sys
sys.path.append('/home/mi/rrszynka/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
import datetime
from bb_behavior import db as bbdb
from skimage.morphology import rectangle, closing
import datetime
import numpy as np
from tqdm import tqdm
import random
#%%

INTERVAL_SIZE = 30
FPS = 3
NUM_DAYS= 62


# Get all cached days (or consider excluding some)
presences = c.load_presence_caches(amount=NUM_DAYS)

presences_bin = []
for (date, presence) in tqdm(presences):
    presence_bin = binarize_presence(presence)
    presences_bin.append((date, presence_bin))
#%%

# BTW: this is concerning, ask David
for (date, presence) in tqdm(presences):
    print(str(date), presence.shape)


 # TODO: Give me 50 exits, from randomly chosen days, for randomly chosen bees and randomly chosen exits



random_exits = []
# %%
for _ in tqdm(range(55)):
    # Choose a random day and get presence
    day = np.random.randint(NUM_DAYS)
    pres_date, presence = presences[day]
    pres_date, pres_bin = presences_bin[day]


    while True:
        # Choose a random bee from the presence table
        row = presence.sample()
        bee_id = row.index.values[0]
        bee_pres_bin = pres_bin.loc[bee_id]

        row = presence.sample()
        bee_id = row.index.values[0]
        bee_pres_bin = pres_bin.loc[bee_id]
        # %%
        exit_timestamps = get_timestamps_from_row(bee_pres_bin, pres_date, mode='exits')
        if len(exit_timestamps) > 0:
            break

    ts = random.choice(exit_timestamps)

    #%%
    frame = get_frame_id_for_bee_id_and_timestamp(bee_id, ts)

    random_exits.append((bee_id, ts, frame))

random_exits = pd.DataFrame(random_exits).dropna()[:49]
random_exits.columns = ['bee_id', 'timestamp', 'frame']

ex_df = pd.Series(exit_timestamps)
frame_ids = [get_frame_id_for_bee_id_and_timestamp(bee_id, ts.astype(datetime.datetime)) for ts in exit_timestamps]


exits = pd.DataFrame(data={'timestamp':exit_timestamps, 'frame':frame_ids})
exits = exits.dropna() # NOTE: note the NaN somehow?
# %%



#TODO: Ask David how this works
#TODO: move to video_helpers?
def get_frame_id_for_bee_id_and_timestamp(bee_id, dt):
    bee_id = int(bee_id)
    if type(dt) == np.datetime64:
        dt = np.datetime64(dt).astype(datetime.datetime)
    for cam_id in range(4):
        frames = bbdb.get_frames(cam_id, dt.timestamp(), dt.timestamp() + 5)
        if len(frames) == 0:
            continue
        detections = bbdb.get_bee_detections(bee_id, frames=frames)
        for d in detections:
            if d is not None:
                return d[1]





# %%

def get_timestamps_from_row(row, date, mode='both'):
    '''
        Takes a binarized presence row (presence for a single bee from single day), date and mode
        returns a list of timestamps for exits/entries/both
    '''
    npdate = np.datetime64(date)
    diff = np.diff(row)

    if mode == 'both':
        timepoints = np.where(np.abs(diff) == 1)[0]
    elif mode == 'exits':
        timepoints = np.where(diff == -1)[0]
    elif mode == 'entries':
        timepoints = np.where(diff == 1)[0]

    timepoint_timestamps = [npdate + np.timedelta64(int(timepoint)*30, 's') for timepoint in timepoints]
    return timepoint_timestamps
