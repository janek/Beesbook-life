import numpy as np
import pandas as pd


from datetime import timedelta, datetime
import time
import random

import bb_utils
import bb_utils.meta
import bb_utils.ids

from tqdm import tqdm

def calc_trip_lengths(presence_df, total_num_intervals):
    '''Takes a Presence dataframe and total number of intervals
    Returns and array of arrays containing lengths of individual trips of each consecutive bee'''
    trip_lengths = []

    for bee in tqdm(range(0, presence_df.shape[0])):
        curr_trip_length = 0
        curr_bee_trip_lenghts = []
        #fill with trip lengths
        for interval in range(total_num_intervals): #t: 2880
            #get the 0/1 value from presence_df at the given (bee, interval)
            bool_is_present = presence_df.iat[bee, interval]
            if bool_is_present == 0.0: #bee not present in this interval
                if curr_trip_length != 0: #if we had a value for a trip length -> means trip ends here -> add it to trips and reset the counter
                    curr_bee_trip_lenghts.append(curr_trip_length)
                    curr_trip_length = 0
            if bool_is_present == 1.0: #bee present in this interval, means trip is underway -> increment the length counter 
                curr_trip_length += 1
        trip_lengths.append(curr_bee_trip_lenghts)
    return trip_lengths



def get_forager_bee_ids():
    #Getting a known forager group from manual labeling experiments
    meta = bb_utils.meta.BeeMetaInfo()
    group_id = 20
    bee_ids_as_beesbookid_format = list(map(bb_utils.ids.BeesbookID.from_dec_12, meta.get_foragergroup(group_id).dec12))
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)

def get_random_bee_ids(amount):
    meta = bb_utils.meta.BeeMetaInfo()
    bees = set()
    while len(bees) < amount:
        bee_id_dec = random.randint(0, 4097)
        bee_id = bb_utils.ids.BeesbookID.from_dec_9(bee_id_dec)
        if meta.get_hatchdate(bee_id) != np.datetime64('NaT'): 
            bees.add(bee_id)
    bee_ids_as_beesbookid_format = list(bees)
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)


def get_all_bee_ids():
    meta = bb_utils.meta.BeeMetaInfo()
    bees = []
    for id in range(0,4096):
        bee_id = bb_utils.ids.BeesbookID.from_dec_9(id)
        if meta.get_hatchdate(bee_id) != np.datetime64('NaT'): 
            bees.append(bee_id)
    bee_ids_as_beesbookid_format = list(bees)
    bee_ids_as_ferwar_format = map(lambda i: i.as_ferwar(), bee_ids_as_beesbookid_format) #as ferwar
    return (list(bee_ids_as_ferwar_format), bee_ids_as_beesbookid_format)


#TODO: get bees that are alive on a certain day 
#TODO: get bees of a certain age for a given day