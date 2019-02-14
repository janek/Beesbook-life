import pandas as pd
import seaborn as sns; sns.set()
import sys
sys.path.append(os.getcwd()+'/Beesbook-janek/Python-modules/') #For bee_helpers, file_helpers and cache
from bee_cache import Cache, CacheType, CacheFormat; c = Cache()




lives_from_detections_df = pd.read_csv(os.getcwd()+'/caches/Other/lives_from_detections_df.csv', index_col='bee_id', parse_dates=['min', 'max'])
foragers_from_groups = pd.read_pickle(os.getcwd()+'/caches/Other/foragers_from_groups.pkl').drop(columns=['bee_id'])

forager_lives = pd.merge(lives_from_detections_df, foragers_from_groups, how='inner', on='bee_id')


forager_lives.rename(columns={'min':'born', 'max':'died', 'date': 'foraging_min_date'}, inplace=True)
forager_lives_short = forager_lives[~forager_lives.index.duplicated()]


foraging_max_date = forager_lives[~forager_lives.index.duplicated(keep='last')].foraging_min_date.rename('foraging_max_date')
forager_lives_short = pd.merge(forager_lives_short, pd.DataFrame(foraging_max_date), how='inner', on='bee_id')
forager_lives_short = forager_lives_short.drop(columns=["group_id", "location"])

forager_lives_short['foraging_min_age'] = (forager_lives_short.foraging_min_date - forager_lives_short.born)
forager_lives_short['foraging_max_age'] = (forager_lives_short.foraging_max_date - forager_lives_short.born)

forager_lives_short.head(60)


# Gannt chart?
# aggregation/plotting? - what questions do I want to answer? ->
# 1. distribution of fmi

sns.distplot(forager_lives_short.foraging_min_age.dt.days, bins=10, kde=False)


c.save(forager_lives_short, 'forager_lives')

xx = c.load('foragers_from_groups')

# Presence charts for all 50 bees that were foraging, with foraging periods marked

xx
