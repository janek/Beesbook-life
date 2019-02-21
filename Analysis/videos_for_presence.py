from bb_behavior import plot
from bb_behavior import db as bbdb
from bb_behavior import plot
import bb_behavior
import pandas as pd
import os
import sys
sys.path.append('/home/mi/rrszynka/mnt/janek/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()
import datetime
from bb_behavior import db as bbdb
import datetime

import numpy as np
from tqdm import tqdm
#%%

INTERVAL_SIZE = 30
FPS = 3

# Get all days that we have cached
#%%
presences = c.load_all_presence_caches()

#%%
bee_id = 10
pres_date = presences[2][0]
presx = presences[2][1].loc[bee_id]



presx[presx > 90] = 90
presbin = binarize_presence_row(presx)

plot_presence(presx)
plot_presence(presbin)

exit_timestamps = get_timestamps_from_row(presbin, pres_date, mode='exits')
entry_timestamps = get_timestamps_from_row(presbin, pres_date, mode='entries')

#%%
ex_df = pd.Series(exit_timestamps)
frame_ids = [get_frame_id_for_bee_id_and_timestamp(bee_id, ts.astype(datetime.datetime)) for ts in exit_timestamps]


d = {'timestamp':exit_timestamps, 'frame':frame_ids}
exits = pd.DataFrame(data=d)

exits = exits.dropna() # NOTE: note the NaN somehow?
# %%

presx


#%%



presx[1202.0]

time = exits.iloc[0].timestamp.time()

#%%
for i, row in exits[5:8].iterrows():
    bee = bee_id
    timestamp = row.timestamp
    frame = row.frame


    # ASK: can this be used given hiccups? or just take days w/o hiccups?
    interval_margin = 1
    frames_per_interval = INTERVAL_SIZE*FPS
    frame_margin = interval_margin*frames_per_interval #30s * 3FPS

    name = str(bee)+'_exitX2_' + str(i)
    video = plot.plot_bees(bee_ids=[bee],
                       frame_id=frame, frame_margin=frame_margin,
                       path_alpha=None, bt_export=None, # '/home/mi/rrszynka/mnt/janek/caches/Videos/bt_export/'+name+".json",
                       plot_labels = True, plot_markers=True)

    intervals = len(video._frames)/(interval_margin*2)

    #TODO: check this conversion from timestamp to interval against the conversion that goes the other way
    middle_timestamp = timestamp

    secs = time_to_secs(middle_timestamp)
    interval_index_mid = int(secs/30)
    print(timestamp, interval_index_mid)
    interval_index_start = interval_index_mid - interval_margin


    for i, frame in enumerate(video._frames):
        interval_index = (i // frames_per_interval)
        #get pres_score and pres_bin values
        frame._title = "\n INTERVAL: " + str(interval_index) + "/" + str(interval_margin*2 - 1) + "\n PRES_SCORE: " + str(presx[interval_index_start + i]) + "PRES: " + str(presbin[interval_index_start + i])
        print(interval_index, i, presx[interval_index_start+i])

    video._crop_margin = None
    video.get_video(save_to_path='/home/mi/rrszynka/mnt/janek/caches/Videos/' + name + ".mp4")


def time_to_secs(time):
    return time.hour * 3600 + time.minute * 60 + time.second

# %%
def get_presence_for_timestamp(timestamp):



#TODO: Ask David how this works
#TODO: move to video_helpers?
def get_frame_id_for_bee_id_and_timestamp(bee_id, dt):
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
    # For each bee, make a list of exits
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
