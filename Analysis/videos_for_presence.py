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
#%%

INTERVAL_SIZE = 30
FPS = 3

# Get all days that we have cached
#%%
presences = c.load_presence_caches(3)

#%%
bee_id = 10
pres_date = presences[2][0]
presx = presences[2][1].loc[bee_id]


presx[presx > 90] = 90
presbin = binarize_presence_row(presx)



exit_timestamps = get_timestamps_from_row(presbin, pres_date, mode='exits')
entry_timestamps = get_timestamps_from_row(presbin, pres_date, mode='entries')

#%%
ex_df = pd.Series(exit_timestamps)
frame_ids = [get_frame_id_for_bee_id_and_timestamp(bee_id, ts.astype(datetime.datetime)) for ts in exit_timestamps]


exits = pd.DataFrame(data={'timestamp':exit_timestamps, 'frame':frame_ids})
exits = exits.dropna() # NOTE: note the NaN somehow?
# %%







#%%
# GENERATE VIDEO
for i, row in tqdm(exits[8:11].iterrows()):
    bee = bee_id
    timestamp = row.timestamp
    frame = row.frame


    # ASK: can this be used given hiccups? or just take days w/o hiccups?
    interval_margin = 2
    frames_per_interval = INTERVAL_SIZE*FPS
    frame_margin = interval_margin*frames_per_interval #30s * 3FPS

    name = str(bee)+'_exitX3_' + str(i)
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
    start_interval = interval_index_mid - interval_margin


    for i, frame in enumerate(video._frames):
        interval_index = (i // frames_per_interval)
        #get pres_score and pres_bin values
        frame._title = "\n INTERVAL: " + str(interval_index) + "/" + str(interval_margin*2 - 1) + "\n PRES_SCORE: " + str(presx[start_interval + interval_index]) + "PRES: " + str(presbin[start_interval + interval_index])
    video._crop_margin = None
    video.get_video(save_to_path='/home/mi/rrszynka/mnt/janek/caches/Videos/' + name + ".mp4")






#%%

# plot_presence(presx)
# plot_presence(presbin)







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



def time_to_secs(time):
    return time.hour * 3600 + time.minute * 60 + time.second




#%%
def binarize_presence_row(presence_for_day_series):
    # TODO: running this on an already-binarized series will return all zeros,
    # (and that's not what we want) - changing the threshold solves it, but try sth else
    ys = presence_for_day_series.copy()
    if ys[ys>1].sum() == 0:
        #Consider this already binarized, make no changes
        return ys

    ys[ys>90] = 90
    ys[ys>45] = 90
    ys[ys<=45] = 0 #TODO: consult: what should the threshold be
    ys[ys==90] = 1

    ys = np.reshape(np.array(ys, dtype=np.int32),[1,ys.shape[0]])
    ys = closing(ys, rectangle(1,15))
    ys = ys.flatten()
    return ys
