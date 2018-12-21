from datetime import timedelta, datetime
import sys
import os; os.getcwd()
sys.path.append(os.getcwd()+'/Beesbook/Python-modules/')
sys.path
from file_helpers import cache_detections_from_database, detections_to_presence
from bee_cache import CacheType, CacheFormat, Cache


# Goal: investigate why some bees have presence higher than 3FPS should allow



# 1. Download and save a detections file for a given hour of a given day (or all hours of a given day) ()
# -- file_helpers -> cache_detections_from_database()


# Detections to presence step
# -- file_helpers -> detections_to_presence



datetime_start = datetime(2016,8,9)
num_observ_periods = 1 # hours
num_intervals_per_hour = 120
observ_period = timedelta(hours=1)
detection_confidence_requirement = 0

cache_detections_from_database(datetime_start, observ_period, num_observ_periods, detection_confidence_requirement)
